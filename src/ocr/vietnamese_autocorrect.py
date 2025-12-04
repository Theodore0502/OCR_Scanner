import regex as re

# Load dictionary
with open("data/processed/vietnamese_words.txt", "r", encoding="utf8") as f:
    VIET_DICT = set([line.strip().lower() for line in f])


def levenshtein(a, b):
    """Simple Levenshtein distance"""
    if len(a) > len(b):
        a, b = b, a

    dp = range(len(a) + 1)

    for i in range(1, len(b) + 1):
        new_dp = [i]
        for j in range(1, len(a) + 1):
            cost = 0 if a[j - 1] == b[i - 1] else 1
            new_dp.append(min(
                new_dp[-1] + 1,
                dp[j] + 1,
                dp[j - 1] + cost
            ))
        dp = new_dp

    return dp[-1]


def autocorrect_word(word):
    w = word.lower()
    if w in VIET_DICT:
        return word

    # too short → skip
    if len(w) <= 2:
        return word

    # find best match
    best = None
    best_dist = 9e9

    for vocab in VIET_DICT:
        d = levenshtein(w, vocab)
        if d < best_dist:
            best = vocab
            best_dist = d

        if best_dist == 0:
            break

    return best if best else word


def autocorrect_text(text):
    """
    Apply autocorrect to entire text block.
    """
    tokens = re.findall(r"[\wÀ-ỹ]+", text)

    fixed = []
    for t in tokens:
        fixed.append(autocorrect_word(t))

    return " ".join(fixed)
