import cv2
import torch
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# ---- Optimize CPU ----
torch.set_num_threads(8)
torch.set_num_interop_threads(8)

# ---- Load strongest OCR model ----
model = ocr_predictor(
    det_arch="db_resnet50",
    reco_arch="vitstr_small",
    pretrained=True
)

def preprocess_image(path):
    """Resize ảnh về kích thước tối ưu cho DocTR"""
    img = cv2.imread(path)
    h, w = img.shape[:2]
    scale = 1800 / max(h, w)
    img = cv2.resize(img, (int(w * scale), int(h * scale)))
    temp = path.replace(".jpg", "_resized.jpg")
    cv2.imwrite(temp, img)
    return temp

def doctr_ocr_image(path):
    """OCR 1 ảnh"""
    pre = preprocess_image(path)
    doc = DocumentFile.from_images([pre])
    result = model(doc)
    text = result.export()["pages"][0]["blocks"]
    return result
