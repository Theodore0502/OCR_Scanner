from src.ocr.doc_folder_doctr import ocr_document_doctr
import sys

def main():
    doc_id = sys.argv[1]
    print(f"\nOCR DocTR test: data/raw/{doc_id}/{doc_id}\n")

    text = ocr_document_doctr(doc_id)

    print("----- OCR RESULT -----\n")
    print(text)


if __name__ == "__main__":
    main()
