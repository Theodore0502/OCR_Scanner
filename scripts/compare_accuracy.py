"""
Script so sánh kết quả OCR với ground truth và tính accuracy

Usage: python scripts/compare_accuracy.py <ocr_result.txt> <ground_truth.txt>
"""
import sys
import difflib
from pathlib import Path


def calculate_accuracy(ocr_text, ground_truth):
    """Tính accuracy dựa trên character-level và word-level"""
    
    # Character-level accuracy
    ocr_chars = list(ocr_text.replace('\n', '').replace('\r', '').replace(' ', ''))
    gt_chars = list(ground_truth.replace('\n', '').replace('\r', '').replace(' ', ''))
    
    sm = difflib.SequenceMatcher(None, gt_chars, ocr_chars)
    char_accuracy = sm.ratio() * 100
    
    # Word-level accuracy
    ocr_words = ocr_text.split()
    gt_words = ground_truth.split()
    
    sm_words = difflib.SequenceMatcher(None, gt_words, ocr_words)
    word_accuracy = sm_words.ratio() * 100
    
    return char_accuracy, word_accuracy


def show_diff(ocr_text, ground_truth):
    """Hiển thị difference giữa OCR và ground truth"""
    diff = difflib.unified_diff(
        ground_truth.splitlines(keepends=True),
        ocr_text.splitlines(keepends=True),
        fromfile='Ground Truth',
        tofile='OCR Result',
        lineterm=''
    )
    
    return ''.join(diff)


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/compare_accuracy.py <ocr_result.txt> <ground_truth.txt>")
        print()
        print("Example:")
        print("  python scripts/compare_accuracy.py data/results/dl_2025_0005/dl_2025_0005.txt data/raw/dl_2025_0005/legit_dl_2025_0005.txt")
        sys.exit(1)
    
    ocr_path = sys.argv[1]
    gt_path = sys.argv[2]
    
    # Read files
    with open(ocr_path, 'r', encoding='utf-8') as f:
        ocr_text = f.read()
    
    with open(gt_path, 'r', encoding='utf-8') as f:
        gt_text = f.read()
    
    # Calculate accuracy
    char_acc, word_acc = calculate_accuracy(ocr_text, gt_text)
    
    print("=" * 70)
    print("OCR ACCURACY REPORT")
    print("=" * 70)
    print(f"OCR File:         {ocr_path}")
    print(f"Ground Truth:     {gt_path}")
    print()
    print(f"Character Accuracy: {char_acc:.2f}%")
    print(f"Word Accuracy:      {word_acc:.2f}%")
    print()
    print("=" * 70)
    print("DIFFERENCES:")
    print("=" * 70)
    diff = show_diff(ocr_text, gt_text)
    print(diff)
    print("=" * 70)


if __name__ == "__main__":
    main()
