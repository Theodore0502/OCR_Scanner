import argparse
from src.ocr.doc_folder_doctr import ocr_document_doctr

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("doc_id")
    args = parser.parse_args()

    text = ocr_document_doctr(args.doc_id)
    print("\n----- OCR RESULT -----\n")
    print(text)

if __name__ == "__main__":
    main()
