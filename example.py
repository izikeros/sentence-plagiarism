from sentence_plagiarism import check
from sentence_plagiarism.visualization.file_handlers import save_html
from sentence_plagiarism.visualization.html_generator import (
    create_html_with_highlights_md,
)

# Basic usage
check(
    examined_file="tests/txt/txt1.txt",
    reference_files=["tests/txt/txt2.txt", "tests/txt/txt3.txt"],
    similarity_threshold=0.8,
    output_file="results.json",
    text_output_file="results.txt",
    quiet=False,
    min_length=10,
    similarity_metric="jaccard_similarity",
)

# Visualization
from sentence_plagiarism.visualization.visualization_utils import (
    generate_document_colors,
)
from sentence_plagiarism.visualization.file_handlers import load_files
from sentence_plagiarism.visualization.html_generator import generate_final_html


markdown_content, plagiarism_matches = load_files(
    markdown_path="tests/txt/txt1.txt", json_path="results.json"
)
doc_colors = generate_document_colors(plagiarism_matches)
html_with_highlights = create_html_with_highlights_md(
    markdown_content, plagiarism_matches, doc_colors
)
final_html = generate_final_html(
    html_content=html_with_highlights,
    doc_colors=doc_colors,
    plagiarism_matches=plagiarism_matches,
    input_file="tests/txt/txt1.txt",
)
save_html(final_html, "plagiarism_report.html")
