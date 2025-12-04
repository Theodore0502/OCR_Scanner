"""
VietOCR Engine - Hybrid approach
Sử dụng PaddleOCR cho text detection, VietOCR cho recognition (tiếng Việt tốt hơn)
"""
import os
import cv2
import numpy as np
from PIL import Image
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

# Global model caches
_vietocr_model = None
_paddle_detector = None


def get_vietocr_model():
    """
    Load VietOCR recognition model (cached)
    """
    global _vietocr_model
    
    if _vietocr_model is None:
        print("🔄 Đang load VietOCR model...")
        
        config = Cfg.load_config_from_name('vgg_transformer')
        config['device'] = 'cpu'
        config['predictor']['beamsearch'] = True
        
        _vietocr_model = Predictor(config)
        print("✅ VietOCR loaded!")
    
    return _vietocr_model


def get_paddle_detector():
    """
    Load PaddleOCR detector (chỉ dùng phần detection)
    """
    global _paddle_detector
    
    if _paddle_detector is None:
        print("🔄 Đang load PaddleOCR detector...")
        from paddleocr import PaddleOCR
        
        _paddle_detector = PaddleOCR(
            use_angle_cls=True,
            lang='vi',
            use_gpu=False,
            show_log=False,
            rec=False  # Chỉ dùng detection, không dùng recognition
        )
        print("✅ PaddleOCR detector loaded!")
    
    return _paddle_detector


def ocr_vietocr_image(image_path: str) -> str:
    """
    OCR full page bằng PaddleOCR detection + VietOCR recognition
    
    Args:
        image_path: Đường dẫn đến file ảnh
        
    Returns:
        Text được nhận dạng (tiếng Việt chính xác)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Không tìm thấy file: {image_path}")
    
    # Load models
    detector = get_paddle_detector()
    recognizer = get_vietocr_model()
    
    # Load ảnh
    img = cv2.imread(image_path)
    
    # Detect text regions
    print("🔍 Đang detect text regions...")
    detection_result = detector.ocr(image_path, rec=False)
    
    if not detection_result or not detection_result[0]:
        print("⚠️  Không phát hiện text trong ảnh")
        return ""
    
    boxes = detection_result[0]
    
    # Sort boxes by position (top to bottom, left to right)
    boxes = sorted(boxes, key=lambda box: (box[0][1], box[0][0]))
    
    # Recognize each text region với VietOCR
    print(f"✏️  Đang nhận dạng {len(boxes)} text regions...")
    lines = []
    
    for i, box in enumerate(boxes):
        # Get bounding box coordinates
        points = np.array(box).astype(np.int32)
        x_min = int(points[:, 0].min())
        y_min = int(points[:, 1].min())
        x_max = int(points[:, 0].max())
        y_max = int(points[:, 1].max())
        
        # Add padding
        padding = 5
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(img.shape[1], x_max + padding)
        y_max = min(img.shape[0], y_max + padding)
        
        # Crop region
        cropped = img[y_min:y_max, x_min:x_max]
        
        # Convert to PIL Image
        cropped_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        
        # Recognize với VietOCR
        try:
            text = recognizer.predict(cropped_pil)
            if text.strip():
                lines.append(text.strip())
        except Exception as e:
            print(f"⚠️  Lỗi khi nhận dạng region {i}: {e}")
            continue
    
    return "\n".join(lines)


def ocr_vietocr_pdf(pdf_path: str) -> str:
    """
    OCR một file PDF
    
    Args:
        pdf_path: Đường dẫn đến file PDF
        
    Returns:
        Text được nhận dạng từ tất cả các trang
    """
    from pdf2image import convert_from_path
    import tempfile
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Không tìm thấy file: {pdf_path}")
    
    print(f"🔄 Đang convert PDF sang ảnh...")
    images = convert_from_path(pdf_path, dpi=200)
    
    all_text = []
    for i, img in enumerate(images, 1):
        print(f"\n📄 Đang OCR trang {i}/{len(images)}...")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            temp_path = tmp.name
        
        try:
            text = ocr_vietocr_image(temp_path)
            all_text.append(text)
        finally:
            os.unlink(temp_path)
    
    return "\n\n".join(all_text)


if __name__ == "__main__":
    # Test script
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python engine_vietocr.py <image_path>")
        sys.exit(1)
    
    img_path = sys.argv[1]
    result = ocr_vietocr_image(img_path)
    
    print("\n" + "="*50)
    print("VietOCR HYBRID RESULT:")
    print("="*50)
    print(result)

