import argparse

from sentence_plagiarism.plagiarism_checker import check


def get_inputs():
    parser = argparse.ArgumentParser(description="Plagiarism Detection Tool")
    parser.add_argument("input_text", help="Path to the input text file")
    parser.add_argument(
        "reference_documents", nargs="+", help="Paths to reference documents"
    )
    parser.add_argument(
        "--threshold", type=float, default=0.8, help="Similarity threshold"
    )
    # output file to save results as JSON
    parser.add_argument(
        "--output_file", type=str, default="results.json", help="Output file name"
    )
    # add quiet mode to suppress output
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress output to console"
    )
    # add minimum sentence length filter
    parser.add_argument(
        "--min_length", type=int, default=10, help="Minimum sentence length to compare"
    )
    args = parser.parse_args()
    in_text = args.input_text
    ref_docs = args.reference_documents
    threshold = args.threshold
    out_file = args.output_file
    quiet = args.quiet
    return in_text, ref_docs, threshold, out_file, quiet


def main():
    in_text, ref_docs, threshold, output, quiet = get_inputs()
    check(in_text, ref_docs, threshold, output, quiet)
