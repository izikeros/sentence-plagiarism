#!/usr/bin/env python3
"""
Plagiarism Visualizer - Converts a Markdown document with plagiarism data
into an interactive HTML report highlighting plagiarized content.

Usage:
   python plagiarism_visualizer.py --input document.md --plagiarism-data results.json --output report.html

TODO:
- add tested document name in the title and keep "Plagiarism Report" as subtitle
- add possibility to fold/unfold sections without any plagiarism - display (on/off) only plagiarised sentences with some context - like 2 sentences before and after
- simplify cli API - add default file names. when user provides input filename assume that JSON and HTML files will be created with the same name but different extensions
"""

import argparse
import json
import random
import re
import sys
import shutil
from pathlib import Path
from typing import NamedTuple
from bs4 import BeautifulSoup
import markdown

import logging

from bs4 import NavigableString

logging.basicConfig(level=logging.DEBUG)

from dataclasses import dataclass


@dataclass
class PlagiarismMatch:
    """Represents a single plagiarism match."""

    input_sentence: str
    input_start_pos: int
    input_end_pos: int
    reference_sentence: str
    reference_start_pos: int
    reference_end_pos: int
    reference_document: str
    similarity_score: float

    def __post_init__(self):
        """Validate that sentence lengths match position ranges."""
        # Validate input sentence
        input_length = len(self.input_sentence)
        input_range = self.input_end_pos - self.input_start_pos

        if input_length != input_range:
            raise ValueError(
                f"Input sentence length ({input_length}) doesn't match position range "
                f"({input_range}): {self.input_sentence}"
            )

        # Validate reference sentence
        ref_length = len(self.reference_sentence)
        ref_range = self.reference_end_pos - self.reference_start_pos

        if ref_length != ref_range:
            raise ValueError(
                f"Reference sentence length ({ref_length}) doesn't match position range "
                f"({ref_range}): {self.reference_sentence}"
            )

        # Validate similarity score is between 0 and 1
        if not 0 <= self.similarity_score <= 1:
            raise ValueError(
                f"Similarity score must be between 0 and 1, got {self.similarity_score}"
            )


class SegmentType(NamedTuple):
    """Represents a segment of text with its plagiarism status."""

    start: int
    end: int
    text: str
    matches: list[PlagiarismMatch]


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate HTML visualization of plagiarism in Markdown documents"
    )
    parser.add_argument("--input", required=True, help="Input Markdown file")
    parser.add_argument(
        "--plagiarism-data", required=True, help="JSON file with plagiarism data"
    )
    parser.add_argument("--output", required=True, help="Output HTML file")
    return parser.parse_args()


def load_files(markdown_path: str, json_path: str) -> tuple[str, list[PlagiarismMatch]]:
    """Load and validate the input files."""
    try:
        with open(markdown_path, encoding="utf-8") as f:
            markdown_content = f.read()
    except OSError as e:
        sys.exit(f"Error reading Markdown file: {e}")

    try:
        with open(json_path, encoding="utf-8") as f:
            plagiarism_data = json.load(f)

        if "plagiarism_results" not in plagiarism_data:
            # Try to handle a direct list of results
            if isinstance(plagiarism_data, list):
                results = plagiarism_data
            else:
                # Use the first key found, assuming it contains the results
                first_key = next(iter(plagiarism_data))
                results = plagiarism_data[first_key]
        else:
            results = plagiarism_data["plagiarism_results"]

        plagiarism_matches = [
            PlagiarismMatch(
                input_sentence=match["input_sentence"],
                input_start_pos=match["input_start_pos"],
                input_end_pos=match["input_end_pos"],
                reference_sentence=match["reference_sentence"],
                reference_start_pos=match["reference_start_pos"],
                reference_end_pos=match["reference_end_pos"],
                reference_document=match["reference_document"],
                similarity_score=match["similarity_score"],
            )
            for match in results
        ]
    except (OSError, json.JSONDecodeError, KeyError) as e:
        sys.exit(f"Error processing JSON file: {e}")

    return markdown_content, plagiarism_matches


