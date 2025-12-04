"""
Script để scan ảnh và export ra file txt
Sử dụng: python scripts/scan_image_to_txt.py <đường_dẫn_ảnh> [đường_dẫn_output.txt]
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ocr.engine_doctr import ocr_doctr_image


def scan_image_to_txt(image_path: str, output_path: str = None):
    """
    Scan ảnh và lưu kết quả ra file txt
    
    Args:
        image_path: Đường dẫn đến file ảnh (jpg, png, tiff...)
        output_path: Đường dẫn file txt output (optional)
    """
    # Kiểm tra file tồn tại
    if not os.path.exists(image_path):
        print(f"❌ Không tìm thấy file: {image_path}")
        return
    
    print(f"🔍 Đang scan ảnh với DocTR (Enhanced): {image_path}")
    
    try:
        # OCR ảnh bằng DocTR với post-processing cải tiến
        text = ocr_doctr_image(image_path)
        
        # Tạo output path nếu không được cung cấp
        if output_path is None:
            input_name = Path(image_path).stem
            output_path = f"data/processed/{input_name}_enhanced.txt"
        
        # Tạo thư mục output nếu chưa có
        output_dir = os.path.dirname(output_path)
        if output_dir:  # Only create if path has a directory
            os.makedirs(output_dir, exist_ok=True)
        
        # Lưu ra file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✅ Hoàn thành! Kết quả đã lưu tại: {output_path}")
        print(f"\n📄 Nội dung ({len(text)} ký tự):\n")
        print(text)
        
        return output_path
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print("Cách sử dụng:")
        print("  python scripts/scan_image_to_txt.py <đường_dẫn_ảnh>")
        print("  python scripts/scan_image_to_txt.py <đường_dẫn_ảnh> <output.txt>")
        print("\nVí dụ:")
        print("  python scripts/scan_image_to_txt.py data/samples/vanban.jpg")
        print("  python scripts/scan_image_to_txt.py temp_doctr_preprocessed.jpg ketqua.txt")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    scan_image_to_txt(image_path, output_path)


if __name__ == "__main__":
    main()

