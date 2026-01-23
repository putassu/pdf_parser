import io
import os
import base64
import shutil
from PIL import Image, ImageOps
from utils import logger, timer, get_base64_size_kb
from config import TARGET_IMAGE_KB, MAX_IMAGE_WIDTH

def process_and_compress_image(image_bytes: bytes) -> str:
    """Сжатие изображения для входа Vision LLM."""
    with timer("Сжатие"):
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        w, h = img.size
        if w > MAX_IMAGE_WIDTH:
            new_h = int(h * (MAX_IMAGE_WIDTH / w))
            img = img.resize((MAX_IMAGE_WIDTH, new_h), Image.Resampling.LANCZOS)

        quality = 85
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality)
        
        while output.tell() > TARGET_IMAGE_KB * 1024 and quality > 15:
            quality -= 7
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=quality)
        
        return base64.b64encode(output.getvalue()).decode("utf-8")

def prepare_output_folders(debug_folder: str, output_dir: str):
    """Пересоздает папку снапшотов и проверяет папку результатов."""
    if os.path.exists(debug_folder):
        shutil.rmtree(debug_folder)
    os.makedirs(debug_folder, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

def save_snapshot(b64_str: str, page_num: int, folder: str):
    """Сохранение обработанного изображения страницы."""
    img_data = base64.b64decode(b64_str)
    path = os.path.join(folder, f"page_{page_num + 1}.jpg")
    with open(path, "wb") as f:
        f.write(img_data)
