import fitz
import json
import os
import sys
from config import PDF_RENDER_DPI, OUTPUT_DIR, DEBUG_DIR
from image_utils import process_and_compress_image, save_snapshot, prepare_output_folders
from ocr_engine import OCRManager
from prompts import get_layout_prompt
from llm_client import call_gemma_sync
from utils import logger, timer

def process_single_page(page, page_num, ocr_manager, debug_folder):
    """Полный цикл обработки одной страницы."""
    logger.info(f"Начало обработки страницы {page_num + 1}")
    
    # 1. Текстовый слой PDF
    text_layer = page.get_text("text").strip()

    # 2. Рендеринг страницы
    pix = page.get_pixmap(matrix=fitz.Matrix(PDF_RENDER_DPI, PDF_RENDER_DPI))
    img_bytes = pix.tobytes("jpeg")

    # 3. Сжатие и сохранение снапшота
    b64_img = process_and_compress_image(img_bytes)
    save_snapshot(b64_img, page_num, debug_folder)

    # 4. Получение OCR подсказок
    with timer("EasyOCR"):
        pre_ocr_hints = ocr_manager.get_preocr_data(b64_img)

    # 5. Промпт
    prompt = get_layout_prompt(pre_ocr_hints, text_layer)

    # 6. Запрос к LLM
    result = call_gemma_sync(prompt, b64_img)
    return result

def run_pipeline(pdf_path):
    # Подготовка имен файлов и папок
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    debug_folder = os.path.join(DEBUG_DIR, base_name)
    output_json_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")

    # Пересоздаем папку для картинок и проверяем папку для JSON
    prepare_output_folders(debug_folder, OUTPUT_DIR)

    ocr_manager = OCRManager()
    final_data = []

    try:
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                page_result = process_single_page(page, i, ocr_manager, debug_folder)
                if page_result:
                    final_data.append({
                        "page": i + 1,
                        "extraction": page_result
                    })
                    logger.info(f"✅ Страница {i+1} успешно обработана")
                else:
                    logger.warning(f"⚠️ Страница {i+1} не дала результата")

        # Сохранение итогового JSON
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Результаты сохранены в: {output_json_path}")
        logger.info(f"🖼️ Снапшоты страниц находятся в: {debug_folder}")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка пайплайна: {e}")

if __name__ == "__main__":
    # Аргумент командной строки или файл по умолчанию
    input_file = sys.argv[1] if len(sys.argv) > 1 else "PFR_777000_0SZIE_20251202_70f51a49-cfa5-11f0-afff-3a453110dbec (1).pdf"
    # "!Ознакомиться перед использованием.pdf"
    
    with timer("Полный цикл обработки"):
        run_pipeline(input_file)
