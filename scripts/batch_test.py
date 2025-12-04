"""
Batch test multiple images with different OCR engines and compare accuracy

Usage: python scripts/batch_test.py
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import subprocess
import difflib


def calculate_accuracy(ocr_text, ground_truth):
    """Calculate character and word level accuracy"""
    # Normalize
    ocr_clean = ocr_text.replace('\n', ' ').replace('\r', '  ').strip()
    gt_clean = ground_truth.replace('\n', ' ').replace('\r', ' ').strip()
    
    # Character level
    sm = difflib.SequenceMatcher(None, gt_clean, ocr_clean)
    char_acc = sm.ratio() * 100
    
    # Word level
    ocr_words = ocr_clean.split()
    gt_words = gt_clean.split()
    sm_words = difflib.SequenceMatcher(None, gt_words, ocr_words)
    word_acc = sm_words.ratio() * 100
    
    return char_acc, word_acc


def test_document(doc_id, engine='ensemble'):
    """Test a single document"""
    img_path = f"data/raw/{doc_id}/{doc_id}.jpg"
    gt_path = f"data/raw/{doc_id}/legit_{doc_id}.txt"
    
    # Handle typo in dl_2025_0008
    if not os.path.exists(gt_path):
        gt_path = f"data/raw/{doc_id}/legigt_{doc_id}.txt"
    
    if not os.path.exists(img_path):
        return None
    if not os.path.exists(gt_path):
        print(f"⚠️  No ground truth for {doc_id}")
        return None
    
    # Run OCR based on engine
    output_path = f"data/results/{doc_id}/{doc_id}.txt"
    
    if engine == 'paddle':
        cmd = f"python scripts/scan_with_paddle.py {img_path}"
    elif engine == 'ensemble':
        cmd = f"python scripts/scan_ensemble.py {img_path}"
    else:  # doctr
        cmd = f"python scripts/scan_to_results.py {img_path}"
    
    print(f"  Running {engine.upper()}...")
    subprocess.run(cmd, shell=True, capture_output=True)
    
    # Read results
    if not os.path.exists(output_path):
        return None
    
    with open(output_path, 'r', encoding='utf-8') as f:
        ocr_text = f.read()
    
    with open(gt_path, 'r', encoding='utf-8') as f:
        gt_text = f.read()
    
    # Calculate accuracy
    char_acc, word_acc = calculate_accuracy(ocr_text, gt_text)
    
    return {
        'doc_id': doc_id,
        'engine': engine,
        'char_accuracy': char_acc,
        'word_accuracy': word_acc,
        'ocr_lines': ocr_text.count('\n') + 1,
        'gt_lines': gt_text.count('\n') + 1
    }


def main():
    docs = ['dl_2025_0003', 'dl_2025_0005', 'dl_2025_0008']
    engines = ['paddle', 'ensemble']
    
    print("=" * 70)
    print("BATCH OCR ACCURACY TEST")
    print("=" * 70)
    print()
    
    results = []
    
    for engine in engines:
        print(f"\n{'='*70}")
        print(f"Testing with {engine.upper()}")
        print(f"{'='*70}\n")
        
        for doc_id in docs:
            print(f"📄 {doc_id}:")
            result = test_document(doc_id, engine)
            if result:
                results.append(result)
                print(f"   ✅ Char: {result['char_accuracy']:.1f}% | Word: {result['word_accuracy']:.1f}%")
                print(f"      Lines: {result['ocr_lines']} (GT: {result['gt_lines']})")
            else:
                print(f"   ❌ Failed")
            print()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    # Group by engine
    for engine in engines:
        engine_results = [r for r in results if r['engine'] == engine]
        if engine_results:
            avg_char = sum(r['char_accuracy'] for r in engine_results) / len(engine_results)
            avg_word = sum(r['word_accuracy'] for r in engine_results) / len(engine_results)
            
            print(f"{engine.upper()}:")
            print(f"  Average Char Accuracy: {avg_char:.1f}%")
            print(f"  Average Word Accuracy: {avg_word:.1f}%")
            print(f"  Documents tested: {len(engine_results)}")
            print()
    
    # Best engine
    best_engine = max(engines, key=lambda e: sum(r['char_accuracy'] for r in results if r['engine'] == e))
    print(f"🏆 Best Engine: {best_engine.upper()}")


if __name__ == "__main__":
    main()
