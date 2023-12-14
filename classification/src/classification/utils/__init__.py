import struct

import numpy as np


def payload_to_melvecs(payload: str, melvec_length: int, n_melvecs: int) -> np.ndarray:
    """Convert a payload string to a melvecs array."""
    fmt = f"!{melvec_length}h"
    buffer = bytes.fromhex(payload.strip())
    print(len(buffer), buffer)
    unpacked = struct.iter_unpack(fmt, buffer)
    print(list(unpacked))
    melvecs_q15int = np.fromiter(unpacked, dtype=np.uint16)
    melvecs = melvecs_q15int / (1 << 15)
    melvecs = np.rot90(melvecs, k=-1, axes=(0, 1))
    melvecs = np.fliplr(melvecs)
    return melvecs
