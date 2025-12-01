# create_vietnamese_dict.py
WORDS = """
anh
em
tôi
chúng
ta
học
trường
đại
học
điện
lực
cộng
hòa
xã
hội
chủ
nghĩa
việt
nam
thông
báo
kế
hoạch
giảng
dạy
sinh
viên
... (1000 từ mẫu)
"""

# Tải 70k từ từ nguồn open-source
URL = "https://raw.githubusercontent.com/skywind3000/vietnamese-dictionary/master/Viet74K.txt"

import requests

def main():
    r = requests.get(URL)
    full_dict = set()

    # từ mẫu có dấu chuẩn
    for w in WORDS.split():
        full_dict.add(w.strip())

    # 70k từ open-source
    for w in r.text.split():
        full_dict.add(w.strip().lower())

    with open("data/vietnamese_words.txt", "w", encoding="utf8") as f:
        for w in sorted(full_dict):
            f.write(w + "\n")

    print("Done! Created data/vietnamese_words.txt")

if __name__ == "__main__":
    main()
