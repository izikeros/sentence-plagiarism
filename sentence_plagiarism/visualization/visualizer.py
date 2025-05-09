#!/usr/bin/env python3
"""
Plagiarism Visualizer - Converts a Markdown document with plagiarism data
into an interactive HTML report highlighting plagiarized content.

Usage:
   python visualizer.py --input document.md --plagiarism-data results.json --output report.html

TODO:
- add possibility to fold/unfold sections without any plagiarism
    - display (on/off) only plagiarised sentences with some context - like 2 sentences before and after
    - divide text to plagiarized and non-plagiarized divs and allow to fold/unfold unplagiarised divs
- generate standalone - single file HTML report with all CSS and JS included

"""

import argparse
import logging
import re

from sentence_plagiarism.visualization.file_handlers import load_files, save_html
from sentence_plagiarism.visualization.html_generator import (
    create_html_with_highlights_md,
    generate_final_html,
)
from sentence_plagiarism.visualization.visualization_utils import (
    generate_document_colors,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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

    # Cleanup output
    # remove ****
    html_with_highlights = re.sub(r"\*\*\*\*", "", html_with_highlights)

    # Generate the final HTML with CSS and JavaScript
    final_html = generate_final_html(
        html_with_highlights, doc_colors, plagiarism_matches, args.input
    )

    # Save the final HTML file
    save_html(final_html, args.output)


if __name__ == "__main__":
    main()
