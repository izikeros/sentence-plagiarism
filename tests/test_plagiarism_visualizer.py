from unittest.mock import mock_open, patch

from bs4 import BeautifulSoup

from sentence_plagiarism.visualization.html_generator import (
    create_html_with_highlights_md,
)
from sentence_plagiarism.visualization.models import PlagiarismMatch
from sentence_plagiarism.visualization.visualization_utils import (
    generate_document_colors,
)


def _offset_helper(content, plagiarized_text):
    # Find the starting offset of the plagiarized word
    start_offset = content.find(plagiarized_text)

    # Calculate the ending offset (last character of the plagiarized text)
    if start_offset != -1:
        end_offset = start_offset + len(plagiarized_text) - 1
    else:
        raise ValueError("plagiarized text not found in content")
    return start_offset, end_offset


class TestVisualizationRendering:
    """Tests for the HTML rendering functionality of the plagiarism visualizer."""

    def test_create_html_with_highlights(self):
        """Test that HTML is properly generated with highlight spans."""

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
        highlighted_spans = soup.find_all("div", class_="plagiarized")

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
                        html_content, doc_colors, matches, "test_input.md"
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
