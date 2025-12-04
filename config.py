USE_GPU = True

PADDLE_OCR_CONFIG = {
    "use_gpu": False,     # ép chạy CPU
    "lang": "vi",
    "show_log": False,
}

# Post-processing configuration
USE_PHOBERT_CORRECTION = False  # PhoBERT is slow, enable for max accuracy
USE_NGRAM_CORRECTION = True      # N-gram based correction (fast)
PHOBERT_CONFIDENCE_THRESHOLD = 0.7  # Only correct words with confidence < 0.7
