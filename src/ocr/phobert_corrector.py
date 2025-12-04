"""
PhoBERT-based Vietnamese Spell Corrector

Uses VinAI PhoBERT for context-aware Vietnamese spell correction.
Combines dictionary lookup with language model predictions.
"""

from typing import List, Dict, Tuple, Optional
import os
import re
from functools import lru_cache

try:
    from transformers import AutoTokenizer, AutoModelForMaskedLM
    import torch
    PHOBERT_AVAILABLE = True
except ImportError:
    PHOBERT_AVAILABLE = False
    print("[WARNING] transformers not installed. PhoBERT correction disabled.")

try:
    from Levenshtein import distance as levenshtein_distance
except ImportError:
    # Fallback to simple character distance
    def levenshtein_distance(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]


# Configuration
PHOBERT_MODEL = "vinai/phobert-base"
CONFIDENCE_THRESHOLD = 0.6
MAX_CANDIDATES = 5


class PhoBERTCorrector:
    """Context-aware Vietnamese spell corrector using PhoBERT"""
    
    def __init__(self, dictionary_path: Optional[str] = None):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load dictionary
        if dictionary_path and os.path.exists(dictionary_path):
            self.dictionary = self._load_dictionary(dictionary_path)
        else:
            # Use default path relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            default_dict = os.path.join(base_dir, "..", "..", "enterprise_ocr", "vietnamese", "dictionary", "words.txt")
            if os.path.exists(default_dict):
                self.dictionary = self._load_dictionary(default_dict)
            else:
                self.dictionary = set()
                print(f"[WARNING] Dictionary not found. Spell correction will be limited.")
        
        # Load PhoBERT lazily (on first use)
        self._model_loaded = False
    
    def _load_dictionary(self, path: str) -> set:
        """Load Vietnamese word dictionary"""
        words = set()
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if word and not word.startswith('#'):
                        words.add(word)
            print(f"[PhoBERT] Loaded {len(words)} words from dictionary")
        except Exception as e:
            print(f"[ERROR] Failed to load dictionary: {e}")
        return words
    
    def _load_model(self):
        """Lazy load PhoBERT model"""
        if self._model_loaded or not PHOBERT_AVAILABLE:
            return
        
        try:
            print(f"[PhoBERT] Loading model {PHOBERT_MODEL}...")
            self.tokenizer = AutoTokenizer.from_pretrained(PHOBERT_MODEL)
            self.model = AutoModelForMaskedLM.from_pretrained(PHOBERT_MODEL)
            self.model.to(self.device)
            self.model.eval()
            self._model_loaded = True
            print(f"[PhoBERT] Model loaded on {self.device}")
        except Exception as e:
            print(f"[ERROR] Failed to load PhoBERT: {e}")
            PHOBERT_AVAILABLE = False
    
    def is_correct_word(self, word: str) -> bool:
        """Check if word exists in dictionary"""
        return word.lower() in self.dictionary
    
    def get_dictionary_candidates(self, word: str, max_distance: int = 2) -> List[Tuple[str, int]]:
        """Get candidate corrections from dictionary using Levenshtein distance"""
        word_lower = word.lower()
        candidates = []
        
        for dict_word in self.dictionary:
            dist = levenshtein_distance(word_lower, dict_word)
            if dist <= max_distance:
                candidates.append((dict_word, dist))
        
        # Sort by distance (lower is better)
        candidates.sort(key=lambda x: x[1])
        return candidates[:MAX_CANDIDATES]
    
    def predict_with_phobert(self, sentence: str, word_index: int) -> List[str]:
        """Use PhoBERT to predict word in context"""
        if not PHOBERT_AVAILABLE or not self._model_loaded:
            return []
        
        try:
            # Tokenize sentence
            words = sentence.split()
            if word_index >= len(words):
                return []
            
            # Replace target word with <mask>
            masked_words = words.copy()
            masked_words[word_index] = '<mask>'
            masked_sentence = ' '.join(masked_words)
            
            # Tokenize and predict
            inputs = self.tokenizer(masked_sentence, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = outputs.logits
            
            # Find mask token position
            mask_token_index = (inputs.input_ids == self.tokenizer.mask_token_id).nonzero(as_tuple=True)[1]
            
            if len(mask_token_index) == 0:
                return []
            
            # Get top predictions
            mask_token_logits = predictions[0, mask_token_index, :]
            top_tokens = torch.topk(mask_token_logits, MAX_CANDIDATES, dim=1).indices[0].tolist()
            
            # Decode tokens
            candidates = [self.tokenizer.decode([token]).strip() for token in top_tokens]
            
            return candidates
        
        except Exception as e:
            print(f"[ERROR] PhoBERT prediction failed: {e}")
            return []
    
    def correct_word(self, word: str, sentence: str = "", word_index: int = -1) -> str:
        """
        Correct a single word using dictionary + PhoBERT
        
        Args:
            word: Word to correct
            sentence: Full sentence for context
            word_index: Position of word in sentence
        
        Returns:
            Corrected word
        """
        # If word is correct, return as-is
        if self.is_correct_word(word):
            return word
        
        # Strategy 1: Dictionary-based correction (fastest)
        dict_candidates = self.get_dictionary_candidates(word, max_distance=2)
        
        if dict_candidates:
            best_candidate, distance = dict_candidates[0]
            
            # If very close match (1 char diff), use it
            if distance == 1:
                return best_candidate
        
        # Strategy 2: PhoBERT context-based correction (slower but more accurate)
        if sentence and word_index >= 0 and PHOBERT_AVAILABLE:
            self._load_model()
            phobert_candidates = self.predict_with_phobert(sentence, word_index)
            
            # Prioritize PhoBERT candidates that are also in dictionary
            for candidate in phobert_candidates:
                if candidate.lower() in self.dictionary:
                    return candidate
            
            # If PhoBERT suggests something close to original, use it
            for candidate in phobert_candidates:
                if levenshtein_distance(word.lower(), candidate.lower()) <= 2:
                    return candidate
        
        # Strategy 3: Use best dictionary match if available
        if dict_candidates and dict_candidates[0][1] <= 2:
            return dict_candidates[0][0]
        
        # Give up, return original
        return word
    
    def correct_text(self, text: str, use_context: bool = True) -> str:
        """
        Correct full text
        
        Args:
            text: Input text
            use_context: Whether to use PhoBERT for context-aware correction
        
        Returns:
            Corrected text
        """
        if not text.strip():
            return text
        
        # Split into words
        words = text.split()
        corrected_words = []
        
        for i, word in enumerate(words):
            # Skip punctuation and numbers
            if not word or not any(c.isalpha() for c in word):
                corrected_words.append(word)
                continue
            
            # Extract word without punctuation
            word_clean = re.sub(r'[^\w\s]', '', word)
            
            if not word_clean:
                corrected_words.append(word)
                continue
            
            # Correct word
            if use_context:
                corrected = self.correct_word(word_clean, text, i)
            else:
                corrected = self.correct_word(word_clean)
            
            # Restore punctuation
            if word != word_clean:
                # Find punctuation positions
                prefix = word[:len(word) - len(word.lstrip('[^\w\s]'))]
                suffix = word[len(word.rstrip('[^\w\s]')):]
                corrected = prefix + corrected + suffix
            
            corrected_words.append(corrected)
        
        return ' '.join(corrected_words)


# Global instance (lazy loaded)
_corrector_instance = None


def get_corrector() -> PhoBERTCorrector:
    """Get singleton corrector instance"""
    global _corrector_instance
    if _corrector_instance is None:
        _corrector_instance = PhoBERTCorrector()
    return _corrector_instance


def correct_vietnamese_text(text: str, use_phobert: bool = True) -> str:
    """
    Convenience function for correcting Vietnamese text
    
    Args:
        text: Input text
        use_phobert: Whether to use PhoBERT (slower but more accurate)
    
    Returns:
        Corrected text
    """
    corrector = get_corrector()
    return corrector.correct_text(text, use_context=use_phobert)


# For batch processing
def correct_batch(texts: List[str], use_phobert: bool = True) -> List[str]:
    """Correct multiple texts"""
    corrector = get_corrector()
    return [corrector.correct_text(text, use_context=use_phobert) for text in texts]


if __name__ == "__main__":
    # Test
    test_cases = [
        "giang day tieng viet",
        "sinh vien hoc tap",
        "truong dai hoc dien luc",
    ]
    
    corrector = PhoBERTCorrector()
    
    for test in test_cases:
        corrected = corrector.correct_text(test, use_context=False)
        print(f"Original:  {test}")
        print(f"Corrected: {corrected}")
        print()
