import easyocr
import numpy as np
from PIL import Image
import io
import base64
from utils import logger, timer

class OCRManager:
    def __init__(self):
        with timer("EasyOCR Initialization"):
            self.reader = easyocr.Reader(['ru', 'en'], gpu=False)

    def get_preocr_data(self, b64_image: str) -> str:
        with timer("EasyOCR Inference"):
            img_data = base64.b64decode(b64_image)
            results = self.reader.readtext(np.array(Image.open(io.BytesIO(img_data))))
            
            # Сортировка: сначала по Y (строки), потом по X (колонки)
            # Добавляем допуск в 10 пикселей, чтобы слова в одной строке не прыгали
            results.sort(key=lambda x: (x[0][0][1] // 10, x[0][0][0]))
            
            lines = []
            current_y = -1
            current_line = []
            
            for (bbox, text, prob) in results:
                if prob < 0.2: continue
                y_top = bbox[0][1]
                if current_y == -1 or abs(y_top - current_y) <= 15:
                    current_line.append(text)
                else:
                    lines.append(" | ".join(current_line))
                    current_line = [text]
                current_y = y_top
            
            lines.append(" | ".join(current_line))
            return "\n".join(lines)

