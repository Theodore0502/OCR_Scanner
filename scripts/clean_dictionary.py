import json
import re
import unicodedata

INPUT = "data/raw_dict.jsonl"
OUTPUT = "data/vietnamese_words.txt"

def normalize_text(text):
    text = text.strip()

    # chuẩn unicode NFC
    text = unicodedata.normalize("NFC", text)

    # chuyển nhiều dấu space thành 1
    text = re.sub(r"\s+", " ", text)

    return text

def is_valid_word(text):
    # Cho phép a-z A-Z À-Ỵ à-ỵ và dấu gạch ngang
    return bool(re.match(r"^[\wÀ-Ỵà-ỵ\- ]+$", text))

def main():
    words = set()

    with open(INPUT, "r", encoding="utf8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                text = obj.get("text", "").strip()

                if not text:
                    continue

                text = normalize_text(text)

                if is_valid_word(text):
                    words.add(text)
            except:
                pass

    with open(OUTPUT, "w", encoding="utf8") as f:
        for w in sorted(words):
            f.write(w + "\n")

    print("Done! Saved:", OUTPUT)

if __name__ == "__main__":
    main()
