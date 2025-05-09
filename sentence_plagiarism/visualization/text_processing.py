import logging
import re
from typing import NamedTuple

from sentence_plagiarism.visualization.models import PlagiarismMatch

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def clean_text(txt):
    txt_clean = txt
    # remove all "|"
    # txt_clean = re.sub(r"\|", "", txt_clean)
    # remove and two or more dashes
    # txt_clean = re.sub(r"[-]{2,}", "", txt_clean)
    # remove all opening and closing tags like: <PC>, </PC>. one up to 15 letters in brackets (both opening and closing tags)
    txt_clean = re.sub(r"<[a-zA-Z0-9]{1,15}>", "", txt_clean)
    txt_clean = re.sub(r"</[a-zA-Z0-9]{1,15}>", "", txt_clean)
    return txt_clean


class SegmentType(NamedTuple):
    """Represents a segment of text with its plagiarism status."""

    start: int
    end: int
    text: str
    matches: list[PlagiarismMatch]


def split_text_into_segments(
    content: str, matches: list[PlagiarismMatch]
) -> list[SegmentType]:
    logger.debug("Starting split_text_into_segments")
    logger.debug(f"Content length: {len(content)}")
    logger.debug(f"Number of matches: {len(matches)}")
    """Split the document into segments, identifying which parts are plagiarized."""
    # Create a list of all start and end positions
    positions = []
    for match in matches:
        positions.append((match.input_start_pos, "start", match))
        positions.append((match.input_end_pos, "end", match))

    # Sort positions by their location and then by type (end comes before start)
    # E.g. for matches: (1, "start"), (3, "end"), (3, "start"), (7, "end"), (5, "start"), (9, "end")
    # we want to process the end of the first match before the start of the second
    # This ensures that if two matches overlap, the end of the first match is processed before the start of the second
    # This prevents the first match from being added to the active matches list when it is already ending
    # This is important for the correct display of overlapping matches.
    # After sorting, the positions will look like this:
    # [(1, "start"), (3, "end"), (3, "start"), (5, "start"), (7, "end"), (9, "end")]
    positions.sort(key=lambda x: (x[0], 0 if x[1] == "end" else 1))

    segments = []
    current_pos = 0
    active_matches = []

    # Handle the case where there's a text before the first position
    if positions and positions[0][0] > 0:
        segments.append(
            SegmentType(
                start=0,
                end=positions[0][0],
                text=content[0 : positions[0][0]],
                matches=[],
            )
        )
        current_pos = positions[0][0]

    for pos, pos_type, match in positions:
        logger.debug(
            f"Processing position: {pos}, type: {pos_type}, match: {match}",
            pos,
            pos_type,
            match,
        )
        # Add segment from current position to this new position
        if pos > current_pos:
            segment_text = content[current_pos:pos]
            segments.append(
                SegmentType(
                    start=current_pos,
                    end=pos,
                    text=segment_text,
                    matches=active_matches.copy(),  # Use copy to prevent reference issues
                )
            )

        # Update active matches
        if pos_type == "start":
            if match not in active_matches:  # Avoid duplicates
                active_matches.append(match)
        elif pos_type == "end" and match in active_matches:
            active_matches.remove(match)

        current_pos = pos

    # Add the final segment if there's content left
    if current_pos < len(content):
        segments.append(
            SegmentType(
                start=current_pos,
                end=len(content),
                text=content[current_pos:],
                matches=[],
            )
        )

    logger.debug(f"Generated segments:{segments}")
    return segments
