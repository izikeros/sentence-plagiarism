import time
from unittest.mock import mock_open, patch

import pytest
from bs4 import BeautifulSoup

from sentence_plagiarism.visualization.models import PlagiarismMatch
from sentence_plagiarism.visualization.text_processing import split_text_into_segments


def _offset_helper(content, plagiarized_text):
    # Find the starting offset of the plagiarized word
    start_offset = content.find(plagiarized_text)

    # Calculate the ending offset (last character of the plagiarized text)
    if start_offset != -1:
        end_offset = start_offset + len(plagiarized_text) - 1
    else:
        raise ValueError("plagiarized text not found in content")
    return start_offset, end_offset


class TestSplitTextIntoSegments:
    @pytest.fixture
    def empty_content(self):
        return ""

    @pytest.fixture
    def sample_content(self):
        return "This is a test document with some plagiarized content in the middle and at the end."

    #           01234567890123456789012345678901234567890123456789012345678901234567890123456789012
    #           0         1         2         3         4         5         6         7         8

    @pytest.fixture
    def sample_matches(self):
        # "This is a test document with some plagiarized content in the middle and at the end."
        #  01234567890123456789012345678901234567890123456789012345678901234567890123456789012
        #  0         1         2         3         4         5         6         7         8
        return [
            PlagiarismMatch(
                input_sentence="plagiarized content ",
                input_start_pos=34,
                input_end_pos=53,
                reference_sentence="plagiarized content",
                reference_start_pos=10,
                reference_end_pos=28,
                reference_document="reference1.md",
                similarity_score=0.95,
            ),
            PlagiarismMatch(
                input_sentence="at the end.",
                input_start_pos=72,
                input_end_pos=82,
                reference_sentence="at the end",
                reference_start_pos=50,
                reference_end_pos=59,
                reference_document="reference2.md",
                similarity_score=0.85,
            ),
        ]

    def test_empty_content_no_matches(self, empty_content):
        """Test with empty content and no matches should return no segments."""
        result = split_text_into_segments(empty_content, [])
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
        # "This is a test document with some plagiarized content in the middle and at the end."
        #  01234567890123456789012345678901234567890123456789012345678901234567890123456789012
        #  0         1         2         3         4         5         6         7         8

        # Check first segment (clean text)
        assert result[0].start == 0
        assert result[0].end == 33
        assert result[0].text == "This is a test document with some "
        assert result[0].matches == []

        # Check second segment (plagiarized)
        assert result[1].start == 44
        assert result[1].end == 53
        assert result[1].text == "plagiarized content "
        assert len(result[1].matches) == 1
        assert result[1].matches[0] == sample_matches[0]

        # Check third segment (clean text)
        assert result[2].start == 54
        assert result[2].end == 71
        assert result[2].text == "in the middle and "
        assert result[2].matches == []

        # Check fourth segment (plagiarized)
        assert result[3].start == 72
        assert result[3].end == 82
        assert result[3].text == "at the end."
        assert len(result[3].matches) == 1
        assert result[3].matches[0] == sample_matches[1]

    def test_overlapping_matches(self, sample_content):
        """Test with overlapping plagiarism matches."""
        # "This is a test document with some plagiarized content in the middle and at the end."
        #  01234567890123456789012345678901234567890123456789012345678901234567890123456789012
        #  0         1         2         3         4         5         6         7         8
        overlapping_matches = [
            PlagiarismMatch(
                input_sentence="test document with some ",
                input_start_pos=10,
                input_end_pos=33,
                reference_sentence="test document with some",
                reference_start_pos=5,
                reference_end_pos=28,
                reference_document="ref1.md",
                similarity_score=0.9,
            ),
            PlagiarismMatch(
                input_sentence="with some plagiarized ",
                input_start_pos=24,
                input_end_pos=45,
                reference_sentence="with some plagiarized",
                reference_start_pos=10,
                reference_end_pos=31,
                reference_document="ref2.md",
                similarity_score=0.8,
            ),
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
        assert overlap_segment.start == 24
        assert overlap_segment.end == 33
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
            ),
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
            ),
        ]

        result = split_text_into_segments(content, adjacent_matches)

        assert len(result) == 4  # Start, first match, second match, end
        assert result[0].start == 0
        assert result[0].end == 7
        assert result[2].start == 8
        assert result[3].end == 29

    def test_malformed_position_data(self):
        """Test with malformed position data where end < start."""
        content = "This is a test for malformed position data"

        # Create a match with end position less than start position
        with pytest.raises(
            ValueError, match="Input sentence length.*doesn't match position range"
        ):
            PlagiarismMatch(
                input_sentence="malformed",
                input_start_pos=20,
                input_end_pos=10,  # Intentionally set end < start
                reference_sentence="malformed",
                reference_start_pos=5,
                reference_end_pos=14,
                reference_document="reference.md",
                similarity_score=0.9,
            )

    def test_matches_beyond_text_boundaries(self):
        """Test with matches that have positions beyond the content boundaries."""

        # Should raise ValueError due to mismatch between sentence length and position range
        with pytest.raises(
            ValueError, match="Input sentence length.*doesn't match position range"
        ):
            PlagiarismMatch(
                input_sentence="text example plus more",
                input_start_pos=6,
                input_end_pos=30,
                reference_sentence="text example plus more",
                reference_start_pos=5,
                reference_end_pos=29,
                reference_document="ref.md",
                similarity_score=0.9,
            )

    def test_large_text_performance(self):
        """Test performance with very long text and many matches."""
        # Create a long text with 1000 words
        long_text = " ".join(["word" + str(i) for i in range(1000)])
        assert len(long_text.split()) == 1000

        # Create 100 non-overlapping matches
        matches = []
        for i in range(0, 900, 10):  # Create matches every 10 words
            start_pos = i * 5  # Approximate character position
            match_text = " ".join(
                ["word" + str(i + j) for j in range(5)]
            )  # 5-word match
            end_pos = start_pos + len(match_text)

            matches.append(
                PlagiarismMatch(
                    input_sentence=match_text,
                    input_start_pos=start_pos,
                    input_end_pos=end_pos,
                    reference_sentence=match_text,
                    reference_start_pos=0,  # Reference position doesn't matter for this test
                    reference_end_pos=len(match_text),
                    reference_document=f"ref{i//100}.md",  # Create multiple reference documents
                    similarity_score=0.8 + (i % 20) / 100,  # Vary similarity scores
                )
            )

        # Test that segmentation completes without errors and returns expected structure
        start_time = time.time()
        result = split_text_into_segments(long_text, matches)
        end_time = time.time()

        # Assert the function completes in reasonable time (adjust threshold as needed)
        assert end_time - start_time < 2.0, "Segmentation took too long"

        # Should have 2 * number_of_matches + 1 segments in the non-overlapping case
        expected_segments = 2 * len(matches)
        assert len(result) == expected_segments

        # Check integrity of segments
        total_length = sum(len(segment.text) for segment in result)
        assert total_length == len(long_text)


