import re

def extract_header(text):
    quoc_hieu = re.search(r"CỘNG HÒA.*?VIỆT NAM", text, re.I)
    co_quan = re.search(r"(BỘ|UBND|SỞ|TRƯỜNG).*", text, re.I)
    return {
        "quoc_hieu": quoc_hieu.group(0) if quoc_hieu else None,
        "co_quan": co_quan.group(0) if co_quan else None,
    }

def extract_so_van_ban(text):
    m = re.search(r"Số[: ]+\s*([0-9A-Za-z\/\.-]+)", text)
    return m.group(1) if m else None

def extract_ngay_thang(text):
    m = re.search(r"ngày\s+\d{1,2}\/\d{1,2}\/\d{2,4}", text, re.I)
    return m.group(0) if m else None

def parse_document(text):
    return {
        "header": extract_header(text),
        "so_van_ban": extract_so_van_ban(text),
        "ngay": extract_ngay_thang(text),
    }
