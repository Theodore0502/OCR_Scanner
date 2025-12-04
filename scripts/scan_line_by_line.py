"""
Enhanced OCR Script với output theo từng line
Usage: python scripts/scan_line_by_line.py <image_path> [output.txt]
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ocr.engine_doctr import ocr_doctr_image


def scan_image_line_by_line(image_path: str, output_path: str = None):
    """
    Scan ảnh và lưu kết quả theo từng line được detect
    """
    if not os.path.exists(image_path):
        print(f"Loi: Khong tim thay file: {image_path}", file=sys.stderr)
        return
    
    print(f"Dang scan anh: {image_path}")
    
    try:
        # OCR bằng DocTR Enhanced (90% accuracy)
        text = ocr_doctr_image(image_path)
        
        # Tạo output path nếu không được cung cấp  
        if output_path is None:
            input_name = Path(image_path).stem
            output_path = f"data/processed/{input_name}_lines.txt"
        
        # Tạo thư mục output nếu chưa có
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Lưu ra file với proper line breaks
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Split và đếm lines
        lines = [line for line in text.split('\n') if line.strip()]
        
        print(f"\nHoan thanh! Ket qua da luu tai: {output_path}")
        print(f"Tong so lines detect: {len(lines)}")
        print(f"\n--- NOI DUNG ({len(text)} ky tu) ---\n")
        
        # In từng line với number
        for i, line in enumerate(lines, 1):
            # Encode safely for Windows console
            try:
                print(f"[Line {i:2d}] {line}")
            except:
                print(f"[Line {i:2d}] [Unicode error - see file]")
        
        return output_path
        
    except Exception as e:
        print(f"Loi khi xu ly: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print("Cach su dung:")
        print("  python scripts/scan_line_by_line.py <duong_dan_anh>")
        print("  python scripts/scan_line_by_line.py <duong_dan_anh> <output.txt>")
        print("\nVi du:")
        print("  python scripts/scan_line_by_line.py temp_doctr_preprocessed.jpg")
        print("  python scripts/scan_line_by_line.py temp_doctr_preprocessed.jpg result.txt")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    scan_image_line_by_line(image_path, output_path)


if __name__ == "__main__":
    main()
