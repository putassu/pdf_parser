import requests
import json
import re
from typing import Optional, Dict
from utils import logger
from config import GEMMA_ENDPOINT, GEMMA_MODEL, LLM_TIMEOUT, API_TOKEN, LLM_ENDPOINT, LLM_MODEL

# def call_gemma_sync(prompt: str, image_b64: str) -> Optional[Dict]:
#     """Отправляет запрос к Vision модели и парсит JSON ответ."""
#     print("\n" + "="*60)
#     print(">>> ОТПРАВЛЯЕМЫЙ ПРОМПТ:")
#     print(prompt)
#     print("="*60 + "\n")
#     headers = {}
#     if API_TOKEN:
#         headers["Authorization"] = f"Bearer {API_TOKEN}"

#     payload = {
#         "model": GEMMA_MODEL,
#         "prompt": prompt,
#         "images": [image_b64],
#         "stream": False,
#         "format": "json",
#         "options": {
#             "temperature": 0.0,
#             "num_ctx": 32000
#         }
#     }

#     try:
#         response = requests.post(
#             GEMMA_ENDPOINT, 
#             json=payload, 
#             headers=headers,
#             timeout=LLM_TIMEOUT
#         )
#         response.raise_for_status()
        
#         text_response = response.json().get("response", "")

#         # Поиск JSON блока в ответе (на случай если модель добавила текст)
#         match = re.search(r'(\{.*\}|$$.*$$)', text_response, re.DOTALL)
#         if match:
#             return json.loads(match.group(1))
        
#         logger.error("Валидный JSON не найден в ответе модели")
#         return None

#     except Exception as e:
#         logger.error(f"Ошибка при обращении к LLM: {e}")
#         return None

def call_gemma_sync(prompt: str, image_b64: str) -> Optional[Dict]:
    """
    Вызов Qwen2.5-VL через llama-server (OpenAI-совместимый API).
    """
    print("\n" + "="*60)
    print("--- ОТПРАВЛЯЕМЫЙ ПРОМПТ ---")
    print(prompt)
    print("="*60 + "\n")

    # Формируем структуру сообщений для Vision-модели в llama.cpp
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.0,
        "stream": False,
        # Важно: llama.cpp может игнорировать "format": "json" в чат-режиме, 
        # поэтому мы полагаемся на наш Regex в парсинге.
    }

    try:
        response = requests.post(
            LLM_ENDPOINT, 
            json=payload, 
            timeout=LLM_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # В OpenAI формате ответ лежит в choices[0].message.content
        res_data = response.json()
        full_text = res_data['choices'][0]['message']['content']
        
        # Логируем ответ для отладки
        logger.debug(f"Raw LLM Response: {full_text}")

        # Извлечение JSON из текста (Qwen часто оборачивает в ```json ... ```)
        match = re.search(r'(\{.*\}|\[.*\])', full_text, re.DOTALL)
        if match:
            clean_json = match.group(1)
            return json.loads(clean_json)
        
        logger.error("JSON не найден в ответе Qwen")
        return None

    except Exception as e:
        logger.error(f"Ошибка при вызове llama-server: {e}")
        if 'response' in locals():
            logger.error(f"Ответ сервера: {response.text}")
        return None
