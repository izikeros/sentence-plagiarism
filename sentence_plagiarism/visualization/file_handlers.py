import json
import sys

from sentence_plagiarism.visualization.models import PlagiarismMatch


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


def save_html(html_content: str, output_path: str) -> None:
    """Save HTML content to the specified output file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully saved HTML report to {output_path}")
    except OSError as e:
        sys.exit(f"Error saving HTML file: {e}")
