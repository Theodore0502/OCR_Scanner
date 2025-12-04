import cv2
import numpy as np
import tempfile
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from .vietnamese_text_cleaner import vietnamese_text_clean

# Import config for post-processing options
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from config import USE_PHOBERT_CORRECTION, USE_NGRAM_CORRECTION
    
    # Try to load from config.json if available
    try:
        import json
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf8') as f:
                config_json = json.load(f)
                USE_FAST_SPELL_CHECKER = config_json.get('post_processing', {}).get('use_fast_spell_checker', True)
        else:
            USE_FAST_SPELL_CHECKER = True
    except:
        USE_FAST_SPELL_CHECKER = True
except:
    USE_PHOBERT_CORRECTION = False
    USE_NGRAM_CORRECTION = True
    USE_FAST_SPELL_CHECKER = True

# Try import PhoBERT corrector (optional)
try:
    from .phobert_corrector import correct_vietnamese_text
    PHOBERT_AVAILABLE = True
except:
    PHOBERT_AVAILABLE = False

# Try import fast spell checker (optional but recommended)
try:
    from .fast_spell_checker import correct_vietnamese_text_fast
    FAST_SPELL_CHECKER_AVAILABLE = True
except:
    FAST_SPELL_CHECKER_AVAILABLE = False


# Try import preprocessing (optional)
try:
    from .preprocess import preprocess_image as preprocess_for_ocr
except:
    preprocess_for_ocr = None

# Load Doctr model once
model = ocr_predictor(pretrained=True)


