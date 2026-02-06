import asyncio, aiohttp, logging, json, os, config
from analyzer import RobustExcelParser
from prompts import get_tuning_prompt
from llm_client import call_gemma_async

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Dispatcher")

class ExcelProcessingDispatcher:
    def __init__(self):
        self.parser = RobustExcelParser(global_config=config.DEFAULT_SETTINGS)

    async def process_file_workflow(self, file_path: str):
        history = [] # Храним результаты всех итераций
        
        async with aiohttp.ClientSession() as session:
            for attempt in range(1, config.XLSX_PARSER_NUM_RETRIES + 1):
                logger.info(f"🔄 ИТЕРАЦИЯ {attempt}: Парсинг...")
                
                # 1. Парсим
                current_results = await self.parser.parse_file(file_path, session=session)
                
                # Сохраняем самый первый прогон как initial
                if attempt == 1:
                    self._save_json(current_results, "initial_results.json")

                # 2. Просим LLM оценить качество
                payload = self._prepare_smart_payload(current_results)
                prompt = get_tuning_prompt(payload, attempt)
                
                decision = await call_gemma_async(prompt, session)
                if not decision: 
                    decision = {"quality_score": 0.0, "action": "stop"}

                score = decision.get("quality_score", 0.0)
                logger.info(f"📊 Оценка LLM: {score} | Действие: {decision.get('action')}")

                # Сохраняем результат и его оценку в историю
                history.append({
                    "score": score,
                    "results": current_results,
                    "decision": decision
                })

                # 3. Условие выхода
                if decision.get("action") == "stop" or score >= 0.95:
                    logger.info("🎯 Достигнуто целевое качество или команда STOP.")
                    break
                
                if attempt < config.XLSX_PARSER_NUM_RETRIES:
                    # Корректируем конфиг для следующей попытки
                    self._apply_recommendations(decision)
                else:
                    logger.warning("⚠️ Исчерпано количество попыток тюнинга.")

            # 4. ВЫБИРАЕМ ЛУЧШИЙ ВАРИАНТ ИЗ ИСТОРИИ
            best_attempt = max(history, key=lambda x: x["score"])
            final_data = best_attempt["results"]
            
            # Добавляем финальную аналитику в JSON
            for s_name, s_res in final_data.items():
                if s_name in best_attempt["decision"].get("sheets", {}):
                    s_res["ai_analysis"] = best_attempt["decision"]["sheets"][s_name].get("summaries")
                    s_res["ai_score"] = best_attempt["score"]

            self._save_json(final_data, "final_results.json")
            logger.info(f"🏆 Финальный выбор: Попытка со скором {best_attempt['score']}")
            return final_data

    def _apply_recommendations(self, decision):
        """Применяет пресеты, рекомендованные LLM для следующего круга."""
        for s_name, sheet_data in decision.get("sheets", {}).items():
            preset_name = sheet_data.get("recommended_preset")
            if preset_name in config.PRESETS:
                logger.info(f"⚙️ Подготовка: Лист '{s_name}' -> пресет {preset_name}")
                new_cfg = {**config.DEFAULT_SETTINGS, **config.PRESETS[preset_name]}
                self.parser.set_sheet_config(s_name, new_cfg)

    def _prepare_smart_payload(self, results):
        """Формирует срез данных для LLM."""
        payload = {}
        for s_name, s_data in results.items():
            if not isinstance(s_data, dict): continue
            regions = []
            for r in s_data.get("regions", []):
                regions.append({
                    "range": r["range"],
                    "type": r["type"],
                    "preview": self._get_smart_preview(r.get("preview", ""))
                })
            payload[s_name] = {"coverage": s_data.get("coverage"), "blocks": regions}
        return payload

    def _get_smart_preview(self, text):
        if not text: return ""
        lines = [l for l in text.split('\n') if l.strip()]
        if len(lines) <= 10: return text
        return "\n".join(lines[:5]) + "\n... [SKIP] ...\n" + "\n".join(lines[-5:])

    def _save_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

async def main():
    path = r"C:\\Users\\sigur\\docling\\xlsx_parser\\price_10.2023.xlsx"
    await ExcelProcessingDispatcher().process_file_workflow(path)

if __name__ == "__main__":
    asyncio.run(main())
