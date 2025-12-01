import os
from .engine_doctr import ocr_doctr_image

def ocr_document_doctr(doc_id: str):
    folder = f"data/raw/{doc_id}"
    image_path = os.path.join(folder, f"{doc_id}.jpg")

    print(f"OCR DocTR: {image_path}")
    return ocr_doctr_image(image_path)