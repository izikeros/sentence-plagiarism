#!/usr/bin/env python3
"""Compare sentences from an input document with all sentences from reference documents - find very similar ones."""
import json
import re
from collections import defaultdict
from itertools import product

from sentence_plagiarism.similarity import jaccard_similarity


def _text_to_sentences(text):
    """Split the text into sentences using regex"""
    return re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)


def _split_texts_to_sentences(input_doc, reference_docs, min_length):
    input_sents = [s for s in _text_to_sentences(input_doc) if len(s) >= min_length]
    ref_doc_sents = defaultdict(list)
    for ref_doc, ref_content in reference_docs.items():
        ref_sents = [
            s
            for s in _text_to_sentences(ref_content.replace("\n", " ").strip())
            if len(s) >= min_length
        ]
        ref_doc_sents[ref_doc].extend(ref_sents)
    return input_sents, ref_doc_sents


def _cross_check_sentences(
    input_sents, ref_doc_sents, results, similarity_threshold, quiet
):
    for input_sent, (ref_doc, ref_sents) in product(input_sents, ref_doc_sents.items()):
        input_tokens = set(re.findall(r"\b\w+\b", input_sent.lower()))
        for ref_sent in ref_sents:
            ref_tokens = set(re.findall(r"\b\w+\b", ref_sent.lower()))
            similarity_score = jaccard_similarity(input_tokens, ref_tokens)
            if similarity_score > similarity_threshold:
                similarity = {
                    "input_sentence": input_sent,
                    "reference_sentence": ref_sent,
                    "reference_document": ref_doc,
                    "similarity_score": similarity_score,
                }
                results.append(similarity)
                if not quiet:
                    _display_similar_sentence(similarity)


def _display_similar_sentence(similarity_dict):
    print("Input Sentence:    ", similarity_dict["input_sentence"])
    print("Reference Sentence:", similarity_dict["reference_sentence"])
    print("Reference Document:", similarity_dict["reference_document"])
    print("Similarity Score: {:.4f}".format(similarity_dict["similarity_score"]))
    print()


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
    quiet=False,
    min_length=10,
):
    # placeholder for the list of dictionaries
    results = []
    input_doc, reference_docs = _get_all_files_content(examined_file, reference_files)

    input_sents, ref_doc_sents = _split_texts_to_sentences(
        input_doc, reference_docs, min_length
    )

    _cross_check_sentences(
        input_sents, ref_doc_sents, results, similarity_threshold, quiet
    )

    if output_file:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
            print(f"Results saved to {output_file}")
