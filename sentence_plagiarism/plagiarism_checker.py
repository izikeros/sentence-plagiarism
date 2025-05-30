#!/usr/bin/env python3
"""Compare sentences from an input document with all sentences from reference documents - find very similar ones."""
import json
import re
from collections import defaultdict
from itertools import product


def _text_to_sentences(text):
    """Split the text into sentences and track their positions.

    - Ignore leading whitespace - assuming it belongs to the previous sentence.
    - Include trailing whitespace - assuming it belongs to the current sentence.
    - Start, end positions are inclusive. e.g., for string "abc def", start=0, end=2, the sentence is "abc".

    """
    sentences = []
    # The regex pattern splits text into sentences by identifying sentence-ending punctuation ('.', '?' or '!')
    # followed by whitespace. It avoids splitting on abbreviations (e.g., "e.g.", "Dr.") or initials (e.g., "A.B.").
    pattern = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s"

    # Find all split positions
    split_positions = [m.start() + 1 for m in re.finditer(pattern, text)]

    # Add the start of a text and end of a text to create complete ranges
    positions = [0] + split_positions + [len(text)]  # noqa: RUF005
    # TODO: KS: 2025-05-09: replace with:
    # positions = [0, *split_positions, len(text)]

    # Extract sentences with their positions
    for i in range(len(positions) - 1):
        start = positions[i]
        end = positions[i + 1] - 1
        if end == -1:
            end = 0  # or len(text) - 1
        # Adjust start to skip leading whitespace
        while start < end and text[start].isspace():
            start += 1

        sentence = text[start : end + 1]
        # Ignore strings that are all whitespace
        if sentence.strip() == "":
            continue
        sentences.append((sentence, start, end))
    return sentences


def _split_texts_to_sentences(input_doc, reference_docs, min_length):
    # Split the input document into sentences
    input_sent_data = [
        (s, start, end)
        for s, start, end in _text_to_sentences(input_doc)
        if len(s) >= min_length
    ]

    # Split the reference documents into sentences
    ref_doc_sents = defaultdict(list)

    for ref_doc, ref_content in reference_docs.items():
        ref_content_clean = ref_content.strip()
        ref_sent_data = [
            (s, start, end)
            for s, start, end in _text_to_sentences(ref_content_clean)
            if len(s) >= min_length
        ]
        ref_doc_sents[ref_doc].extend(ref_sent_data)

    return input_sent_data, ref_doc_sents


def _cross_check_sentences(
    input_sents,
    ref_doc_sents,
    results,
    similarity_threshold,
    quiet,
    similarity_metric="jaccard_similarity",
):
    from sentence_plagiarism.similarity import (  # noqa
        cosine_similarity,
        jaccard_similarity,
        jaro_similarity,
        jaro_winkler_similarity,
        overlap_similarity,
        sorensen_dice_similarity,
        tversky_similarity,
    )

    metric_function = locals()[similarity_metric]

    for input_sent_data, (ref_doc, ref_sents_data) in product(
        input_sents, ref_doc_sents.items()
    ):
        input_sent, input_start, input_end = input_sent_data
        input_tokens = set(re.findall(r"\b\w+\b", input_sent.lower()))

        for ref_sent_data in ref_sents_data:
            ref_sent, ref_start, ref_end = ref_sent_data
            ref_tokens = set(re.findall(r"\b\w+\b", ref_sent.lower()))
            similarity_score = metric_function(input_tokens, ref_tokens)

            if similarity_score > similarity_threshold:
                similarity = {
                    "input_sentence": input_sent,
                    "input_start_pos": input_start,
                    "input_end_pos": input_end,
                    "reference_sentence": ref_sent,
                    "reference_start_pos": ref_start,
                    "reference_end_pos": ref_end,
                    "reference_document": ref_doc,
                    "similarity_score": similarity_score,
                }
                results.append(similarity)
                if not quiet:
                    _display_similar_sentence(similarity)


def _display_similar_sentence(similarity_dict):
    print("Input Sentence:    ", similarity_dict["input_sentence"])
    print(
        f"Input Position:     {similarity_dict['input_start_pos']}-{similarity_dict['input_end_pos']}"
    )
    print("Reference Sentence:", similarity_dict["reference_sentence"])
    print(
        f"Reference Position: {similarity_dict['reference_start_pos']}-{similarity_dict['reference_end_pos']}"
    )
    print("Reference Document:", similarity_dict["reference_document"])
    print("Similarity Score:   {:.4f}".format(similarity_dict["similarity_score"]))
    print()


def _write_to_text_file(results, text_output_file):
    """Write similarity results to a text file in a readable format."""
    with open(text_output_file, "w", encoding="utf-8") as f:
        for i, similarity in enumerate(results, 1):
            f.write(f"Match #{i}\n")
            f.write(f"Input Sentence:     {similarity['input_sentence']}\n")
            f.write(
                f"Input Position:     {similarity['input_start_pos']}-{similarity['input_end_pos']}\n"
            )
            f.write(f"Reference Sentence: {similarity['reference_sentence']}\n")
            f.write(
                f"Reference Position: {similarity['reference_start_pos']}-{similarity['reference_end_pos']}\n"
            )
            f.write(f"Reference Document: {similarity['reference_document']}\n")
            f.write(f"Similarity Score:   {similarity['similarity_score']:.4f}\n")
            f.write("\n")
        print(f"Results saved to text file: {text_output_file}")


def _get_all_files_content(examined_file, reference_files):
    with open(examined_file, encoding="utf-8") as f:
        input_text_content = f.read().replace("\n", " ").strip()

    reference_docs = {}
    for ref_doc in reference_files:
        with open(ref_doc, encoding="utf-8") as f:
            reference_docs[ref_doc] = f.read().replace("\n", " ").strip()
    return input_text_content, reference_docs


def check(
    examined_file,
    reference_files,
    similarity_threshold,
    output_file=None,
    text_output_file=None,
    quiet=False,
    min_length=10,
    similarity_metric="jaccard_similarity",
):
    """
    Check for similar sentences between an examined file and reference files.

    Args:
        examined_file: Path to the file being examined
        reference_files: List of paths to reference files
        similarity_threshold: Threshold for similarity detection
        output_file: Path for JSON output (None to skip)
        text_output_file: Path for text output (None to skip)
        quiet: If True, suppress console output
        min_length: Minimum sentence length to consider
        similarity_metric: Method to calculate similarity
    """
    # placeholder for the list of dictionaries
    results = []
    input_doc, reference_docs = _get_all_files_content(examined_file, reference_files)

    input_sents, ref_doc_sents = _split_texts_to_sentences(
        input_doc, reference_docs, min_length
    )

    _cross_check_sentences(
        input_sents,
        ref_doc_sents,
        results,
        similarity_threshold,
        quiet,
        similarity_metric,
    )

    # loop over all the results and in each result item convert value under 'reference_document' from
    # path to string
    for result in results:
        result["reference_document"] = str(result["reference_document"])

    # Output to JSON file if specified
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
            if not quiet:
                print(f"Results saved to JSON file: {output_file}")

    # Output to a text file if specified
    if text_output_file:
        _write_to_text_file(results, text_output_file)

    return results
