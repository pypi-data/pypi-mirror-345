from collections.abc import Iterable
import numpy as np
import pandas as pd

"""
Data containers
---------------
ActivitySegments 
    - (start, end, value)
    - Allows overlapping
    - Ex: [(0, 2, 1), (1, 6, 3), (9, 15, 0)]
ActivityProbabilities
    - [T,C] numpy array
    - For plotting predictions

Utility functions
-----------------
segments_from_sequence
    - Builds a segment container from a sequence
    - Ex: [0, 0, 1, 1, 1, 2, 2, 0] -> [(0, 1, 0), (2, 4, 1), (5, 6, 2), (7, 7, 0)]
"""


class ActivitySegments:
    def __init__(
        self,
        starts: Iterable,
        ends: Iterable,
        label_ids: Iterable,
        total_length: int = 0,  # Defaults to max(ends) + 1 if not provided
        label_set: list = None,  # Defaults to value in label_ids if not provided
        confidences: Iterable = None,  # Defaults to 1.0 if not provided
    ):
        # Set defaults if not provided
        total_length = total_length or max(ends) + 1
        label_set = label_set or [str(x) for x in range(max(label_ids) + 1)]

        # Validate inputs
        if not (len(starts) == len(ends) == len(label_ids)):
            raise ValueError("starts, ends, and label_ids must have same size")
        if max(label_ids) >= len(label_set):
            raise IndexError(f"label_id {max(label_ids)} not in label_set [{len(label_set)}]")
        if (confidences is not None) and (len(starts) != len(confidences)):
            raise ValueError("Must have a confidence for each segment")

        # Create the data
        self.df = pd.DataFrame({
            "start": starts,
            "end": ends,
            "length": np.array(ends) - np.array(starts) + 1,
            "label_id": label_ids,
            "label_name": [label_set[x] for x in label_ids],
            "confidence": confidences or 1.0,
        })
        self.label_set = label_set
        self.total_length = total_length


class ActivityProbabilities:
    def __init__(
        self,
        probs: np.ndarray,
        label_set: list = None,
    ):
        if (label_set is not None) and (probs.shape[1] != len(label_set)):
            raise ValueError(f"Dimension mismatch: probs={probs.shape} label_set={len(label_set)}")
        self.probs = probs
        self.label_set = label_set or [str(x) for x in range(probs.shape[1] + 1)]


def segments_from_sequence(
    sequence: Iterable,
    label_set: list = None,
    ignore_value: int = -1,
):
    sequence = np.array(sequence)
    transitions = np.flatnonzero(np.diff(sequence, prepend=ignore_value, append=ignore_value))
    starts = transitions[:-1]
    ends = transitions[1:] - 1
    label_ids = sequence[starts]
    mask = label_ids != ignore_value

    # TODO: remove test before release
    test = np.zeros(len(sequence)).astype(int) + ignore_value
    for s, e, v in zip(starts[mask], ends[mask], label_ids[mask]):
        test[s : e + 1] = v
    assert np.array_equal(test, sequence), f"Reconstructed sequence does not match original\n{test}\n{sequence}"

    return ActivitySegments(
        starts=starts[mask],
        ends=ends[mask],
        label_ids=label_ids[mask],
        total_length=len(sequence),
        label_set=label_set,
    )
