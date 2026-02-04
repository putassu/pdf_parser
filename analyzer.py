import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.cell.cell import Cell, MergedCell
import logging
import time

# ================= ГЛОБАЛЬНЫЕ НАСТРОЙКИ ПАРСЕРА =================
H_TOLERANCE = 1          # Разрыв между колонками, чтобы считать их одним блоком
V_TOLERANCE = 1          # Разрыв между строками, чтобы считать их одним блоком
MAX_CHARS_BLOCK = 3000   # Лимит символов для анкеты (data_form), выше -> data_table
MIN_TABLE_ROWS = 10      # Минимальное кол-во строк для потенциальной таблицы
SHOW_MERGED_MAP = True   # Показывать ли диапазоны [A1:C1] в выводе
VALIDATION_THRESHOLD = 0.95 # Допустимый % покрытия (0.95 = 95%)
# ================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ExcelParser")

class RobustExcelParser:
    def __init__(self):
        pass

    def parse_file(self, file_path: str):
        start_time = time.time()
        logger.info(f"Processing file: {file_path}")
        try:
            # data_only=True для значений, read_only=False для стилей (границ)
            wb = openpyxl.load_workbook(file_path, data_only=True)
        except Exception as e:
            logger.error(f"Failed to open file: {e}")
            return []

        results = []
        for sheet in wb.worksheets:
            # Пропускаем совсем пустые листы
            if sheet.calculate_dimension() == 'A1:A1' and not sheet['A1'].value:
                continue
                
            sheet_data = self._process_sheet(sheet)
            if sheet_data:
                results.extend(sheet_data)
        
        logger.info(f"Finished in {time.time() - start_time:.2f} seconds")
        return results

    def _process_sheet(self, sheet):
        # 1. Предварительный сбор всех значимых данных в кэш
        # Это КРИТИЧЕСКИ ускоряет работу, т.к. мы не дергаем sheet.cell()
        sig_data = {} # (r, c) -> value
        total_sig_count = 0
        
        # Кэшируем объединенные ячейки
        merged_lookup = {}
        for rng in sheet.merged_cells.ranges:
            for r in range(rng.min_row, rng.max_row + 1):
                for c in range(rng.min_col, rng.max_col + 1):
                    merged_lookup[(r, c)] = rng

        # Сканируем лист один раз
        for row in sheet.iter_rows():
            for cell in row:
                if self._is_significant(cell, (cell.row, cell.column) in merged_lookup):
                    sig_data[(cell.row, cell.column)] = cell.value
                    total_sig_count += 1

        if not sig_data:
            return []

        # 2. Кластеризация
        clusters = self._cluster_regions(list(sig_data.keys()))

        # 3. Анализ и валидация
        sheet_output = []
        cells_covered = 0
        
        for cluster in clusters:
            cells_covered += len(cluster)
            region_info = self._analyze_region(sheet, cluster, sig_data, merged_lookup)
            region_info['sheet'] = sheet.title
            sheet_output.append(region_info)

        # Валидация покрытия
        self.coverage = cells_covered / total_sig_count if total_sig_count > 0 else 1.0
        if self.coverage < VALIDATION_THRESHOLD:
            logger.warning(f"Sheet '{sheet.title}': Coverage only {coverage:.2%}. Some cells were orphaned.")
            # Здесь можно реализовать смену стратегии (например, увеличить толерантность)
        
        return sheet_output

    def _is_significant(self, cell, in_merged):
        """Проверка ячейки на значимость."""
        if cell.value is not None and str(cell.value).strip() != "":
            return True
        if in_merged: # Любая ячейка в объединении считается значимой для структуры
            return True
        if cell.border and any([cell.border.left.style, cell.border.right.style, 
                                cell.border.top.style, cell.border.bottom.style]):
            return True
        if cell.fill and cell.fill.patternType and cell.fill.patternType != 'none':
            return True
        return False

    def _cluster_regions(self, coords):
        coords_set = set(coords)
        clusters = []
        visited = set()
        
        # Сортировка ускоряет BFS за счет локальности данных
        sorted_coords = sorted(coords)

        for start_node in sorted_coords:
            if start_node in visited:
                continue

            cluster = []
            queue = [start_node]
            visited.add(start_node)
            
            while queue:
                r, c = queue.pop(0)
                cluster.append((r, c))

                # Поиск соседей в окне толерантности
                for nr in range(r - V_TOLERANCE, r + V_TOLERANCE + 1):
                    for nc in range(c - H_TOLERANCE, c + H_TOLERANCE + 1):
                        neighbor = (nr, nc)
                        if neighbor in coords_set and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
            clusters.append(cluster)
        return clusters

    def _analyze_region(self, sheet, cluster_coords, sig_data_cache, merged_lookup):
        rows = [c[0] for c in cluster_coords]
        cols = [c[1] for c in cluster_coords]
        min_r, max_r, min_c, max_c = min(rows), max(rows), min(cols), max(cols)
        
        # Сбор строк
        lines = []
        for r in range(min_r, max_r + 1):
            row_cells = []
            processed_in_row = set()
            
            for c in range(min_c, max_c + 1):
                if c in processed_in_row: continue
                
                coord = (r, c)
                val = sig_data_cache.get(coord)
                
                # Обработка Merged Cells
                if coord in merged_lookup:
                    m_rng = merged_lookup[coord]
                    # Берем значение только из верхней левой ячейки
                    if r == m_rng.min_row and c == m_rng.min_col:
                        addr = str(m_rng) if SHOW_MERGED_MAP else get_column_letter(c)+str(r)
                        display_val = str(val).strip() if val is not None else ""
                        row_cells.append(f"[{addr}]: {display_val}")
                    
                    # Помечаем все колонки этого объединения в текущей строке как обработанные
                    for mc in range(m_rng.min_col, m_rng.max_col + 1):
                        processed_in_row.add(mc)
                else:
                    if val is not None and str(val).strip() != "":
                        row_cells.append(f"[{get_column_letter(c)}{r}]: {str(val).strip()}")
            
            if row_cells:
                lines.append(" | ".join(row_cells))

        # Формирование превью
        total_lines = len(lines)
        full_text = "\n".join(lines)
        
        if len(full_text) > MAX_CHARS_BLOCK and total_lines > MIN_TABLE_ROWS:
            # Режим TABLE
            head = lines[:5]
            tail = lines[-5:]
            skipped_count = total_lines - 10
            preview = "\n".join(head) + f"\n... [DATA SKIPPED: {skipped_count} ROWS] ...\n" + "\n".join(tail)
            r_type = "data_table"
        else:
            # Режим FORM
            preview = full_text
            r_type = "data_form"

        return {
            "type": r_type,
            "range": f"{get_column_letter(min_c)}{min_r}:{get_column_letter(max_c)}{max_r}",
            "preview": preview,
            "coverage_cells": len(cluster_coords)
        }

# --- TEST ---
if __name__ == "__main__":
    parser = RobustExcelParser()
    # Укажи путь к своему файлу
    results = parser.parse_file("C:\\Users\\sigur\\docling\\xlsx_parser\\Анкета_соискателя_на_вакантную_должность_1_1 (3) — копия (2).xlsx")
    
    for r in results:
        print(f"--- Region ({r['type']}) {r['range']} (Sheet: {r['sheet']}) ---")
        print(r['preview'])
        print("-" * 50 + "\n")
        print(parser.coverage)
