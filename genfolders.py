import os

base_path = r"D:\Sources\-----OCR_Scanner\ocr_scanner\data\raw"  # đổi đường dẫn bạn muốn
prefix = "dl_2025_"

for i in range(3, 51):  # 0003 -> 0050
    folder_name = f"{prefix}{i:04d}"
    full_path = os.path.join(base_path, folder_name)
    os.makedirs(full_path, exist_ok=True)
    print("Đã tạo:", full_path)