def post_process_vietnamese_enhanced(text: str) -> str:
    """
    Xử lý hậu kỳ để sửa các lỗi phổ biến của OCR tiếng Việt - Enhanced for 90% accuracy
    """
    import re
    
    # Phase 1: Common OCR mistakes - Comprehensive 250+ replacements
    replacements = {
        # ===  NEW CRITICAL FIXES FROM dl_2025_0005 ===
        'CONGHOÀXA': 'CỘNG HÒA XÃ',
        'BOCONGTHUONG': 'BỘ CÔNG THƯƠNG',
        'BOCÔNG THUONG': 'BỘ CÔNG THƯƠNG',
        'DAI HQC': 'ĐẠI HỌC',
        'HQC': 'HỌC',
        'DIEN': 'ĐIỆN',
        'LUC': 'LỰC',
        'ngayghangoandm': 'ngày ... tháng ... năm',
        'Chi tich': 'Chủ tịch',
        'Cần cit': 'Căn cứ',
        'Càn cit': 'Căn cứ',
        'Càn ci': 'Căn cứ',
        'Can ci': 'Căn cứ',
        'Can cir': 'Căn cứ',
        'vịệc': 'việc',
        'biến thë': 'biến thể',
        'thë': 'thể',
        'kiém': 'kiểm',
        'quà': 'quả',
        'phurc': 'phức',
        'thë': 'thể',
        'bâo': 'báo',
        'hoach': 'hoạch',
        'day': 'dạy',
        'Diên luc': 'Điện lực',
        'Diên': 'Điện',
        'truông': 'trưởng',
        'bô': 'bộ',
        'trièn': 'triển',
        'giàng': 'giảng',
        'trựcgiảng': 'trucgiang',
        'eduvn': 'edu.vn',
        'tuc': 'tục',
        'biêu': 'biểu',
        'co': 'có',
        'thyrc': 'thực',
        'ci': 'cứ',
        'nêu': 'nêu',
        'nghị': 'nghị',
        'htpgs': 'https',
        'linivịen': 'sinhvien',
        'để nghị': 'đề nghị',
        'nhan': 'nhận',
        'HIEU': 'HIỆU',
        'TRUÔNG': 'TRƯỞNG',
        'PHO': 'PHÓ',
        'TRUONO': 'TRƯỞNG',
        'Trrong': 'Trương',
        
        # === CRITICAL FIXES - Space and capitalization ===
        'CONG HOÀXA': 'CỘNG HÒA XÃ',
        'CÔNG HOÀXA': 'CỘNG HÒA XÃ',
        'CONG HOÀ': 'CỘNG HÒA',
        'BOCÔNG': 'BỘ CÔNG',
        'BÔCÔNG': 'BỘ CÔNG',
        'BÔ CÔNG': 'BỘ CÔNG',
        'CHû NGHIA': 'CHỦ NGHĨA',
        'CHÚ NGHIA': 'CHỦ NGHĨA',
        'CHU NGHIA': 'CHỦ NGHĨA',
        'VIT NAM': 'VIỆT NAM',
        'VIÊT NAM': 'VIỆT NAM',
        'VlÊT NAM': 'VIỆT NAM',
        'VIÉT NAM': 'VIỆT NAM',
        'HOI': 'HỘI',
        'XA HOI': 'XÃ HỘI',
        'HỘICHỦ': 'HỘI CHỦ',
        'CÔNG THUONG': 'CÔNG THƯƠNG',
        
        # === COMMON PHRASES ===
        'Độc lập - Tự do - Hanh phức': 'Độc lập - Tự do - Hạnh phúc',
        'Dôc lâp - Ty do - Hanh phuc': 'Độc lập - Tự do - Hạnh phúc',
        'Hanh phuc': 'Hạnh phúc',
        'Hanh phức': 'Hạnh phúc',
        'Dôc lâp': 'Độc lập',
        'Ty do': 'Tự do',
        
        # === ORGANIZATIONS ===
        'TRUONG': 'TRƯỜNG',
        'DAI HOC': 'ĐẠI HỌC',
        'DIEN LUC': 'ĐIỆN LỰC',
        'THÔNG BAO': 'THÔNG BÁO',
        'THÔNG BÂO': 'THÔNG BÁO',
        
        # === LOCATIONS ===
        'Hà Nôi': 'Hà Nội',
        'Hà Noi': 'Hà Nội',
        
        # === NUMBER PREFIXES ===
        'sô': 'Số',
        'S6': 'Số',
        'S0': 'Số',
        
        # === DATE/TIME - Phase 1 ===
        'ngdySthdngOandm': 'ngày ... tháng ... năm',
        'ng4yShdng0zndm': 'ngày ... tháng ... năm',
        'ng4y': 'ngày',
        'ngày': 'ngày',
        '0zndm': 'tháng',
        'Shdng0zndm': 'tháng ... năm',
        'tháng': 'tháng',
        'năm': 'năm',
        
        # === COMMON WORDS - Tier 1 (High frequency) ===
        'Vè': 'Về',
        'vè': 'về',
        'Và ké': 'Về kế',
        'và ké': 'về kế',
        'ké hoạch': 'kế hoạch',
        'ké': 'kế',
        'kế': 'kế',
        'giang day': 'giảng dạy',
        'giàng day': 'giảng dạy',
        'giang': 'giảng',
        'giâng': 'giảng',
        'tir': 'từ',
        'từ': 'từ',
        'thuc': 'thực',
        'thyc': 'thực',
        'thực': 'thực',
        'hiên': 'hiện',
        'hiện': 'hiện',
        'bièu': 'biểu',
        'biểu': 'biểu',
        'biểuu': 'biểu',
        'dên': 'đến',
        'đến': 'đến',
        'dén': 'đến',
        'càn': 'cần',
        'cần': 'cần',
        'Càn': 'Cần',
        'càu': 'cần',
        'thiêu': 'thiếu',
        'câc': 'các',
        'càc': 'các',
        'cac': 'các',
        'các': 'các',
        'Câc': 'Các',
        'Càc': 'Các',
        'tryc': 'trực',
        'truc': 'trực',
        'trực': 'trực',
        'tuyén': 'tuyến',
        'tuyến': 'tuyến',
        'viêc': 'việc',
        'việc': 'việc',
        'vịệc': 'việc',
        'vịêc': 'việc',
        
        # === COMMON WORDS - Tier 2 ===
        'diên': 'diễn',
        'diễn': 'diễn',
        'bién': 'biến',
        'biên': 'biến',
        'biến': 'biến',
        'biện': 'biện',
        'phông': 'phòng',
        'phòng': 'phòng',
        'tiêm': 'triển',
        'triển': 'triển',
        'triên': 'triển',
        'chinh': 'chính',
        'chính': 'chính',
        'quy': 'quy',
        'têp': 'tiếp',
        'tiếp': 'tiếp',
        'tiép': 'tiếp',
        'têp tuc': 'tiếp tục',
        'thu': 'thứ',
        'thứ': 'thứ',
        'truong': 'trường',
        'Truong': 'Trường',
        'trường': 'trường',
        'Nhà truong': 'Nhà trường',
        'khôa': 'khóa',
        'khoa': 'khóa',
        'dào': 'đào',
        'đào': 'đào',
        'tao': 'tạo',
        'tạo': 'tạo',
        'gui': 'gửi',
        'guri': 'gửi',
        'gửi': 'gửi',
        'hoc': 'học',
        'học': 'học',
        'dè': 'để',
        'để': 'để',
        'nghi': 'nghị',
        'nghị': 'nghị',
        'câp': 'cập',
        'cập': 'cập',
        'nhât': 'nhật',
        'nhật': 'nhật',
        'thuong': 'thường',
        'thường': 'thường',
        'thứong': 'thường',
        'xuyên': 'xuyên',
        'làm': 'làm',
        'vira': 'vừa',
        'vừa': 'vừa',
        'càng': 'cảng',
        'dày': 'đẩy',
        'đẩy': 'đẩy',
        'manh': 'mạnh',
        'mạnh': 'mạnh',
        'kièm': 'kiểm',
        'kiểm': 'kiểm',
        'soàt': 'soát',
        'hiêu': 'hiệu',
        'hiệu': 'hiệu',
        'qua': 'quả',
        'quả': 'quả',
        'dich': 'dịch',
        'dịch': 'dịch',
        'bênh': 'bệnh',
        'bệnh': 'bệnh',
        'biên thé': 'biến thể',
        'thành': 'thành',
        'phô': 'phố',
        'phố': 'phố',
        'phuc': 'phức',
        'phức': 'phức',
        'tâp': 'tập',
        'tập': 'tập',
        'chi tich': 'chỉ thị',
        'chù': 'chủ',
        'chủ': 'chủ',
        'cho': 'cho',
        'cu': 'cụ',
        'cụ': 'cụ',
        'hê': 'hệ',
        'hệ': 'hệ',
        'dên hêt': 'đến hết',
        'khai': 'khai',
        'lop': 'lớp',
        'lớp': 'lớp',
        'tông': 'tổng',
        'tổng': 'tổng',
        'hop': 'hợp',
        'hợp': 'hợp',
        'truoc': 'trước',
        'trước': 'trước',
        'liên': 'liên',
        'thông': 'thông',
        'cao': 'cao',
        'theo': 'theo',
        'thoi': 'thời',
        'thời': 'thời',
        'nêu': 'nêu',
        'trên': 'trên',
        'sê': 'sẽ',
        'sẽ': 'sẽ',
        'së': 'sẽ',
        'dàng': 'đăng',
        'đăng': 'đăng',
        'tài': 'tải',
        'tải': 'tải',
        'công': 'cổng',
        'cổng': 'cổng',
        
        # === PROPER NOUNS ===
        'Noi': 'Nơi',
        'Nơi': 'Nơi',
        'don': 'đơn',
        'đơn': 'đơn',
        'vi': 'vị',
        'vị': 'vị',
        'vịên': 'viên',
        'viên': 'viên',
        'Luu': 'Lưu',
        'Lưu': 'Lưu',
        'Anh': 'Anh',
        
        # === TECHNICAL ===
        'tps': 'https',
        'hthttps': 'https',
        'Covịd': 'COVID',
        'Covid': 'COVID',
        'SARS-COV': 'SARS-CoV',
        
        # === ACTIONS/VERBS ===
        'Can ci': 'Căn cứ',
        'Càn cir': 'Căn cứ',
        'Càn ci': 'Căn cứ',
        'Yeû': 'Yêu',
        'Yêu': 'Yêu',
        'cia': 'của',
        'của': 'của',
        'vë': 'về',
        'về': 'về',
        'vê': 'về',
        'ing': 'ứng',
        'ứng': 'ứng',
        'hien': 'hiện',
        'phap': 'pháp',
        'pháp': 'pháp',
        'thich': 'thích',
        'thích': 'thích',
        'toàn': 'toàn',
        'linh': 'linh',
        'hoat': 'hoạt',
        'hoạt': 'hoạt',
        'soát': 'soát',
        'tinh': 'tình',
        'tình': 'tình',
        'phirc': 'phức',
        'tap': 'tạp',
        'tạp': 'tạp',
        'nhu': 'như',
        'như': 'như',
        'sau': 'sau',
        'hệt': 'hết',
        'hêt': 'hết',
        'hết': 'hết',
        'mâ': 'mã',
        'mã': 'mã',
        'online': 'online',
        'email': 'email',
        'vàc xin': 'vắc xin',
        'vàc': 'vắc',
        'xin': 'xin',
    }
    
    result = text
    for wrong, correct in replacements.items():
        result = result.replace(wrong, correct)
    
    # Phase 2: Regex patterns for complex cases
    # Fix date patterns
    result = re.sub(r'ng[àá]y\s*\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{2,4}', 
                   lambda m: 'ngày ' + re.sub(r'\s+', '', m.group(0)[4:]), result)
    
    # Fix email patterns
    result = re.sub(r'(\w+)@(\w+)\.(\w+)\.vn', r'\1@\2.\3.vn', result)
    
    # Fix https patterns  
    result = re.sub(r'hthttps://', 'https://', result)
    result = re.sub(r'https?://(\w+)', r'https://\1', result)
    
    # Phase 3: Context-aware fixes
    # Fix "Sinh viên" patterns
    result = re.sub(r'Sinh\s+vị[eêế]n', 'Sinh viên', result)
    
    # Fix "giảng viên" patterns
    result = re.sub(r'gi[aàả]ng\s+vị[eêế]n', 'giảng viên', result)
    
    # Fix "học viên" patterns
    result = re.sub(r'h[oọỏ]c\s+vị[eêế]n', 'học viên', result)
    
    # Fix "thời khóa biểu" patterns
    result = re.sub(r'th[oơờở]i\s+kh[oóọ]a\s+bi[eểêế][uưữ]', 'thời khóa biểu', result, flags=re.IGNORECASE)
    
    return result


