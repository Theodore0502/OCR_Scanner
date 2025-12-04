"""
Test different preprocessing strategies to find best approach for each image
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2
import numpy as np
from pathlib import Path

def test_preprocessing_strategies(img_path):
    """Test different preprocessing approaches on an image"""
    
    img = cv2.imread(img_path)
    if img is None:
        print(f"Could not load image: {img_path}")
        return
    
    print(f"Testing preprocessing strategies on: {img_path}")
    print(f"Image shape: {img.shape}")
    print()
    
    strategies = {
        "original": img,
        "grayscale": cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        "adaptive_thresh": None,
        "otsu_thresh": None,
        "denoised": None,
    }
    
    # Adaptive threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    strategies["adaptive_thresh"] = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        35, 10
    )
    
    # Otsu threshold
    _, strategies["otsu_thresh"] = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    # Denoise
    strategies["denoised"] = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Save all variants
    output_dir = Path("data/preprocessing_tests")
    output_dir.mkdir(exist_ok=True)
    
    base_name = Path(img_path).stem
    
    for strategy_name, result_img in strategies.items():
        if result_img is None:
            continue
        output_path = output_dir / f"{base_name}_{strategy_name}.jpg"
        cv2.imwrite(str(output_path), result_img)
        print(f"✓ Saved: {output_path}")
    
    print()
    print("Now manually OCR each variant to find the best one!")
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_preprocessing.py <image_path>")
        print("Example: python scripts/test_preprocessing.py data/raw/dl_2025_0008/dl_2025_0008.jpg")
        sys.exit(1)
    
    test_preprocessing_strategies(sys.argv[1])
