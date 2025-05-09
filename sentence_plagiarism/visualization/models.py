import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class PlagiarismMatch:
    """Represents a single plagiarism match."""

    input_sentence: str
    input_start_pos: int
    input_end_pos: int
    reference_sentence: str
    reference_start_pos: int
    reference_end_pos: int
    reference_document: str
    similarity_score: float

    def __post_init__(self):
        """Validate that sentence lengths match position ranges."""
        # Validate input sentence
        input_length = len(self.input_sentence)
        input_range = self.input_end_pos - self.input_start_pos + 1

        logger.debug(
            f"Validating input: length={input_length}, range={input_range}, sentence='{self.input_sentence}'"
        )
        if input_length != input_range:
            raise ValueError(
                f"Input sentence length ({input_length}) doesn't match position range "
                f"({input_range}): {self.input_sentence}"
            )

        # Validate reference sentence
        ref_length = len(self.reference_sentence)
        ref_range = self.reference_end_pos - self.reference_start_pos + 1

        logger.debug(
            f"Validating reference: length={ref_length}, range={ref_range}, sentence='{self.reference_sentence}'"
        )
        if ref_length != ref_range:
            raise ValueError(
                f"Reference sentence length ({ref_length}) doesn't match position range "
                f"({ref_range}): {self.reference_sentence}"
            )

        # Validate similarity score is between 0 and 1
        if not 0 <= self.similarity_score <= 1:
            raise ValueError(
                f"Similarity score must be between 0 and 1, got {self.similarity_score}"
            )
