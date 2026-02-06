import aiohttp
import json
import logging
import re
from typing import Optional, Dict, Any
from config import LLM_ENDPOINT, LLM_TOKEN, LLM_MODEL
import asyncio
# Настройка логгера
parse_logger = logging.getLogger("LLM_Validator")
DEBUG_MODE = True # Можно вынести в config

def parse_llm_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Извлекает JSON из текстового ответа LLM, очищая от Markdown-разметки.
    """
    try:
        # 1. Пытаемся найти блок кода ```json ... ```
        json_block_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_block_match:
            return json.loads(json_block_match.group(1))
        
        # 2. Если блока нет, ищем просто что-то похожее на JSON объект
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
            
        # 3. Пробуем распарсить текст целиком
        return json.loads(text)
    except (json.JSONDecodeError, AttributeError) as e:
        parse_logger.error(f"Ошибка парсинга JSON: {e}")
        return None


# async def call_gemma_async(prompt: str, image_b64: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
#     from config import LLM_ENDPOINT, LLM_MODEL
#     print(prompt)
#     # Мы добавляем system prompt, чтобы модель лучше понимала роль
#     payload = {
#         "model": LLM_MODEL,
#         "messages": [
#             {
#                 "role": "system", 
#                 "content": "Ты — профессиональный аналитик Excel. Ты всегда отвечаешь только валидным JSON на русском языке."
#             },
#             {
#                 "role": "user", 
#                 "content": prompt
#             }
#         ],
#         "stream": False,
#         "format": "json",
#         "options": {
#             "temperature": 0.0, # Максимальная точность
#             "num_ctx": 16000
#         }
#     }

#     url = f"{LLM_ENDPOINT}/api/chat"

#     try:
#         async with session.post(url, json=payload, timeout=120) as response:
#             if response.status != 200:
#                 return None

#             res_data = await response.json()
#             print(res_data)
#             content = res_data.get("message", {}).get("content", "").strip()
            
#             if not content or content == "{}":
#                 parse_logger.warning("Ollama вернула пустой объект. Проверь промпт.")
#                 return None
                
#             return json.loads(content)
#     except Exception as e:
#         parse_logger.error(f"Ошибка вызова LLM: {e}")
#         return None


def _manual_json_clean(text: str) -> Optional[Dict[str, Any]]:
    """Резервный очиститель, если модель добавила текст вокруг JSON."""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return json.loads(text[start:end])
    except:
        return None
    return None

import aiohttp
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("LLM_Client")

async def call_gemma_async(prompt: str, session: aiohttp.ClientSession, image_b64: str = "") -> Optional[Dict[str, Any]]:
    from config import LLM_ENDPOINT, LLM_MODEL
    
    # Печатаем промпт для отладки
    print("\n" + "="*50 + "\nPROMPT TO LLM:\n" + prompt + "\n" + "="*50)

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Ты — аналитик Excel. Отвечай ТОЛЬКО валидным JSON."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0, "num_ctx": 16000}
    }

    try:
        async with session.post(f"{LLM_ENDPOINT}/api/chat", json=payload, timeout=120) as response:
            if response.status != 200:
                logger.error(f"Ollama error: {response.status}")
                return None
            
            res_data = await response.json()
            content = res_data.get("message", {}).get("content", "").strip()
            return json.loads(content)
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return None

async def process_image(session: aiohttp.ClientSession, file_path: str, filename: str) -> str:
    """Моковая функция VLM для тестов"""
    await asyncio.sleep(0.5)
    return f"VLM_ANALYSIS: На изображении {filename} обнаружена подпись или печать."
