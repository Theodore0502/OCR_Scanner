from doctr.io import DocumentFile
from doctr.models import ocr_predictor

model = ocr_predictor(
    det_arch="db_resnet50",
    reco_arch="vitstr_small",
    pretrained=True
)

def ocr_doctr_image(path: str) -> str:
    doc = DocumentFile.from_images([path])
    result = model(doc).export()

    text = ""
    for page in result["pages"]:
        for block in page["blocks"]:
            for line in block.get("lines", []):
                line_text = " ".join([w["value"] for w in line.get("words", [])])
                text += line_text + "\n"

    return text
