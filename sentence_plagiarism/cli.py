import argparse
import sys

from sentence_plagiarism.plagiarism_checker import check


def get_inputs():
    parser = argparse.ArgumentParser(description="Plagiarism Detection Tool")
    parser.add_argument("input_file", help="Path to the input text file")
    parser.add_argument(
        "reference_files", nargs="+", help="Paths to reference documents"
    )
    parser.add_argument(
        "--threshold", "-t", type=float, default=0.8, help="Similarity threshold"
    )
    # output file to save results as JSON
    parser.add_argument(
        "--output", "-o", type=str, default="results.json", help="JSON output file name"
    )
    # text output file option
    parser.add_argument("--text_output", "-to", type=str, help="Text output file name")
    # add quiet mode to suppress output
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress output to console"
    )
    # add minimum sentence length filter
    parser.add_argument(
        "--min_length",
        "-ml",
        type=int,
        default=10,
        help="Minimum sentence length to compare",
    )
    # add similarity metric selection
    parser.add_argument(
        "--metric",
        "-m",
        type=str,
        default="jaccard_similarity",
        choices=[
            "jaccard_similarity",
            "cosine_similarity",
            "sorensen_dice_similarity",
            "overlap_similarity",
            "tversky_similarity",
            "jaro_similarity",
            "jaro_winkler_similarity",
        ],
        help="Similarity metric to use for comparison",
    )
    return parser.parse_args()


def main():
    args = get_inputs()
    try:
        check(
            examined_file=args.input_file,
            reference_files=args.reference_files,
            similarity_threshold=args.threshold,
            output_file=args.output,
            text_output_file=args.text_output,
            quiet=args.quiet,
            min_length=args.min_length,
            similarity_metric=args.metric,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1
