"""
Script để scan ảnh từ data/raw và lưu kết quả vào data/results
Tự động tạo folder structure dựa trên path gốc của ảnh

Sử dụng: 
    python scripts/scan_to_results.py <đường_dẫn_ảnh_trong_raw>
    
Ví dụ:
    python scripts/scan_to_results.py data/raw/dl_2025_0001/dl_2025_0001.jpg
    → Kết quả: data/results/dl_2025_0001/dl_2025_0001.txt
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ocr.engine_doctr import ocr_doctr_image


def scan_to_results(image_path: str):
    """
    Scan ảnh và lưu kết quả vào data/results với cấu trúc tương tự data/raw
    
    Args:
        image_path: Đường dẫn đến file ảnh (trong data/raw)
        
    Returns:
        Path to output file
    """
    # Kiểm tra file tồn tại
    if not os.path.exists(image_path):
        print(f"❌ Không tìm thấy file: {image_path}")
        return None
    
    # Parse path
    image_path = os.path.normpath(image_path)
    path_parts = Path(image_path).parts
    
    # Tìm vị trí của 'raw' trong path
    try:
        raw_index = path_parts.index('raw')
    except ValueError:
        print(f"❌ File phải nằm trong data/raw/")
        print(f"   Path hiện tại: {image_path}")
        return None
    
    # Lấy phần path sau 'raw' (ví dụ: dl_2025_0001/dl_2025_0001.jpg)
    relative_parts = path_parts[raw_index + 1:]
    
    # Tạo output path (thay raw -> results, .jpg -> .txt)
    output_parts = list(path_parts[:raw_index]) + ['results'] + list(relative_parts)
    output_path = os.path.join(*output_parts)
    output_path = Path(output_path).with_suffix('.txt')
    output_path = str(output_path)
    
    print(f"🔍 Đang scan ảnh với DocTR Enhanced...")
    print(f"   Input:  {image_path}")
    print(f"   Output: {output_path}")
    print()
    
    try:
        # OCR ảnh bằng DocTR với post-processing cải tiến
        text = ocr_doctr_image(image_path)
        
        # Tạo thư mục output nếu chưa có
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Lưu ra file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✅ Hoàn thành!")
        print(f"   Đã lưu tại: {output_path}")
        print(f"   Kích thước: {len(text)} ký tự")
        print(f"   Số dòng: {text.count(chr(10)) + 1}")
        print()
        print("=" * 60)
        print("📄 NỘI DUNG:")
        print("=" * 60)
        print(text)
        print("=" * 60)
        
        return output_path
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    if len(sys.argv) < 2:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║  SCAN ẢNH VÀ LƯU VÀO DATA/RESULTS                        ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print("Cách sử dụng:")
        print("  python scripts/scan_to_results.py <đường_dẫn_ảnh>")
        print()
        print("Ví dụ:")
        print("  python scripts/scan_to_results.py data/raw/dl_2025_0001/dl_2025_0001.jpg")
        print("  → Kết quả: data/results/dl_2025_0001/dl_2025_0001.txt")
        print()
        print("  python scripts/scan_to_results.py data/raw/dl_2025_0002/image.jpg")
        print("  → Kết quả: data/results/dl_2025_0002/image.txt")
        print()
        sys.exit(1)
    
    image_path = sys.argv[1]
    scan_to_results(image_path)


if __name__ == "__main__":
    main()
