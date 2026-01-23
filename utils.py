import time
import logging
import sys
from contextlib import contextmanager

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("parsing.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("PDF_Parser")

@contextmanager
def timer(name: str):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    logger.info(f"⏱️ Stage [{name}] took {end - start:.3f} seconds")

def get_base64_size_kb(b64_str: str) -> float:
    return (len(b64_str) * 3 / 4) / 1024
