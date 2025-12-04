import os
import json
from unidecode import unidecode

# ---- Load Vietnamese dictionary safely ----

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Try to load from config
VI_DICT_PATH = os.path.join(PROJECT_ROOT, "data/processed/vietnamese_words.txt")

try:
    config_path = os.path.join(PROJECT_ROOT, "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf8') as f:
            config = json.load(f)
            dict_path_from_config = config.get('paths', {}).get('vietnamese_dictionary', '')
            if dict_path_from_config:
                VI_DICT_PATH = os.path.join(PROJECT_ROOT, dict_path_from_config)
except Exception as e:
    print(f"[WARN] Could not load config.json: {e}. Using default path.")


VI_WORDS = set()

if os.path.exists(VI_DICT_PATH):
    with open(VI_DICT_PATH, "r", encoding="utf8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                word = obj["text"].strip().lower()
                VI_WORDS.add(word)
            except Exception:
                continue
else:
    print(f"[WARN] Không tìm thấy dictionary: {VI_DICT_PATH}. Bộ sửa lỗi sẽ hoạt động yếu hơn.")


# ---- clean function ----

def vietnamese_text_clean(text: str) -> str:
    """
    Sửa lỗi OCR cơ bản bằng từ điển tiếng Việt.
    """
    output_words = []
    for word in text.split():
        lw = word.lower()

        # Nếu từ OCR ra đúng → giữ nguyên
        if lw in VI_WORDS:
            output_words.append(word)
            continue

        # fallback: dùng unidecode để normalize
        norm = unidecode(word)

        # Nếu normalize trùng từ điển → thay thế
        if norm.lower() in VI_WORDS:
            output_words.append(norm)
        else:
            output_words.append(word)

    return " ".join(output_words)
