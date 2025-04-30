import pytest

from sentence_plagiarism.similarity import (
    cosine_similarity,
    jaccard_similarity,
    jaro_similarity,
    jaro_winkler_similarity,
    overlap_similarity,
    sorensen_dice_similarity,
    tversky_similarity,
)


class TestSimilarityMetrics:
    def test_jaccard_similarity(self):
        set1 = {"a", "b", "c"}
        set2 = {"b", "c", "d"}
        assert jaccard_similarity(set1, set2) == 2 / 4

    def test_cosine_similarity(self):
        set1 = {"a", "b", "c"}
        set2 = {"b", "c", "d"}
        assert cosine_similarity(set1, set2) == 2 / (3 * 3)

    def test_sorensen_dice_similarity(self):
        set1 = {"a", "b", "c"}
        set2 = {"b", "c", "d"}
        assert sorensen_dice_similarity(set1, set2) == 2 * 2 / (3 + 3)

    def test_overlap_similarity(self):
        set1 = {"a", "b", "c"}
        set2 = {"b", "c", "d"}
        assert overlap_similarity(set1, set2) == 2 / 3

    def test_tversky_similarity(self):
        set1 = {"a", "b", "c"}
        set2 = {"b", "c", "d"}
        assert tversky_similarity(set1, set2, alpha=0.5) == 2 / (2 + 0.5 * 1 + 0.5 * 1)

    @pytest.mark.skip(reason="Need to verify this test")
    def test_jaro_similarity(self):
        s1 = "martha"
        s2 = "marhta"
        assert round(jaro_similarity(s1, s2), 4) == 0.9444

    @pytest.mark.skip(reason="Need to verify this test")
    def test_jaro_winkler_similarity(self):
        s1 = "martha"
        s2 = "marhta"
        assert round(jaro_winkler_similarity(s1, s2, p=0.1), 4) == 0.9611
