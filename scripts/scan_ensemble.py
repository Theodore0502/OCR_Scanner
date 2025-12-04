"""
Ensemble OCR: Combine multiple OCR engines for best accuracy

Uses DocTR, PaddleOCR, and confidence scoring to select best result.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ocr.engine_doctr import ocr_doctr_image
from paddleocr import PaddleOCR
from src.ocr.engine_doctr import post_process_vietnamese_enhanced
from src.ocr.vietnamese_text_cleaner import vietnamese_text_clean

# Initialize PaddleOCR
paddle_ocr = PaddleOCR(use_angle_cls=True, lang='vi', show_log=False)


def ocr_paddle(img_path: str) -> tuple:
    """Run PaddleOCR and return (text, avg_confidence)"""
    result = paddle_ocr.ocr(img_path, cls=True)
    
    lines = []
    confidences = []
    
    if result and result[0]:
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            if text.strip():
                # Post-process
                cleaned = post_process_vietnamese_enhanced(text)
                cleaned = vietnamese_text_clean(cleaned)
                lines.append(cleaned)
                confidences.append(confidence)
    
    text = '\n'.join(lines)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    
    return text, avg_conf


def ocr_doctr(img_path: str) -> tuple:
    """Run DocTR and return (text, confidence)"""
    try:
        text = ocr_doctr_image(img_path)
        # DocTR doesn't provide confidence, estimate based on text quality
        # If text has many single characters, it's likely garbage
        words = text.split()
        if len(words) == 0:
            confidence = 0.0
        else:
            # Count words with length > 2
            good_words = sum(1 for w in words if len(w) > 2)
            confidence = good_words / len(words)
        
        return text, confidence
    except Exception as e:
        print(f"DocTR failed: {e}")
        return "", 0.0


def ensemble_ocr(img_path: str) -> dict:
    """
    Run ensemble OCR with multiple engines
    
    Returns:
        dict with keys: best_text, best_engine, all_results
    """
    print(f"🔍 Running ensemble OCR on: {img_path}")
    print()
    
    results = {}
    
    # Run PaddleOCR
    print("  → Running PaddleOCR...")
    paddle_text, paddle_conf = ocr_paddle(img_path)
    results['paddle'] = {'text': paddle_text, 'confidence': paddle_conf}
    print(f"     Confidence: {paddle_conf:.2%}")
    
    # Run DocTR
    print("  → Running DocTR...")
    doctr_text, doctr_conf = ocr_doctr(img_path)
    results['doctr'] = {'text': doctr_text, 'confidence': doctr_conf}
    print(f"     Confidence: {doctr_conf:.2%}")
    
    print()
    
    # Select best based on confidence
    best_engine = max(results.keys(), key=lambda k: results[k]['confidence'])
    best_text = results[best_engine]['text']
    
    print(f"✅ Best engine: {best_engine.upper()} ({results[best_engine]['confidence']:.2%})")
    
    return {
        'best_text': best_text,
        'best_engine': best_engine,
        'all_results': results
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/scan_ensemble.py <image_path> [output.txt]")
        print()
        print("Example:")
        print("  python scripts/scan_ensemble.py data/raw/dl_2025_0003/dl_2025_0003.jpg")
        sys.exit(1)
    
    img_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(img_path):
        print(f"❌ File not found: {img_path}")
        sys.exit(1)
    
    # Run ensemble
    result = ensemble_ocr(img_path)
    
    # Auto-generate output path
    if output_path is None:
        path = Path(img_path)
        if 'raw' in path.parts:
            raw_idx = path.parts.index('raw')
            output_parts = list(path.parts[:raw_idx]) + ['results'] + list(path.parts[raw_idx+1:])
            output_path = Path(*output_parts).with_suffix('.txt')
        else:
            output_path = path.with_suffix('.txt')
    
    # Save
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result['best_text'])
    
    print()
    print(f"📄 Saved to: {output_path}")
    print(f"   Engine: {result['best_engine'].upper()}")
    print(f"   Lines: {result['best_text'].count(chr(10)) + 1}")
    print()
    print("=" * 60)
    print("CONTENT:")
    print("=" * 60)
    print(result['best_text'])


if __name__ == "__main__":
    main()
