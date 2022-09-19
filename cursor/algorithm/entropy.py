import numpy as np
from scipy import stats
from math import log, e

from cursor.misc import Timer


def calc_entropy(labels, base=None):
    values, counts, = np.unique(labels, return_counts=True)
    # TODO: use data in entropy directly, don't use sorted unique elements?
    return stats.entropy(counts, base=base)


def impl(labels, base=None):
    """Computes entropy of label distribution."""

    assert len(labels) > 1

    _, counts = np.unique(labels, return_counts=True)

    probs = counts / len(labels)
    n_classes = np.count_nonzero(probs)

    if n_classes <= 1:
        return 0

    ent = 0.0

    # Compute entropy
    base = e if base is None else base
    for i in probs:
        ent -= i * log(i, base)

    return ent
