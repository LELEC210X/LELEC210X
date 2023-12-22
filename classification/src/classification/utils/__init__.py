import struct

import numpy as np

from common.defaults import MELVEC_LENGTH, N_MELVECS


def payload_to_melvecs(
    payload: str, melvec_length: int = MELVEC_LENGTH, n_melvecs: int = N_MELVECS
) -> np.ndarray:
    """Convert a payload string to a melvecs array."""
    fmt = f"!{melvec_length}h"
    buffer = bytes.fromhex(payload.strip())
    unpacked = struct.iter_unpack(fmt, buffer)
    melvecs_q15int = np.asarray(list(unpacked), dtype=np.int16)
    melvecs = melvecs_q15int.astype(float) / 32768  # 32768 = 2 ** 15
    melvecs = np.rot90(melvecs, k=-1, axes=(0, 1))
    melvecs = np.fliplr(melvecs)
    return melvecs
