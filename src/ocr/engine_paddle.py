"""
Enhanced PaddleOCR Engine - Tối ưu cho tiếng Việt
Sử dụng PaddleOCR với Vietnamese language model + post-processing
"""
import os
from paddleocr import PaddleOCR

# Global model cache
_paddle_model = None


def get_paddle_ocr():
    """
    Load PaddleOCR model (cached)
    """
    global _paddle_model
    
    if _paddle_model is None:
        print("🔄 Đang load PaddleOCR cho tiếng Việt...")
        
        _paddle_model = PaddleOCR(
            use_angle_cls=True,
            lang='vi',  # Vietnamese language
            use_gpu=False,
            show_log=False,
            det_db_thresh=0.3,  # Lower threshold for better detection
            rec_batch_num=6,  # Batch processing
        )
        print("✅ PaddleOCR loaded!")
    
    return _paddle_model


def post_process_vietnamese(text: str) -> str:
    """
    Xử lý hậu kỳ để sửa các lỗi phổ biến của OCR tiếng Việt
    """
    # Common OCR mistakes fixes
    replacements = {
        # Space issues
        'CONG HOÀXA': 'CỘNG HÒA XÃ',
        'CÔNG HOÀXA': 'CỘNG HÒA XÃ',
        'CHû NGHIA': 'CHỦ NGHĨA',
        'VIT NAM': 'VIỆT NAM',
        'VIÊT NAM': 'VIỆT NAM',
        'Hà Nôi': 'Hà Nội',
        'tir': 'từ',
        'thuc': 'thực',
        'hiên': 'hiện',
        'bièu': 'biểu',
        'dên': 'đến',
        'càn': 'cần',
        'Và ké': 'Về kế',
        'ké hoach': 'kế hoạch',
        'thiêu': 'thiếu',
        'câc': 'các',
        'tryc': 'trực',
        'tuyén': 'tuyến',
        'ngày': 'ngày',  # This is already correct
        'ngày': 'ngày',
        
        # Number-letter confusion
        'S6': 'Số',
        'ng4y': 'ngày',
        '0zndm': '03 tháng',
        'Shdng0zndm': '03 tháng',
        
        # Common word corrections
        'Dôc lâp': 'Độc lập',
        'Ty do': 'Tự do',
        'Hanh phuc': 'Hạnh phúc',
        'BÔCÔNG': 'BỘ CÔNG',
        'BÔ': 'BỘ',
        'HOI': 'HỘI',
    }
    
    result = text
    for wrong, correct in replacements.items():
        result = result.replace(wrong, correct)
    
    return result


def ocr_paddle_image(image_path: str) -> str:
    """
    OCR ảnh bằng PaddleOCR + post-processing
    
    Args:
        image_path: Đường dẫn file ảnh
        
    Returns:
        Text đã được làm sạch
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Không tìm thấy file: {image_path}")
    
    model = get_paddle_ocr()
    
    print(f"🔍 Đang OCR với PaddleOCR...")
    result = model.ocr(image_path, cls=True)
    
    if not result or not result[0]:
        print("⚠️  Không phát hiện text")
        return ""
    
    # Extract text from results
    lines = []
    for line in result[0]:
        text = line[1][0] # [1][0] is the text
        lines.append(text)
    
    raw_text = "\n".join(lines)
    
    # Post-processing
    cleaned_text = post_process_vietnamese(raw_text)
    
    return cleaned_text


def ocr_paddle_pdf(pdf_path: str) -> str:
    """
    OCR file PDF
    
    Args:
        pdf_path: Đường dẫn file PDF
        
    Returns:
        Text từ tất cả các trang
    """
    from pdf2image import convert_from_path
    import tempfile
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Không tìm thấy file: {pdf_path}")
    
    print(f"🔄 Đang convert PDF...")
    images = convert_from_path(pdf_path, dpi=200)
    
    all_text = []
    for i, img in enumerate(images, 1):
        print(f"\n📄 OCR trang {i}/{len(images)}...")
        
        # Save to temp
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            temp_path = tmp.name
        
        try:
            text = ocr_paddle_image(temp_path)
            all_text.append(text)
        finally:
            os.unlink(temp_path)
    
    return "\n\n".join(all_text)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python engine_paddle.py <image_path>")
        sys.exit(1)
    
    result = ocr_paddle_image(sys.argv[1])
    
    print("\n" + "="*50)
    print("PaddleOCR RESULT (Enhanced):")
    print("="*50)
    print(result)