def generate_document_colors(
    plagiarism_matches: list[PlagiarismMatch],
) -> dict[str, str]:
    """Generate a distinct color for each reference document."""
    reference_documents = {match.reference_document for match in plagiarism_matches}

    # Define a set of distinct colors
    base_colors = [
        "#FF5733",  # Red-orange
        "#33A8FF",  # Blue
        "#33FF57",  # Green
        "#FF33A8",  # Pink
        "#A833FF",  # Purple
        "#FFD433",  # Yellow
        "#33FFD4",  # Teal
        "#FF8333",  # Orange
        "#8333FF",  # Indigo
        "#33FF83",  # Mint
    ]

    # If we have more documents than colors, generate additional ones
    if len(reference_documents) > len(base_colors):
        for _ in range(len(reference_documents) - len(base_colors)):
            r = random.randint(50, 200)
            g = random.randint(50, 200)
            b = random.randint(50, 200)
            base_colors.append(f"#{r:02x}{g:02x}{b:02x}")

    return {
        doc: base_colors[i % len(base_colors)]
        for i, doc in enumerate(sorted(reference_documents))
    }


def split_text_into_segments(
    content: str, matches: list[PlagiarismMatch]
) -> list[SegmentType]:
    """Split the document into segments, identifying which parts are plagiarized."""
    # Create a list of all start and end positions
    positions = []
    for match in matches:
        positions.append((match.input_start_pos, "start", match))
        positions.append((match.input_end_pos, "end", match))

    # Sort positions by their location and then by type (end comes before start)
    positions.sort(key=lambda x: (x[0], 0 if x[1] == "end" else 1))

    segments = []
    current_pos = 0
    active_matches = []

    # Handle the case where there's a text before the first position
    if positions and positions[0][0] > 0:
        segments.append(
            SegmentType(
                start=0,
                end=positions[0][0],
                text=content[0 : positions[0][0]],
                matches=[],
            )
        )
        current_pos = positions[0][0]

    for pos, pos_type, match in positions:
        # Add segment from current position to this new position
        if pos > current_pos:
            segment_text = content[current_pos:pos]
            segments.append(
                SegmentType(
                    start=current_pos,
                    end=pos,
                    text=segment_text,
                    matches=active_matches.copy(),  # Use copy to prevent reference issues
                )
            )

        # Update active matches
        if pos_type == "start":
            if match not in active_matches:  # Avoid duplicates
                active_matches.append(match)
        elif pos_type == "end":
            if match in active_matches:
                active_matches.remove(match)

        current_pos = pos

    # Add the final segment if there's content left
    if current_pos < len(content):
        segments.append(
            SegmentType(
                start=current_pos,
                end=len(content),
                text=content[current_pos:],
                matches=[],
            )
        )

    return segments

def create_html_with_highlights_html(
    content: str, plagiarism_matches: list[PlagiarismMatch], doc_colors: dict[str, str]
) -> str:
    html = markdown.markdown(content, extensions=["tables", "fenced_code", "attr_list"])
    soup = BeautifulSoup(html, "html.parser")

    # Collect all text nodes with their offsets
    text_nodes = []
    offset = 0
    for element in soup.descendants:
        if element.name in ["script", "style"]:
            continue
        if isinstance(element, str):
            length = len(element)
            text_nodes.append(
                {"node": element, "start": offset, "end": offset + length}
            )
            offset += length

    # Sort matches by start position
    plagiarism_matches.sort(key=lambda m: m.input_start_pos)

    # Prepare replacements without modifying DOM immediately
    replacements = []

    for match in plagiarism_matches:
        match_start = match.input_start_pos
        match_end = match.input_end_pos

        for tn in text_nodes:
            node_start, node_end = tn["start"], tn["end"]
            if node_end <= match_start or node_start >= match_end:
                continue  # No overlap

            relative_start = max(match_start - node_start, 0)
            relative_end = min(match_end - node_start, node_end - node_start)

            original_text = tn["node"]
            parent = original_text.parent
            if parent is None:
                continue  # Skip nodes already detached

            before = original_text[:relative_start]
            highlight = original_text[relative_start:relative_end]
            after = original_text[relative_end:]

            span_tag = soup.new_tag("span")
            doc_id = re.sub(r"[^a-zA-Z0-9]", "_", match.reference_document)
            opacity = min(0.3 + match.similarity_score * 0.7, 1.0)
            span_tag["class"] = f"plagiarized plag-doc-{doc_id}"
            span_tag["style"] = (
                f"opacity: {opacity}; background-color: {doc_colors[match.reference_document]}"
            )
            span_tag["data-references"] = match.reference_document
            span_tag["data-similarity"] = f"{match.similarity_score:.2f}"
            span_tag.string = highlight

            new_nodes = []
            if before:
                new_nodes.append(NavigableString(before))
            new_nodes.append(span_tag)
            if after:
                new_nodes.append(NavigableString(after))

            replacements.append((original_text, new_nodes))

    # Apply replacements after collecting all
    for original_text, new_nodes in replacements:
        if original_text.parent:
            original_text.replace_with(*new_nodes)

    return str(soup)


