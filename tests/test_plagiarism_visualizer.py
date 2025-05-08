import pytest

from sentence_plagiarism.plagiarism_visualizer import (
    PlagiarismMatch,
    split_text_into_segments,
)


class TestSplitTextIntoSegments:
    @pytest.fixture
    def empty_content(self):
        return ""

    @pytest.fixture
    def sample_content(self):
        return "This is a test document with some plagiarized content in the middle and at the end."

    @pytest.fixture
    def sample_matches(self):
        return [
            PlagiarismMatch(
                input_sentence="plagiarized content",
                input_start_pos=28,
                input_end_pos=47,
                reference_sentence="plagiarized content",
                reference_start_pos=10,
                reference_end_pos=29,
                reference_document="reference1.md",
                similarity_score=0.95,
            ),
            PlagiarismMatch(
                input_sentence="at the end",
                input_start_pos=61,
                input_end_pos=72,
                reference_sentence="at the end",
                reference_start_pos=50,
                reference_end_pos=61,
                reference_document="reference2.md",
                similarity_score=0.85,
            )
        ]

    def test_empty_content_no_matches(self, empty_content):
        """Test with empty content and no matches should return no segments."""
        result = split_text_into_segments(empty_content, [])
        assert result == []

    def test_empty_content_with_matches(self, empty_content, sample_matches):
        """Test with empty content but with matches should return no segments."""
        result = split_text_into_segments(empty_content, sample_matches)
        assert result == []

    def test_content_without_matches(self, sample_content):
        """Test with content but no matches should return a single segment."""
        result = split_text_into_segments(sample_content, [])
        assert len(result) == 1
        assert result[0].start == 0
        assert result[0].end == len(sample_content)
        assert result[0].text == sample_content
        assert result[0].matches == []

    def test_content_with_matches(self, sample_content, sample_matches):
        """Test with content and matches should split correctly into segments."""
        result = split_text_into_segments(sample_content, sample_matches)

        # Should have 5 segments:
        # 1. before first match
        # 2. first match
        # 3. between matches
        # 4. second match
        # 5. after second match (which is empty since match is at end)
        assert len(result) == 5

        # Check first segment (clean text)
        assert result[0].start == 0
        assert result[0].end == 28
        assert result[0].text == "This is a test document with "
        assert result[0].matches == []

        # Check second segment (plagiarized)
        assert result[1].start == 28
        assert result[1].end == 47
        assert result[1].text == "plagiarized content"
        assert len(result[1].matches) == 1
        assert result[1].matches[0] == sample_matches[0]

        # Check third segment (clean text)
        assert result[2].start == 47
        assert result[2].end == 61
        assert result[2].text == " in the middle and "
        assert result[2].matches == []

        # Check fourth segment (plagiarized)
        assert result[3].start == 61
        assert result[3].end == 72
        assert result[3].text == "at the end."
        assert len(result[3].matches) == 1
        assert result[3].matches[0] == sample_matches[1]

    def test_overlapping_matches(self, sample_content):
        """Test with overlapping plagiarism matches."""
        overlapping_matches = [
            PlagiarismMatch(
                input_sentence="test document with some",
                input_start_pos=10,
                input_end_pos=34,
                reference_sentence="test document with some",
                reference_start_pos=5,
                reference_end_pos=29,
                reference_document="ref1.md",
                similarity_score=0.9,
            ),
            PlagiarismMatch(
                input_sentence="with some plagiarized",
                input_start_pos=22,
                input_end_pos=44,
                reference_sentence="with some plagiarized",
                reference_start_pos=10,
                reference_end_pos=32,
                reference_document="ref2.md",
                similarity_score=0.8,
            )
        ]

        result = split_text_into_segments(sample_content, overlapping_matches)

        # Should have 4 segments:
        # 1. Before any match
        # 2. First match only
        # 3. Both matches
        # 4. Second match only
        # 5. After all matches
        assert len(result) == 5

        # Check overlap segment
        overlap_segment = result[2]
        assert overlap_segment.start == 22
        assert overlap_segment.end == 34
        assert overlap_segment.text == "with some"
        assert len(overlap_segment.matches) == 2
        assert overlapping_matches[0] in overlap_segment.matches
        assert overlapping_matches[1] in overlap_segment.matches

    def test_match_at_start(self, sample_content):
        """Test with a match at the beginning of content."""
        start_match = [
            PlagiarismMatch(
                input_sentence="This is",
                input_start_pos=0,
                input_end_pos=7,
                reference_sentence="This is",
                reference_start_pos=0,
                reference_end_pos=7,
                reference_document="ref.md",
                similarity_score=0.9,
            )
        ]

        result = split_text_into_segments(sample_content, start_match)

        assert len(result) == 2
        assert result[0].start == 0
        assert result[0].end == 7
        assert result[0].text == "This is"
        assert len(result[0].matches) == 1
        assert result[0].matches[0] == start_match[0]

    def test_match_exactly_at_end(self):
        """Test with a match that ends exactly at the end of the content."""
        content = "This is a test."
        end_match = [
            PlagiarismMatch(
                input_sentence="a test.",
                input_start_pos=8,
                input_end_pos=15,
                reference_sentence="a test.",
                reference_start_pos=8,
                reference_end_pos=15,
                reference_document="ref.md",
                similarity_score=0.9,
            )
        ]

        result = split_text_into_segments(content, end_match)

        assert len(result) == 2
        assert result[1].start == 8
        assert result[1].end == 15
        assert result[1].text == "a test."
        assert len(result[1].matches) == 1
        assert result[1].matches[0] == end_match[0]

    def test_multiple_matches_same_position(self):
        """Test with multiple matches at the same position."""
        content = "Duplicate text here"
        same_pos_matches = [
            PlagiarismMatch(
                input_sentence="Duplicate text",
                input_start_pos=0,
                input_end_pos=14,
                reference_sentence="Duplicate text",
                reference_start_pos=0,
                reference_end_pos=14,
                reference_document="ref1.md",
                similarity_score=0.9,
            ),
            PlagiarismMatch(
                input_sentence="Duplicate text",
                input_start_pos=0,
                input_end_pos=14,
                reference_sentence="Duplicate text",
                reference_start_pos=5,
                reference_end_pos=19,
                reference_document="ref2.md",
                similarity_score=0.85,
            )
        ]

        result = split_text_into_segments(content, same_pos_matches)

        assert len(result) == 2
        assert result[0].start == 0
        assert result[0].end == 14
        assert result[0].text == "Duplicate text"
        assert len(result[0].matches) == 2
        assert same_pos_matches[0] in result[0].matches
        assert same_pos_matches[1] in result[0].matches

    def test_adjacent_matches(self):
        """Test with adjacent matches without gaps between them."""
        content = "This is adjacent matches test"
        adjacent_matches = [
            PlagiarismMatch(
                input_sentence="This is",
                input_start_pos=0,
                input_end_pos=7,
                reference_sentence="This is",
                reference_start_pos=0,
                reference_end_pos=7,
                reference_document="ref1.md",
                similarity_score=0.9,
            ),
            PlagiarismMatch(
                input_sentence="adjacent matches",
                input_start_pos=8,
                input_end_pos=24,
                reference_sentence="adjacent matches",
                reference_start_pos=5,
                reference_end_pos=21,
                reference_document="ref2.md",
                similarity_score=0.8,
            )
        ]

        result = split_text_into_segments(content, adjacent_matches)

        assert len(result) == 4  # Start, first match, second match, end
        assert result[0].start == 0
        assert result[0].end == 7
        assert result[2].start == 8
        assert result[3].end == 24
