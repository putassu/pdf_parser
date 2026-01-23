import os

# Настройки LLM
# GEMMA_ENDPOINT = os.getenv("GEMMA_ENDPOINT", "http://localhost:11434/api/generate")
# GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma3:4b")
GEMMA_ENDPOINT = os.getenv("GEMMA_ENDPOINT", "http://10.0.245.10:8003/v1/chat/completions")
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-3-27b") # Имя в llama-server может быть любым
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://10.0.245.10:8003/v1/chat/completions")
LLM_MODEL = "gpt-4o" # В llama.cpp имя модели в запросе может быть любым, если загружена одна
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 300))
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 300))
# Токен (если используется прокси или облачный API)
API_TOKEN = os.getenv("LLM_API_TOKEN", "")

# Настройки обработки изображений
TARGET_IMAGE_KB = int(os.getenv("TARGET_IMAGE_KB", 80))
MAX_IMAGE_WIDTH = int(os.getenv("MAX_IMAGE_WIDTH", 1024))
PDF_RENDER_DPI = float(os.getenv("PDF_RENDER_DPI", 2.0))

# Настройки OCR
OCR_GPU = os.getenv("OCR_GPU", "False").lower() == "true"


LOG_FILE = "parsing.log"
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
DEBUG_DIR = "debug_snapshots" # Папка для снапшотов страниц