def create_html_with_highlights_md(
    content: str, plagiarism_matches: list[PlagiarismMatch], doc_colors: dict[str, str]
) -> str:
    """Create HTML content with plagiarism highlights."""
    segments = split_text_into_segments(content, plagiarism_matches)
    # TODO: the number of segments is not equal to the number of matches - it is greater - why?
    # Generate HTML with appropriate spans for highlights
    html_content = ""
    for segment in segments:
        if not segment.matches:
            # Regular text, no plagiarism
            html_content += segment.text
        else:
            # Plagiarized text
            class_names = []
            doc_ids = []
            similarity_sum = 0

            for match in segment.matches:
                doc_id = re.sub(r"[^a-zA-Z0-9]", "_", match.reference_document)
                class_names.append(f"plag-doc-{doc_id}")
                doc_ids.append(doc_id)
                similarity_sum += match.similarity_score

            # Average similarity for overlapping segments
            avg_similarity = similarity_sum / len(segment.matches)
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
            attrs = f'class="plagiarized {" ".join(class_names)}" style="opacity: {opacity}" '
            attrs += " ".join(f'{k}="{v}"' for k, v in data_attrs.items())

            html_content += f"<span {attrs}>{segment.text}</span>"

    # Convert Markdown to HTML, preserving our highlight spans
    html = markdown.markdown(html_content, extensions=["tables", "fenced_code"])

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
    with open(template_dir / "plagiarism_report_template.html", "r") as f:
        template = f.read()

    # Fill in the template
    output_html = template.format(
        title=f"Plagiarism Report: {input_filename}",
        subtitle="Plagiarism Visualization",
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


def save_html(html_content: str, output_path: str) -> None:
    """Save HTML content to the specified output file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully saved HTML report to {output_path}")
    except OSError as e:
        sys.exit(f"Error saving HTML file: {e}")


def main() -> None:
    """Main function to process files and generate visualization."""
    args = parse_arguments()

    # Load and process input files
    markdown_content, plagiarism_matches = load_files(args.input, args.plagiarism_data)

    # Generate colors for each reference document
    doc_colors = generate_document_colors(plagiarism_matches)

    # Create HTML with plagiarism highlights
    html_with_highlights = create_html_with_highlights_md(
        markdown_content, plagiarism_matches, doc_colors
    )

    # Generate the final HTML with CSS and JavaScript
    final_html = generate_final_html(
        html_with_highlights, doc_colors, plagiarism_matches, args.input, args.output
    )

    # Save the final HTML file
    save_html(final_html, args.output)


def test() -> None:
    """Main function to process files and generate visualization."""
    #args = parse_arguments()

    # Load and process input files
    markdown_content, plagiarism_matches = load_files("../BPMTE.md", "../BPMTE.json")

    # Generate colors for each reference document
    doc_colors = generate_document_colors(plagiarism_matches)

    # Create HTML with plagiarism highlights
    html_with_highlights = create_html_with_highlights_md(
        markdown_content, plagiarism_matches, doc_colors
    )

    # Generate the final HTML with CSS and JavaScript
    final_html = generate_final_html(
        html_with_highlights, doc_colors, plagiarism_matches, "../BPMTE.md", "../BPMTE.html"
    )

    # Save the final HTML file
    save_html(final_html, "../BPMTE.html")

if __name__ == "__main__":
    #main()
    test()
