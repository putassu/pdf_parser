import openpyxl
from openpyxl.utils import get_column_letter
import asyncio
import logging

logger = logging.getLogger("SeniorAnalyzer")

class AsyncExcelAnalyzer:
    def __init__(self):
        self.H_TOLERANCE = 15 # Увеличил, чтобы видеть ОЧЕНЬ далекие значения
        self.V_TOLERANCE = 2
        self.MAX_CELLS_GLOBAL = 600

    def _is_significant(self, cell, merged_ranges):
        # 1. Значение (основной признак)
        if cell.value is not None and str(cell.value).strip() != "":
            return True
        # 2. Границы (безопасная проверка)
        b = cell.border
        if b:
            for side in [b.left, b.right, b.top, b.bottom]:
                if side and side.style is not None:
                    return True
        # 3. Объединение ячеек
        coord = f"{get_column_letter(cell.column)}{cell.row}"
        for r in merged_ranges:
            if coord in r: return True
        return False

    async def analyze_file(self, file_path: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._analyze_file_sync, file_path)

    def _analyze_file_sync(self, file_path: str):
        wb = openpyxl.load_workbook(file_path, data_only=True)
        manifest = []
        for sheet in wb.worksheets:
            merged = sheet.merged_cells.ranges
            sig_cells = [c for row in sheet.iter_rows() for c in row if self._is_significant(c, merged)]
            
            if not sig_cells: continue

            # Группируем ячейки по строкам для компактного превью
            rows_data = {}
            for c in sig_cells:
                if c.row not in rows_data: rows_data[c.row] = []
                val = str(c.value).strip() if c.value is not None else ""
                rows_data[c.row].append(f"[{get_column_letter(c.column)}{c.row}]: {val}")

            clean_preview = []
            for r in sorted(rows_data.keys()):
                # Соединяем только значимые ячейки в строке
                clean_preview.append(" | ".join(rows_data[r]))

            # Логика островов
            islands = self._cluster(sig_cells)
            
            manifest.append({
                "sheet": sheet.title,
                "strategy": "GLOBAL" if len(sig_cells) < self.MAX_CELLS_GLOBAL else "REGIONAL",
                "full_preview": clean_preview,
                "islands": islands
            })
        return manifest

    def _cluster(self, cells):
        islands = []
        visited = set()
        cmap = {(c.row, c.column): c for c in cells}
        coords = list(cmap.keys())
        for coord in coords:
            if coord in visited: continue
            island = []
            q = [coord]
            visited.add(coord)
            while q:
                r, c = q.pop(0)
                island.append(cmap[(r, c)])
                for dr in range(-self.V_TOLERANCE, self.V_TOLERANCE+1):
                    for dc in range(-self.H_TOLERANCE, self.H_TOLERANCE+1):
                        nb = (r+dr, c+dc)
                        if nb in cmap and nb not in visited:
                            visited.add(nb); q.append(nb)
            
            min_r, max_r = min(c.row for c in island), max(c.row for c in island)
            min_c, max_c = min(c.column for c in island), max(c.column for c in island)
            
            # Компактное превью для острова
            i_rows = {}
            for c in island:
                if c.row not in i_rows: i_rows[c.row] = []
                i_rows[c.row].append(f"[{get_column_letter(c.column)}{c.row}]: {str(c.value or '')}")
            
            p = [" | ".join(i_rows[r]) for r in sorted(i_rows.keys())[:15]]
            islands.append({
                "range": f"{get_column_letter(min_c)}{min_r}:{get_column_letter(max_c)}{max_r}",
                "preview": p
            })
        return islands
