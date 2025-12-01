import os
from pdf2image import convert_from_path
import cv2
import numpy as np

def load_images_from_doc(doc_id):
    base = f"data/raw/{doc_id}"
    pages = []
    for fname in sorted(os.listdir(base)):
        path = os.path.join(base, fname).lower()
        if path.endswith('.pdf'):
            imgs = convert_from_path(path, dpi=200)
            for pil in imgs:
                pages.append(cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR))
        elif path.endswith(('.jpg', '.png', '.jpeg', '.tiff')):
            img = cv2.imread(path)
            pages.append(img)
    return pages