class TestVisualizationRendering:
    """Tests for the HTML rendering functionality of the plagiarism visualizer."""

    def test_create_html_with_highlights(self):
        """Test that HTML is properly generated with highlight spans."""
        from sentence_plagiarism.visualization.html_generator import (
            create_html_with_highlights_md,
        )
        from sentence_plagiarism.visualization.visualization_utils import (
            generate_document_colors,
        )

        content = "This is a paragraph with some plagiarized text inside it."
        matches = [
            PlagiarismMatch(
                input_sentence="plagiarized text",
                input_start_pos=30,
                input_end_pos=46,
                reference_sentence="plagiarized text",
                reference_start_pos=5,
                reference_end_pos=21,
                reference_document="document1.md",
                similarity_score=0.9,
            )
        ]

        # Generate colors for reference documents
        doc_colors = generate_document_colors(matches)

        # Generate HTML with highlights
        html_content = create_html_with_highlights_md(content, matches, doc_colors)

        # Parse the HTML to check the structure
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all highlighted spans
        highlighted_spans = soup.find_all("span", class_="plagiarized")

        # Should have exactly one highlighted span
        assert len(highlighted_spans) == 1

        # Check the content of the span
        span = highlighted_spans[0]
        assert span.text == "plagiarized text"

        # Check the class and data attributes
        assert "plagiarized" in span["class"]
        assert "plag-doc-document1_md" in span["class"]
        assert "data-references" in span.attrs
        assert "document1.md" in span["data-references"]
        assert "data-similarity" in span.attrs
        assert float(span["data-similarity"]) > 0.8

    def test_complete_html_generation(self):
        """Test the complete HTML report generation process."""
        from sentence_plagiarism.visualization.html_generator import generate_final_html
        from sentence_plagiarism.visualization.visualization_utils import (
            generate_document_colors,
        )

        # Mock the internal template and file operations
        html_content = (
            "<p>Test content with <span class='plagiarized'>highlighted text</span></p>"
        )
        matches = [
            PlagiarismMatch(
                input_sentence="highlighted text",
                input_start_pos=20,
                input_end_pos=36,
                reference_sentence="highlighted text",
                reference_start_pos=5,
                reference_end_pos=21,
                reference_document="document1.md",
                similarity_score=0.9,
            )
        ]

        doc_colors = generate_document_colors(matches)

        # Mock template file reading
        template_content = """
        <!DOCTYPE html>
        <html>
        <head><title>{title}</title></head>
        <body>
            <h1>{subtitle}</h1>
            <div class="controls">{filter_buttons}</div>
            <div class="legend">{legend_items}</div>
            <style>{document_colors}</style>
            <div class="content">{content}</div>
        </body>
        </html>
        """

        with patch("builtins.open", mock_open(read_data=template_content)):
            with patch("pathlib.Path.mkdir"):
                with patch("shutil.copy"):
                    # Generate the final HTML
                    final_html = generate_final_html(
                        html_content,
                        doc_colors,
                        matches,
                        "test_input.md",
                        "test_output.html",
                    )

                    # Verify the final HTML structure
                    assert "test_input.md" in final_html
                    assert "document1.md" in final_html
                    assert "highlighted text" in final_html

                    # Check for required components
                    assert "filter_buttons" in template_content
                    assert "legend_items" in template_content
                    assert "document_colors" in template_content
                    assert "content" in template_content

                    # Validate the HTML structure
                    soup = BeautifulSoup(final_html, "html.parser")
                    assert soup.title is not None
                    assert (
                        soup.find("div", class_="controls") is not None
                        or "controls" in final_html
                    )
                    assert (
                        soup.find("div", class_="legend") is not None
                        or "legend" in final_html
                    )
                    assert (
                        soup.find("div", class_="content") is not None
                        or "content" in final_html
                    )
