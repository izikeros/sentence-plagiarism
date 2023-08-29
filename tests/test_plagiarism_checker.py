from sentence_plagiarism.plagiarism_checker import check


def test_check():
    check(
        examined_file="txt/txt1.txt",
        reference_files=["txt/txt2.txt", "txt/txt3.txt"],
        similarity_threshold=0.8,
        output_file="results.json",
        quiet=False,
    )