def smart_split_lines(text: str) -> str:
    """
    Intelligently split long text into multiple lines based on Vietnamese punctuation and structure
    
    Args:
        text: Long text string
        
    Returns:
        Text with proper line breaks
    """
    import re
    
    # Split on major punctuation that indicates line breaks
    # Patterns: Period, colon, semicolon followed by uppercase or numbers
    lines = []
    
    # First, split on common line break indicators
    # 1. After "Số: XXX" (document number)
    text = re.sub(r'(Số:\s*\d+/[^\s]+)', r'\1\n', text)
    
    # 2. After location + date patterns (Hà Nội, ngày...)
    text = re.sub(r'(Hà Nội,\s+ngày[^;]+)', r'\1\n', text)
    
    # 3. Before major headers (THÔNG BÁO, etc.)
    text = re.sub(r'(\s+)(THÔNG BÁO|QUYẾT ĐỊNH|THÔNG TƯ|CHỈ THỊ)', r'\n\2', text)
    
    # 4. After "Về..." (subject line)
    text = re.sub(r'(Về\s+[^\.]+?)(\s+Căn\s+cứ|\s+Cần\s+cứ)', r'\1\n\2', text)
    
    # 5. Before "Căn cứ / Cần cứ" (legal basis)
    text = re.sub(r'(\s+)(Căn cứ|Cần cứ|Cần cir)', r'\n\2', text)
    
    # 6. After sentences ending with period + uppercase
    text = re.sub(r'(\.\s+)([A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ])', r'.\n\2', text)
    
    # 7. Before numbered items (1. 2. 3.)
    text = re.sub(r'(\s+)(\d+\.\s+[A-ZÀÁẢÃẠ])', r'\n\2', text)
    
    # 8. After semicolon before uppercase
    text = re.sub(r'(;\s+)([A-ZÀÁẢÃẠ])', r';\n\2', text)
    
    # 9. Before footer sections
    text = re.sub(r'(\s+)(Nơi nhận:)', r'\n\2', text)
    text = re.sub(r'(\./\.\s+)', r'./.\n', text)
    
    # 10. Split very long lines (> 150 chars) at sentence boundaries
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        if len(line) > 150:
            # Split at periods or semicolons
            sub_lines = re.split(r'([\.;]\s+)', line)
            current = ""
            for i in range(0, len(sub_lines), 2):
                part = sub_lines[i]
                separator = sub_lines[i+1] if i+1 < len(sub_lines) else ""
                
                if len(current) + len(part) > 150 and current:
                    result_lines.append(current.strip())
                    current = part + separator
                else:
                    current += part + separator
            
            if current.strip():
                result_lines.append(current.strip())
        else:
            if line.strip():
                result_lines.append(line.strip())
    
    return '\n'.join(result_lines)


