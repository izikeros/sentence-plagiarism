from unittest.mock import mock_open, patch

import pytest

from sentence_plagiarism.plagiarism_checker import (
    _cross_check_sentences,
    _display_similar_sentence,
    _get_all_files_content,
    _split_texts_to_sentences,
    _text_to_sentences,
    check,
)


@pytest.fixture
def sample_texts():
    """Fixture providing sample texts for testing."""
    input_text = "This is a test sentence. Another test sentence with similarity."
    ref_docs = {
        "doc1.txt": "This is a test sentence with words. Something completely different.",
        "doc2.txt": "Another test sentence with similarity and more words.",
    }
    return input_text, ref_docs


@pytest.fixture
def sample_files():
    """Fixture providing sample file paths for testing."""
    return "input.txt", ["ref1.txt", "ref2.txt"]


@pytest.fixture
def sample_results():
    """Fixture providing sample similarity results."""
    return [
        {
            "input_sentence": "This is a test sentence.",
            "reference_sentence": "This is a test sentence with words.",
            "reference_document": "doc1.txt",
            "similarity_score": 0.85,
        }
    ]


class TestTextToSentences:
    def test_basic_sentence_splitting(self):
        """Test that _text_to_sentences correctly splits basic sentences."""
        text = "This is one sentence. This is another sentence."
        result = _text_to_sentences(text)
        assert len(result) == 2
        assert result[0] == ("This is one sentence.", 0, 22)
        assert result[1] == ("This is another sentence.", 22, 47)

    def test_complex_sentence_splitting(self):
        """Test splitting with abbreviations and special cases."""
        text = "Dr. Smith went to the store. What did he buy? He bought apples, oranges, etc. Then he went home."
        result = _text_to_sentences(text)
        # The expected result: [('Dr. Smith went to the store.', 0, 29), ('What did he buy?', 29, 46), ('He bought apples, oranges, etc.', 46, 78), ('Then he went home.', 78, 96)]
        assert len(result) == 4
        assert result[0] == ("Dr. Smith went to the store.", 0, 29)
        assert result[1] == ("What did he buy?", 29, 46)
        assert result[2] == ("He bought apples, oranges, etc.", 46, 78)
        assert result[3] == ("Then he went home.", 78, 96)

    def test_empty_text(self):
        """Test that an empty text returns a list with one empty string."""
        result = _text_to_sentences("")
        assert result == [("", 0, 0)]


class TestSplitTextsToSentences:
    def test_basic_splitting(self, sample_texts):
        """Test that _split_texts_to_sentences correctly splits input and reference texts."""
        input_doc, ref_docs = sample_texts
        min_length = 0

        input_sents, ref_doc_sents = _split_texts_to_sentences(
            input_doc, ref_docs, min_length
        )

        assert len(input_sents) == 2
        assert input_sents[0] == ("This is a test sentence.", 0, 25)
        assert input_sents[1] == ("Another test sentence with similarity.", 25, 63)
        assert len(ref_doc_sents) == 2

        assert ref_doc_sents["doc1.txt"][0] == (
            "This is a test sentence with words.",
            0,
            36,
        )
        assert ref_doc_sents["doc1.txt"][1] == (
            "Something completely different.",
            36,
            67,
        )
        assert ref_doc_sents["doc2.txt"][0] == (
            "Another test sentence with similarity and more words.",
            0,
            53,
        )

    def test_min_length_filter(self, sample_texts):
        """Test that sentences shorter than min_length are filtered out."""
        input_doc, ref_docs = sample_texts
        min_length = 30

        input_sents, ref_doc_sents = _split_texts_to_sentences(
            input_doc, ref_docs, min_length
        )

        assert len(input_sents) == 1
        assert "Another test sentence with similarity." in input_sents[0][0]
        assert len(ref_doc_sents["doc2.txt"]) == 1


class TestCrossCheckSentences:
    def test_similarity_detection(self, sample_texts):
        """Test that similar sentences are detected correctly."""
        input_doc, ref_docs = sample_texts
        input_sents, ref_doc_sents = _split_texts_to_sentences(input_doc, ref_docs, 0)
        results = []
        similarity_threshold = 0.5

        with patch("builtins.print"):
            _cross_check_sentences(
                input_sents, ref_doc_sents, results, similarity_threshold, quiet=False
            )

        assert len(results) >= 2  # At least 2 matches with threshold 0.5

        # Check if structure is correct
        assert all(
            key in results[0]
            for key in [
                "input_sentence",
                "reference_sentence",
                "reference_document",
                "similarity_score",
            ]
        )

    def test_threshold_filtering(self, sample_texts):
        """Test that a similarity threshold correctly filters matches."""
        input_doc, ref_docs = sample_texts
        input_sents, ref_doc_sents = _split_texts_to_sentences(input_doc, ref_docs, 0)

        # Test with a low threshold
        results_low = []
        _cross_check_sentences(input_sents, ref_doc_sents, results_low, 0.1, quiet=True)

        # Test with a high threshold
        results_high = []
        _cross_check_sentences(
            input_sents, ref_doc_sents, results_high, 0.9, quiet=True
        )

        assert len(results_low) > len(results_high)

    def test_quiet_mode(self, sample_texts):
        """Test that quiet mode suppresses output."""
        input_doc, ref_docs = sample_texts
        input_sents, ref_doc_sents = _split_texts_to_sentences(input_doc, ref_docs, 0)
        results = []

        with patch("builtins.print") as mock_print:
            _cross_check_sentences(input_sents, ref_doc_sents, results, 0.5, quiet=True)
            mock_print.assert_not_called()


