import re
from rapidfuzz import process, fuzz

# Từ điển tiếng Việt đơn giản (có thể mở rộng)
with open("data/vietnamese_words.txt", "r", encoding="utf8") as f:
    VN_WORDS = [w.strip() for w in f.readlines()]

def autocorrect_word(w):
    if len(w) <= 2:
        return w

    best = process.extractOne(w, VN_WORDS, scorer=fuzz.WRatio)
    if best and best[1] > 80:   # confidence threshold
        return best[0]
    return w

def autocorrect_text(text):
    words = re.findall(r"[A-Za-zÀ-ỹ]+", text)
    corrected = {}
    for w in words:
        corrected[w] = autocorrect_word(w)

    for w, c in corrected.items():
        text = text.replace(w, c)
    return text
