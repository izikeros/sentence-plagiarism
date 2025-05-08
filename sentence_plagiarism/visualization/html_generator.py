import logging
import re
import shutil
from pathlib import Path

import markdown

from sentence_plagiarism.visualization.models import PlagiarismMatch
from sentence_plagiarism.visualization.text_processing import (
    clean_text,
    split_text_into_segments,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_html_with_highlights_md(
    content: str, plagiarism_matches: list[PlagiarismMatch], doc_colors: dict[str, str]
) -> str:
    logger.debug("Starting create_html_with_highlights_md")
    logger.debug("Content length: %d", len(content))
    logger.debug("Number of plagiarism matches: %d", len(plagiarism_matches))
    """Create HTML content with plagiarism highlights."""
    segments = split_text_into_segments(content, plagiarism_matches)
    # TODO: the number of segments is not equal to the number of matches - it is greater - why?
    # Generate HTML with appropriate divs for highlights
    html_content = ""
    num_segments = len(segments)
    for idx, segment in enumerate(segments):
        txt = segment.text
        if not segment.matches:
            # Regular text, no plagiarism
            text_cleaned = clean_text(txt)
            html_content += text_cleaned
            logger.debug(f"No matches in segment, adding text {text_cleaned}")
        else:
            # Plagiarized text
            class_names = []
            doc_ids = []
            similarity_sum = 0

            num_matches = len(segment.matches)
            for match in segment.matches:
                doc_id = re.sub(r"[^a-zA-Z0-9]", "_", match.reference_document)
                class_names.append(f"plag-doc-{doc_id}")
                doc_ids.append(doc_id)
                similarity_sum += match.similarity_score

            # Average similarity for overlapping segments
            avg_similarity = similarity_sum / num_matches
            opacity = min(
                0.3 + avg_similarity * 0.7, 1.0
            )  # Scale opacity based on similarity

            # Build data attributes for tooltip
            data_attrs = {
                "data-references": ", ".join(
                    m.reference_document for m in segment.matches
                ),
                "data-similarity": f"{avg_similarity:.2f}",
            }

            # Create attributes string
            attrs = f'class="plagiarized {" ".join(class_names)}" '
            attrs += " ".join(f'{k}="{v}"' for k, v in data_attrs.items())

            txt_clean = clean_text(txt)
            new_html_content = f"<div {attrs}>{txt_clean}</div>"

            logger.debug(f"Adding plagiarized segment: {new_html_content}")
            html_content += new_html_content

    # Convert Markdown to HTML, preserving our highlight divs
    html = markdown.markdown(html_content, extensions=["tables", "fenced_code"])
    logger.debug(f"Generated HTML content length: {len(html)}")
    return html


def get_document_specific_css(doc_colors: dict[str, str]) -> str:
    """Generate CSS for document-specific colors."""
    return "\n".join(
        f".plag-doc-{re.sub(r'[^a-zA-Z0-9]', '_', doc)} {{ background-color: {color}; }}"
        for doc, color in doc_colors.items()
    )


def generate_filter_buttons(reference_documents: set[str]) -> str:
    """Generate HTML for filter buttons."""
    buttons = '<button id="show-all-btn" class="control-btn active">Show All</button>'
    buttons += '<button id="hide-all-btn" class="control-btn">Hide All</button>'

    for doc in sorted(reference_documents):
        doc_id = re.sub(r"[^a-zA-Z0-9]", "_", doc)
        doc_name = Path(doc).name
        buttons += f'<button class="filter-btn control-btn" data-doc="{doc_id}">{doc_name}</button>'

    return buttons


def generate_legend_items(doc_colors: dict[str, str]) -> str:
    """Generate HTML for legend items."""
    items = ""
    for doc, color in doc_colors.items():
        doc_id = re.sub(r"[^a-zA-Z0-9]", "_", doc)
        doc_name = Path(doc).name
        items += f'<div class="legend-item"><span class="color-box" style="background-color: {color};"></span>{doc_name}</div>'
    return items


def generate_final_html(
    html_content: str,
    doc_colors: dict[str, str],
    plagiarism_matches: list[PlagiarismMatch],
    input_file: str,
    output_path: str,
) -> str:
    """Generate the final self-contained HTML file with styling and JavaScript."""
    # Get unique list of reference documents for filter controls
    reference_documents = {match.reference_document for match in plagiarism_matches}

    # Create filter buttons HTML
    filter_buttons = generate_filter_buttons(reference_documents)

    # Create document legend
    legend_items = generate_legend_items(doc_colors)

    # Create document-specific CSS
    document_colors = get_document_specific_css(doc_colors)

    # Get template directory path
    template_dir = Path(__file__).parent / "templates"

    # Get input filename for title
    input_filename = Path(input_file).name

    # Read HTML template
    with open(template_dir / "plagiarism_report_template.html") as f:
        template = f.read()

    # input file without extension and without the path
    input_filename_stem = Path(input_file).stem

    # Fill in the template
    output_html = template.format(
        title=input_filename_stem,
        subtitle=input_filename_stem,
        subsubtitle="Plagiarism Report",
        filter_buttons=filter_buttons,
        legend_items=legend_items,
        document_colors=document_colors,
        content=html_content,
    )

    # Create output directory if it doesn't exist
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy CSS and JS files to the output directory
    css_path = template_dir / "plagiarism_report.css"
    js_path = template_dir / "plagiarism_report.js"

    shutil.copy(css_path, output_dir / "plagiarism_report.css")
    shutil.copy(js_path, output_dir / "plagiarism_report.js")

    return output_html
