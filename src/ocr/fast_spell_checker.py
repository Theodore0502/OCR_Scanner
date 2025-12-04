"""
Fast Vietnamese Spell Checker using SymSpell Algorithm

This module provides a high-performance spell checker optimized for Vietnamese text.
Uses SymSpell algorithm for O(1) lookup instead of O(n) brute-force Levenshtein.

Performance: ~1000x faster than naive approach for large dictionaries.
"""

from typing import Dict, List, Tuple, Optional, Set
import json
import os
from collections import defaultdict
from functools import lru_cache


class SymSpellChecker:
    """
    SymSpell-based spell checker with Vietnamese dictionary support.
    
    SymSpell generates all possible variations of a word within edit distance
    at index time, allowing for constant-time lookups.
    """
    
    def __init__(self, dictionary_path: str = None, max_edit_distance: int = 2):
        """
        Initialize spell checker.
        
        Args:
            dictionary_path: Path to Vietnamese word dictionary (JSONL format)
            max_edit_distance: Maximum edit distance for suggestions (default: 2)
        """
        self.max_edit_distance = max_edit_distance
        self.word_frequency: Dict[str, int] = {}
        self.deletes: Dict[str, Set[str]] = defaultdict(set)
        
        if dictionary_path and os.path.exists(dictionary_path):
            self._load_dictionary(dictionary_path)
    
    def _load_dictionary(self, path: str):
        """Load Vietnamese word dictionary and build SymSpell index."""
        print(f"[INFO] Loading dictionary from {path}...")
        
        try:
            with open(path, 'r', encoding='utf8') as f:
                for line in f:
                    try:
                        obj = json.loads(line.strip())
                        word = obj.get('text', '').strip().lower()
                        freq = obj.get('frequency', 1)
                        
                        if word and len(word) >= 2:
                            self.word_frequency[word] = freq
                            self._create_deletes(word)
                    except:
                        continue
            
            print(f"[INFO] Loaded {len(self.word_frequency)} words")
            print(f"[INFO] Created {len(self.deletes)} delete variations")
        except Exception as e:
            print(f"[ERROR] Failed to load dictionary: {e}")
    
    def _create_deletes(self, word: str):
        """
        Create all delete variations of a word up to max_edit_distance.
        
        This is the core of SymSpell: pre-compute all possible deletions.
        """
        # Add the word itself
        self.deletes[word].add(word)
        
        # Generate all deletions
        edits = {word}
        for _ in range(self.max_edit_distance):
            new_edits = set()
            for edit in edits:
                for i in range(len(edit)):
                    delete = edit[:i] + edit[i+1:]
                    if delete:
                        new_edits.add(delete)
                        self.deletes[delete].add(word)
            edits = new_edits
    
    @lru_cache(maxsize=10000)
    def lookup(self, word: str, max_candidates: int = 5) -> List[Tuple[str, int, int]]:
        """
        Find spelling suggestions for a word.
        
        Args:
            word: Input word
            max_candidates: Maximum number of suggestions to return
            
        Returns:
            List of (suggested_word, edit_distance, frequency) tuples,
            sorted by edit distance then frequency
        """
        word_lower = word.lower()
        
        # If word is in dictionary, return it
        if word_lower in self.word_frequency:
            return [(word_lower, 0, self.word_frequency[word_lower])]
        
        # Find all candidates within edit distance
        candidates: Dict[str, Tuple[int, int]] = {}  # word -> (distance, freq)
        
        # Check all delete variations
        for i in range(self.max_edit_distance + 1):
            deletes = self._get_deletes(word_lower, i)
            for delete in deletes:
                if delete in self.deletes:
                    for suggestion in self.deletes[delete]:
                        if suggestion not in candidates:
                            distance = self._edit_distance(word_lower, suggestion)
                            if distance <= self.max_edit_distance:
                                freq = self.word_frequency.get(suggestion, 0)
                                candidates[suggestion] = (distance, freq)
        
        # Sort by distance (ascending) then frequency (descending)
        sorted_candidates = sorted(
            [(word, dist, freq) for word, (dist, freq) in candidates.items()],
            key=lambda x: (x[1], -x[2])
        )
        
        return sorted_candidates[:max_candidates]
    
    def _get_deletes(self, word: str, num_deletes: int) -> Set[str]:
        """Generate all possible deletions of a word."""
        if num_deletes == 0:
            return {word}
        
        deletes = {word}
        current_level = {word}
        
        for _ in range(num_deletes):
            next_level = set()
            for w in current_level:
                for i in range(len(w)):
                    delete = w[:i] + w[i+1:]
                    if delete:
                        next_level.add(delete)
                        deletes.add(delete)
            current_level = next_level
        
        return deletes
    
    @staticmethod
    def _edit_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) > len(s2):
            s1, s2 = s2, s1
        
        if len(s1) == 0:
            return len(s2)
        
        previous_row = range(len(s1) + 1)
        
        for i, c2 in enumerate(s2):
            current_row = [i + 1]
            for j, c1 in enumerate(s1):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def is_correct(self, word: str) -> bool:
        """Check if a word is in the dictionary."""
        return word.lower() in self.word_frequency
    
    def correct_word(self, word: str) -> str:
        """
        Correct a single word.
        
        Args:
            word: Input word
            
        Returns:
            Corrected word (or original if no good suggestion found)
        """
        # Skip very short words
        if len(word) <= 2:
            return word
        
        # If already correct, return as-is
        if self.is_correct(word):
            return word
        
        # Get suggestions
        suggestions = self.lookup(word, max_candidates=1)
        
        if suggestions:
            best_word, distance, _ = suggestions[0]
            # Only correct if edit distance is reasonable
            if distance <= self.max_edit_distance:
                return best_word
        
        return word
    
    def correct_text(self, text: str) -> str:
        """
        Correct all words in a text.
        
        Args:
            text: Input text
            
        Returns:
            Corrected text
        """
        import re
        
        # Find all Vietnamese words
        # Vietnamese characters: a-z, à-ỹ
        words = re.findall(r'[\wÀ-ỹ]+', text)
        
        corrected_words = []
        for word in words:
            corrected = self.correct_word(word)
            corrected_words.append(corrected)
        
        return ' '.join(corrected_words)


