import os
from .engine_doctr import ocr_doctr_image, ocr_doctr_pdf


def ocr_document_doctr(doc_id: str):
    base = f"data/raw/{doc_id}"

    # tìm file trong thư mục
    for filename in os.listdir(base):
        path = os.path.join(base, filename)

        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return ocr_doctr_image(path)

        if filename.lower().endswith(".pdf"):
            return ocr_doctr_pdf(path)

        if filename.lower().endswith(".tiff"):
            return ocr_doctr_image(path)

    raise FileNotFoundError(f"Không tìm thấy file phù hợp trong {base}")