@pytest.mark.skip(reason="Need to verify this test")
class TestDisplaySimilarSentence:
    def test_output_format(self, sample_results):
        """Test that the similar sentence display has a correct format."""
        with patch("builtins.print") as mock_print:
            _display_similar_sentence(sample_results[0])
            assert mock_print.call_count == 4


class TestGetAllFilesContent:
    def test_file_reading(self, sample_files):
        """Test that files are read correctly."""
        input_file, ref_files = sample_files

        mock_file_data = {
            input_file: "This is input text.\nWith multiple lines.",
            ref_files[0]: "This is reference text 1.\nWith lines.",
            ref_files[1]: "This is reference text 2.",
        }

        def mock_file_open(filename, *args, **kwargs):
            if filename in mock_file_data:
                return mock_open(read_data=mock_file_data[filename])(*args, **kwargs)
            return mock_open()(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_file_open):
            input_content, ref_contents = _get_all_files_content(input_file, ref_files)

            assert input_content == "This is input text. With multiple lines."
            assert ref_contents[ref_files[0]] == "This is reference text 1. With lines."
            assert ref_files[0] in ref_contents
            assert ref_files[1] in ref_contents


class TestCheckFunction:
    def test_basic_check(self):
        """Test the main check function with basic inputs."""
        input_file = "input.txt"
        ref_files = ["ref1.txt", "ref2.txt"]

        mock_file_data = {
            input_file: "This is a test sentence.",
            ref_files[0]: "This is a similar test sentence.",
            ref_files[1]: "Something completely different.",
        }

        def mock_file_open(filename, mode="r", *args, **kwargs):
            if filename in mock_file_data and mode == "r":
                return mock_open(read_data=mock_file_data[filename])(*args, **kwargs)
            return mock_open()(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_file_open):
            with patch("json.dump") as mock_json_dump:
                with patch("builtins.print") as mock_print:
                    check(input_file, ref_files, 0.5, "results.json")

                    # Check that json.dump was called
                    mock_json_dump.assert_called_once()
                    # Get the results from the first arg of json.dump
                    results = mock_json_dump.call_args[0][0]
                    assert len(results) >= 1

    def test_min_length_filter_in_check(self):
        """Test that the min_length parameter works in the check function."""
        input_file = "input.txt"
        ref_files = ["ref1.txt"]

        mock_file_data = {
            input_file: "Short. This is a longer test sentence.",
            ref_files[0]: "Short too. This is a similar longer test sentence.",
        }

        def mock_file_open(filename, mode="r", *args, **kwargs):
            if filename in mock_file_data and mode == "r":
                return mock_open(read_data=mock_file_data[filename])(*args, **kwargs)
            return mock_open()(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_file_open):
            with patch("json.dump") as mock_json_dump:
                # Test with min_length that should filter out "Short" and "Short too"
                check(
                    input_file,
                    ref_files,
                    0.5,
                    "results.json",
                    quiet=True,
                    min_length=10,
                )

                # Get the results from the first arg of json.dump
                results = mock_json_dump.call_args[0][0]

                # Check that we only have matches for the longer sentences
                for result in results:
                    assert len(result["input_sentence"]) >= 10
                    assert len(result["reference_sentence"]) >= 10

    def test_file_not_found(self):
        """Test handling when an input file is not found."""
        with pytest.raises(FileNotFoundError):
            check("nonexistent.txt", ["ref.txt"], 0.5)

    def test_no_output_file(self):
        """Test check function works when no output file is specified."""
        input_file = "input.txt"
        ref_files = ["ref1.txt"]

        mock_file_data = {
            input_file: "Test sentence.",
            ref_files[0]: "Test sentence similarity.",
        }

        def mock_file_open(filename, mode="r", *args, **kwargs):
            if filename in mock_file_data and mode == "r":
                return mock_open(read_data=mock_file_data[filename])(*args, **kwargs)
            return mock_open()(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_file_open):
            with patch("json.dump") as mock_json:
                check(input_file, ref_files, 0.5, output_file=None, quiet=True)
                mock_json.assert_not_called()


def test_check():
    check(
        examined_file="txt/txt1.txt",
        reference_files=["txt/txt2.txt", "txt/txt3.txt"],
        similarity_threshold=0.8,
        output_file="results.json",
        quiet=False,
    )