# Global instance (lazy loaded)
_spell_checker_instance: Optional[SymSpellChecker] = None


def get_spell_checker(config_path: str = "config.json") -> SymSpellChecker:
    """
    Get singleton spell checker instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        SymSpellChecker instance
    """
    global _spell_checker_instance
    
    if _spell_checker_instance is None:
        # Load config
        dict_path = "data/processed/vietnamese_words.txt"  # default
        max_distance = 2  # default
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf8') as f:
                    config = json.load(f)
                    dict_path = config.get('paths', {}).get('vietnamese_dictionary', dict_path)
                    max_distance = config.get('post_processing', {}).get('spell_checker', {}).get('max_edit_distance', max_distance)
            except:
                pass
        
        _spell_checker_instance = SymSpellChecker(
            dictionary_path=dict_path,
            max_edit_distance=max_distance
        )
    
    return _spell_checker_instance


def correct_vietnamese_text_fast(text: str) -> str:
    """
    Fast Vietnamese spell correction using SymSpell.
    
    Args:
        text: Input text
        
    Returns:
        Corrected text
    """
    checker = get_spell_checker()
    return checker.correct_text(text)


if __name__ == "__main__":
    # Test the spell checker
    checker = SymSpellChecker("data/processed/vietnamese_words.txt", max_edit_distance=2)
    
    test_cases = [
        "giang day tieng viet",
        "sinh vien hoc tap",
        "truong dai hoc dien luc",
        "tir ngay mai",
        "viêc quan trong",
    ]
    
    print("\\n=== SymSpell Spell Checker Test ===\\n")
    for test in test_cases:
        corrected = checker.correct_text(test)
        print(f"Original:  {test}")
        print(f"Corrected: {corrected}")
        print()
