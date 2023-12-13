from struct import Struct

import numpy as np


def q15dec(x: int) -> float:
    """Convert Q1.15 integer to float."""
    return x / (1 << 15)


def payload_to_melvecs(
    payload: str, melvec_length: int, num_melvecs: int
) -> np.ndarray:
    """Convert a payload string to a melvecs array."""
    s = Struct(f"!{melvec_length}h")
    melvecs = np.vectorize(q15dec)(np.array(list(s.iter_unpack(payload))))

    melvecs = np.asarray(melvecs, dtype=np.float32).reshape(
        (num_melvecs, melvec_length)
    )
    melvecs = np.rot90(melvecs, k=-1, axes=(0, 1))
    melvecs = np.fliplr(melvecs)
    return melvecs
