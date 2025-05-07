#!/usr/bin/env python3
"""
Plagiarism Visualizer - Converts a Markdown document with plagiarism data
into an interactive HTML report highlighting plagiarized content.

Usage:
   python plagiarism_visualizer.py --input document.md --plagiarism-data results.json --output report.html
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import NamedTuple

import markdown


class PlagiarismMatch(NamedTuple):
    """Represents a single plagiarism match."""

    input_sentence: str
    input_start_pos: int
    input_end_pos: int
    reference_sentence: str
    reference_start_pos: int
    reference_end_pos: int
    reference_document: str
    similarity_score: float


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
            # Try to handle direct list of results
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
        """
        Split the document into segments, identifying which parts are plagiarized.
        Handles overlapping segments properly.
        """
        # Create a list of all start and end positions
        positions = []
        for match in matches:
            positions.append((match.input_start_pos, "start", match))
            positions.append((match.input_end_pos, "end", match))

        # Sort positions by their location and then by type (end comes before start)
        positions.sort(key=lambda x: (x[0], 0 if x[1] == "end" else 1))

        segments = []
        current_pos = 0
        active_matches = set()

        # Handle the case where there's text before the first position
        if positions and positions[0][0] > 0:
            segments.append(
                SegmentType(
                    start=0,
                    end=positions[0][0],
                    text=content[0:positions[0][0]],
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
                        matches=list(active_matches),
                    )
                )

            # Update active matches
            if pos_type == "start":
                active_matches.add(match)
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


def create_html_with_highlights(
    content: str, plagiarism_matches: list[PlagiarismMatch], doc_colors: dict[str, str]
) -> str:
    """Create HTML content with plagiarism highlights."""
    segments = split_text_into_segments(content, plagiarism_matches)

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

    # Convert markdown to HTML, preserving our highlight spans
    html = markdown.markdown(html_content, extensions=["tables", "fenced_code"])

    return html


def generate_final_html(
    html_content: str,
    doc_colors: dict[str, str],
    plagiarism_matches: list[PlagiarismMatch],
) -> str:
    """Generate the final self-contained HTML file with styling and JavaScript."""
    # Get unique list of reference documents for filter controls
    reference_documents = sorted(
        {match.reference_document for match in plagiarism_matches}
    )

    # Create filter buttons HTML
    filter_buttons = ""
    filter_buttons += (
        '<button id="show-all-btn" class="control-btn active">Show All</button>'
    )
    filter_buttons += '<button id="hide-all-btn" class="control-btn">Hide All</button>'

    for doc in reference_documents:
        doc_id = re.sub(r"[^a-zA-Z0-9]", "_", doc)
        doc_name = Path(doc).name
        filter_buttons += f'<button class="filter-btn control-btn" data-doc="{doc_id}">{doc_name}</button>'

    # Create document legend
    legend_items = ""
    for doc, color in doc_colors.items():
        doc_id = re.sub(r"[^a-zA-Z0-9]", "_", doc)
        doc_name = Path(doc).name
        legend_items += f'<div class="legend-item"><span class="color-box" style="background-color: {color};"></span>{doc_name}</div>'

    # Define CSS
    css = f"""
   <style>
       body {{
           font-family: Arial, sans-serif;
           line-height: 1.6;
           max-width: 900px;
           margin: 0 auto;
           padding: 20px;
       }}

       .controls {{
           position: sticky;
           top: 0;
           background: white;
           padding: 15px 0;
           border-bottom: 1px solid #ddd;
           margin-bottom: 20px;
           z-index: 100;
       }}

       .control-btn {{
           padding: 8px 12px;
           margin-right: 5px;
           border: 1px solid #ccc;
           background: #f5f5f5;
           cursor: pointer;
           border-radius: 4px;
       }}

       .control-btn.active {{
           background: #4CAF50;
           color: white;
           border-color: #4CAF50;
       }}

       .legend {{
           margin-top: 10px;
           display: flex;
           flex-wrap: wrap;
           gap: 10px;
       }}

       .legend-item {{
           display: flex;
           align-items: center;
           margin-right: 15px;
       }}

       .color-box {{
           width: 15px;
           height: 15px;
           display: inline-block;
           margin-right: 5px;
           border: 1px solid #333;
       }}

       .plagiarized {{
           position: relative;
           border-radius: 3px;
           cursor: pointer;
       }}

       .plagiarized:hover {{
           filter: brightness(0.9);
       }}

       .plagiarized:hover::after {{
           content: attr(data-references) "\\A" "Similarity: " attr(data-similarity);
           position: absolute;
           bottom: 100%;
           left: 0;
           background: #333;
           color: white;
           padding: 5px 10px;
           border-radius: 3px;
           font-size: 14px;
           white-space: pre;
           z-index: 10;
           pointer-events: none;
       }}

       .hidden {{
           background-color: transparent !important;
           border: 1px dashed #ccc;
       }}

       pre, code {{
           background-color: #f6f8fa;
           border-radius: 3px;
           padding: 10px;
           overflow-x: auto;
       }}

       /* Document-specific colors */
       {
        chr(10).join(
            [
                f".plag-doc-{re.sub(r'[^a-zA-Z0-9]', '_', doc)} {{ background-color: {color}; }}"
                for doc, color in doc_colors.items()
            ]
        )
    }
   </style>
   """

    # Define JavaScript
    js = """
   <script>
       document.addEventListener('DOMContentLoaded', function() {
           // Show/Hide all buttons
           document.getElementById('show-all-btn').addEventListener('click', function() {
               document.querySelectorAll('.plagiarized').forEach(el => {
                   el.classList.remove('hidden');
               });
               setActiveButton(this);
           });

           document.getElementById('hide-all-btn').addEventListener('click', function() {
               document.querySelectorAll('.plagiarized').forEach(el => {
                   el.classList.add('hidden');
               });
               setActiveButton(this);
           });

           // Filter buttons
           document.querySelectorAll('.filter-btn').forEach(btn => {
               btn.addEventListener('click', function() {
                   const docId = this.getAttribute('data-doc');

                   // Hide all plagiarism highlights
                   document.querySelectorAll('.plagiarized').forEach(el => {
                       el.classList.add('hidden');
                   });

                   // Show only the selected document's highlights
                   document.querySelectorAll('.plag-doc-' + docId).forEach(el => {
                       el.classList.remove('hidden');
                   });

                   setActiveButton(this);
               });
           });

           function setActiveButton(activeBtn) {
               document.querySelectorAll('.control-btn').forEach(btn => {
                   btn.classList.remove('active');
               });
               activeBtn.classList.add('active');
           }
       });
   </script>
   """

    # Combine everything into a complete HTML document
    complete_html = f"""<!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>Plagiarism Report</title>
       {css}
   </head>
   <body>
       <div class="controls">
           <h2>Plagiarism Visualization</h2>
           <div class="buttons">
               {filter_buttons}
           </div>
           <div class="legend">
               {legend_items}
           </div>
       </div>
       <div class="content">
           {html_content}
       </div>
       {js}
   </body>
   </html>
   """

    return complete_html


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
    html_with_highlights = create_html_with_highlights(
        markdown_content, plagiarism_matches, doc_colors
    )

    # Generate the final HTML with CSS and JavaScript
    final_html = generate_final_html(
        html_with_highlights, doc_colors, plagiarism_matches
    )

    # Save the final HTML file
    save_html(final_html, args.output)


if __name__ == "__main__":
    main()
