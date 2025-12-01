from src.ocr.engine_paddle import ocr_paddle_image
from src.ocr.pdf_utils import load_images_from_doc

def ocr_document_paddle(doc_id, mode="raw"):
    pages = load_images_from_doc(doc_id)
    results = []
    for idx, img in enumerate(pages, 1):
        text = ocr_paddle_image(img)
        results.append({"page_index": idx, "text": text})
    return results
