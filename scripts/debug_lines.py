"""
Debug script to check how many lines DocTR detects and show line-by-line output
"""
import sys
sys.path.insert(0, '.')

from src.ocr.engine_doctr import ocr_doctr_image

# OCR the image
print("Running OCR...")
text = ocr_doctr_image("temp_doctr_preprocessed.jpg")

# Split into lines
lines = text.split('\n')

print(f"\n{'='*60}")
print(f"TOTAL LINES DETECTED: {len(lines)}")
print(f"{'='*60}\n")

# Show each line separately
for i, line in enumerate(lines, 1):
    if line.strip():
        print(f"Line {i:2d}: {line}")
        print()

# Save with proper line breaks
with open('result_linebyline.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"\n{'='*60}")
print("Saved to: result_linebyline.txt")
print(f"{'='*60}")
