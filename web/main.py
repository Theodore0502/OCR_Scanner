from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import shutil
import os

from src.ocr.engine_doctr import doctr_ocr_image
from src.ocr.vietnamese_autocorrect import autocorrect_text

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ocr", response_class=HTMLResponse)
async def ocr_image(request: Request, file: UploadFile):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = doctr_ocr_image(filepath)
    blocks = result.export()["pages"][0]["blocks"]

    raw = "\n".join(" ".join(w["value"] for w in line["words"])
                    for b in blocks for line in b["lines"])

    fixed = autocorrect_text(raw)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "raw": raw,
        "fixed": fixed
    })
