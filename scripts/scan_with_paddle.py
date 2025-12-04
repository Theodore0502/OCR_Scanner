"""
PaddleOCR Engine Integration for Vietnamese OCR

Usage: python scripts/scan_with_paddle.py <image_path>
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paddleocr import PaddleOCR
from src.ocr.engine_doctr import post_process_vietnamese_enhanced
from src.ocr.vietnamese_text_cleaner import vietnamese_text_clean

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='vi', show_log=False)


def ocr_paddle_image(img_path: str) -> str:
    """
    OCR image using PaddleOCR
    
    Args:
        img_path: Path to image
        
    Returns:
        Extracted and cleaned text
    """
    # Run OCR
    result = ocr.ocr(img_path, cls=True)
    
    # Extract text from result
    lines = []
    if result and result[0]:
        for line in result[0]:
            text = line[1][0]  # Extract text from (bbox, (text, confidence))
            if text.strip():
                lines.append(text.strip())
    
    # Combine lines
    raw_text = '\n'.join(lines)
    
    # Process each line separately
    processed_lines = []
    for line in lines:
        # Enhanced post-processing
        cleaned = post_process_vietnamese_enhanced(line)
        cleaned = vietnamese_text_clean(cleaned)
        processed_lines.append(cleaned)
    
    return '\n'.join(processed_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/scan_with_paddle.py <image_path> [output.txt]")
        print()
        print("Example:")
        print("  python scripts/scan_with_paddle.py data/raw/dl_2025_0003/dl_2025_0003.jpg")
        sys.exit(1)
    
    img_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(img_path):
        print(f"❌ File not found: {img_path}")
        sys.exit(1)
    
    print(f"🔍 Scanning with PaddleOCR: {img_path}")
    
    try:
        text = ocr_paddle_image(img_path)
        
        # Auto-generate output path if not provided
        if output_path is None:
            # Mirror structure: raw → results
            path = Path(img_path)
            if 'raw' in path.parts:
                raw_idx = path.parts.index('raw')
                output_parts = list(path.parts[:raw_idx]) + ['results'] + list(path.parts[raw_idx+1:])
                output_path = Path(*output_parts).with_suffix('.txt')
                output_path = str(output_path).replace('_paddle', '')  # Clean filename
            else:
                output_path = path.with_suffix('.txt')
        
        # Save output
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✅ Saved to: {output_path}")
        print(f"   Lines: {text.count(chr(10)) + 1}")
        print(f"   Characters: {len(text)}")
        print()
        print("=" * 60)
        print("CONTENT:")
        print("=" * 60)
        print(text)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
