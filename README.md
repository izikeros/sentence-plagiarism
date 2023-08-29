# Plagiarism Checker

![img](https://img.shields.io/pypi/v/sentence-plagiarism.svg)
![](https://img.shields.io/pypi/pyversions/sentence-plagiarism.svg)
![](https://img.shields.io/pypi/dm/sentence-plagiarism.svg)

This is a command-line tool for checking the similarity between a given text and a set of reference documents. The tool uses the Jaccard similarity algorithm to compare the input text with the reference documents.

## Installation
Install in an isolated environment using pipx (or normal pip):
```
pipx install sentence-plagiarism
```

## CLI Usage

To run the plagiarism checker, use the following command:

```sh
sentence-plagiarism <path-to-input-file> <path-to-reference-file-1> <path-to-reference-file-2> ... [--threshold <threshold-value>] [--output_file <path-to-output-file>] [--quiet]
```

- `<path-to-input-file>`: Path to the input file to be checked for plagiarism.
- `<path-to-reference-file-1> ...`: Paths to the reference files to compare against.
- `--threshold`: (optional) The minimum similarity score required to consider a sentence as plagiarized. The value should be between 0 and 1.
- `--output-file` (optional): Path to the output file to save the results in JSON format.
- `--quiet` (optional): Flag to suppress the display of similar sentences in the console.

## Example

The following command:
```sh
sentence-plagiarism  input.txt --reference-files ref1.txt ref2.txt --similarity-threshold 0.8 --output-file results.json
```

can produce the following output on stdout:
```
Input Sentence:     The retriever and seq2seq modules commence their operations as pretrained models, and through a joint fine-tuning process, they adapt collaboratively, thus enhancing both retrieval and generation for specific downstream tasks.
Reference Sentence:  foobar  The retriever and seq2seq modules commence their operations as pretrained models, and through a joint fine-tuning process, they adapt collaboratively, thus enhancing both retrieval and generation for specific downstream tasks.
Reference Document: ref1.txt
Similarity Score: 0.9667

Input Sentence:      Closing thoughts  For a comprehensive understanding of the RAG technique, we offer an in-depth exploration, commencing with a simplified overview and progressively delving into more intricate technical facets.
Reference Sentence:  barfoo  For a comprehensive understanding of the RAG technique, we offer an in-depth exploration, commencing with a simplified overview and progressively delving into more intricate technical facets.
Reference Document: ref2.txt
Similarity Score: 0.8966

Results saved to results.json
```
and save results to `results.json`.

## Programmatic Usage

```python
from sentence_plagiarism import check

check(
    examined_file="txt/txt1.txt",
    reference_files=["txt/txt2.txt", "txt/txt3.txt"],
    similarity_threshold=0.8,
    output_file=None,
    quiet=False,
)
```

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Krystian Safjan - ksafjan@gmail.com

Project Link: [https://github.com/izikeros/sentence-plagiarism](https://github.com/izikeros/sentence-plagiarism)
