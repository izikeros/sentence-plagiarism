def jaccard_similarity(set1, set2):
    """Compute the Jaccard similarity between two sets"""
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union != 0 else 0


# other similarity metrics for the text comparison
def cosine_similarity(set1, set2):
    """Compute the cosine similarity between two sets"""
    intersection = len(set1 & set2)
    return intersection / (len(set1) * len(set2))


def sorensen_dice_similarity(set1, set2):
    """Compute the Sorensen-Dice similarity between two sets"""
    intersection = len(set1 & set2)
    return 2 * intersection / (len(set1) + len(set2))

def overlap_similarity(set1, set2):
    """Compute the overlap similarity between two sets"""
    intersection = len(set1 & set2)
    return intersection / min(len(set1), len(set2))


def tversky_similarity(set1, set2, alpha=0.5):
    """Compute the Tversky similarity between two sets"""
    intersection = len(set1 & set2)
    return intersection / (
        intersection
        + alpha * (len(set1) - intersection)
        + (1 - alpha) * (len(set2) - intersection)
    )


def _jaro_similarity(s1, s2):
    len_s1, len_s2 = len(s1), len(s2)
    match_distance = max(len_s1, len_s2) // 2 - 1

    common_chars_s1 = []
    common_chars_s2 = []

    for i, char in enumerate(s1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len_s2)

        if char in s2[start:end]:
            common_chars_s1.append(char)
            common_chars_s2.append(s2[start:end][s2[start:end].index(char)])

    m = len(common_chars_s1)
    if m == 0:
        return 0.0

    transpositions = sum(c1 != c2 for c1, c2 in zip(common_chars_s1, common_chars_s2)) // 2
    jaro_similarity = (m / len_s1 + m / len_s2 + (m - transpositions) / m) / 3
    return jaro_similarity


def jaro_winkler_similarity(s1, s2, p=0.1):
    jaro_sim = _jaro_similarity(s1, s2)
    common_prefix_len = 0

    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 == c2:
            common_prefix_len += 1
        else:
            break

    jaro_winkler_sim = jaro_sim + (common_prefix_len * p * (1 - jaro_sim))
    return jaro_winkler_sim
