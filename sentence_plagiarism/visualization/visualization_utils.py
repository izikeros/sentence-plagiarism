import random

from sentence_plagiarism.visualization.models import PlagiarismMatch


def generate_document_colors(
    plagiarism_matches: list[PlagiarismMatch],
) -> dict[str, str]:
    """Generate a distinct color for each reference document."""
    reference_documents = {match.reference_document for match in plagiarism_matches}

    # Define a set of distinct colors
    base_colors = [
        "#FF5733",  # Red-orange
        "#33A8FF",  # Blue
        "#33FF57",  # Green
        "#FF33A8",  # Pink
        "#A833FF",  # Purple
        "#FFD433",  # Yellow
        "#33FFD4",  # Teal
        "#FF8333",  # Orange
        "#8333FF",  # Indigo
        "#33FF83",  # Mint
    ]

    # If we have more documents than colors, generate additional ones
    if len(reference_documents) > len(base_colors):
        for _ in range(len(reference_documents) - len(base_colors)):
            r = random.randint(50, 200)
            g = random.randint(50, 200)
            b = random.randint(50, 200)
            base_colors.append(f"#{r:02x}{g:02x}{b:02x}")

    return {
        doc: base_colors[i % len(base_colors)]
        for i, doc in enumerate(sorted(reference_documents))
    }