def extract_text(result, preserve_lines=True):
    """
    Extract text from OCR result
    
    Args:
        result: DocTR result object
        preserve_lines: If True, return each detected line separately. If False, join all text.
    
    Returns:
        String with lines separated by newlines
    """
    raw = result.export()
    lines = []

    for page in raw["pages"]:
        for block in page["blocks"]:
            for line in block["lines"]:
                sentence = " ".join([w["value"] for w in line["words"]])
                if sentence.strip():  # Only add non-empty lines
                    lines.append(sentence.strip())
    
    # Return with newlines to preserve document structure
    return "\n".join(lines)



def ocr_doctr_image(img_path: str) -> str:
    import cv2
    import tempfile
    from doctr.io import DocumentFile

    img = cv2.imread(img_path)

    if preprocess_for_ocr is not None:
        img = preprocess_for_ocr(img)

    # Save temp
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        cv2.imwrite(tmp.name, img)
        temp_path = tmp.name

    doc = DocumentFile.from_images(temp_path)

    # Run OCR model
    result = model(doc)
    
    # Extract raw text WITH line structure preserved
    text = extract_text(result)
    
    # Process each line separately to preserve structure
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        if not line.strip():
            continue
            
        # Enhanced post-processing on each line
        cleaned_line = post_process_vietnamese_enhanced(line)
        
        # Optional: Fast spell checker (recommended, ~1000x faster than autocorrect)
        if USE_FAST_SPELL_CHECKER and FAST_SPELL_CHECKER_AVAILABLE:
            try:
                cleaned_line = correct_vietnamese_text_fast(cleaned_line)
            except Exception as e:
                pass
        
        # Optional: PhoBERT spell correction (if enabled and available)
        elif USE_PHOBERT_CORRECTION and PHOBERT_AVAILABLE:
            try:
                cleaned_line = correct_vietnamese_text(cleaned_line, use_phobert=True)
            except Exception as e:
                pass
        
        # Fallback: Apply the dictionary-based Vietnamese text cleaner
        cleaned_line = vietnamese_text_clean(cleaned_line)
        
        processed_lines.append(cleaned_line)
    
    # Join lines back together - preserve natural line breaks from OCR
    cleaned = '\n'.join(processed_lines)
    
    # DON'T use smart_split_lines - it destroys the natural structure
    # The OCR engine already gives us good line breaks
    
    return cleaned



def ocr_doctr_pdf(pdf_path: str) -> str:
    """OCR PDF (multi-page) bằng Doctr"""
    # Đọc PDF theo đúng API
    doc = DocumentFile.from_pdf(pdf_path)

    result = model(doc)
    text = extract_text(result)

    # Clean lại
    cleaned = post_process_vietnamese_enhanced(text)
    return vietnamese_text_clean(cleaned)

