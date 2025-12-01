import os
from src.ocr.engine_doctr import doctr_ocr_image
from src.ocr.vietnamese_autocorrect import autocorrect_text
from src.ocr.doc_parser import parse_document

def ocr_document_doctr(doc_id):
    img_path = f"data/raw/{doc_id}/{doc_id}.jpg"
    result = doctr_ocr_image(img_path)

    # extract plain text
    blocks = result.export()["pages"][0]["blocks"]
    raw_text = "\n".join(
        [" ".join([w["value"] for w in line["words"]]) 
         for b in blocks for line in b["lines"]]
    )

    # clean + autocorrect
    cleaned = autocorrect_text(raw_text)

    # parse structured data
    parsed = parse_document(cleaned)

    print("\n----- RAW OCR -----\n")
    print(raw_text)

    print("\n----- AFTER FIX -----\n")
    print(cleaned)

    print("\n----- STRUCTURED DATA -----\n")
    print(parsed)

if __name__ == "__main__":
    import sys
    ocr_document_doctr(sys.argv[1])
