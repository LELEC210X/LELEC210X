import atexit
import logging
import statistics as stats
from collections.abc import Callable
from functools import wraps
from time import time
from typing import Any

import numpy as np

logging.basicConfig(level=logging.INFO)


# Order of the common parameter list shared by all the blocks. In GRC it is
# built from the individual flowgraph variables:
#   [data_rate, fdev, samp_rate, oversampling, preamble_len, sync_word, payload_len, crc_len]
COMMON_PARAMS_KEYS = (
    "data_rate",
    "fdev",
    "samp_rate",
    "oversampling",
    "preamble_len",
    "sync_word",
    "payload_len",
    "crc_len",
)


def parse_common_params(params: Any):
    """
    Parse the common parameters shared by all the blocks.

    `params` is either a list/tuple ordered as COMMON_PARAMS_KEYS, or a
    dictionary using these keys. The returned dictionary contains these keys
    (lengths in bytes, rates in Hz, integers converted to int) plus the
    derived values:

        hdr_len    = preamble_len + sync word length
        packet_len = hdr_len + payload_len + crc_len
    """
    values = list(params)
    if len(values) != len(COMMON_PARAMS_KEYS):
        for i in range(len(values)):
            print(values[i])
        raise ValueError(
            f"Expected {len(COMMON_PARAMS_KEYS)} common parameters "
            f"({', '.join(COMMON_PARAMS_KEYS)}), got {len(values)}"
        )

    p = dict(zip(COMMON_PARAMS_KEYS, values))
    for k in ("preamble_len", "crc_len", "payload_len", "oversampling"):
        p[k] = int(p[k])

    # --- Sync word: hex string → bit array ---
    # The sync word is passed as a hex string from GRC (e.g. "3E2A54B7").
    # All DSP blocks (modulator, correlator in parser, STO estimator) work
    # on individual bits, so the string is converted once here and stored as
    # a NumPy array of 0/1 integers, MSB-first.
    ######### SYNC WORD TRANSFORM ######################################################
    hex_string = p["sync_word"]  # Fonctionne aussi avec "3E" ou "3E2A54B7A1B2"
    # 1. Calcul dynamique du nombre de bits nécessaires (1 caractère hex = 4 bits)
    num_bits = len(hex_string) * 4
    # 2. Conversion et formatage dynamique
    # Nous utilisons une f-string imbriquée {num_bits} pour définir la taille
    bit_array = np.array([int(bit) for bit in f"{int(hex_string, 16):0>{num_bits}b}"])
    p["sync_word"] = bit_array
    ##########################################################################################

    # sync_word_len: number of bytes in the sync word (derived from bit array length)
    p["sync_word_len"] = int(len(p["sync_word"]) // 8)
    # hdr_len: total header = preamble bytes + sync word bytes
    # (the demodulator must pass this many bytes before the payload starts)
    p["hdr_len"] = p["preamble_len"] + p["sync_word_len"]
    # packet_len: full packet length in bytes (header + payload + CRC)
    p["packet_len"] = p["hdr_len"] + p["payload_len"] + p["crc_len"]
    return p


def timeit(fun: Callable[..., Any]) -> Callable[..., Any]:
    """
    Wrapper around a function and registers timing statistics about it.

    When the program exits (e.g., with CTRL + C), this utility
    will print short message with mean execution duration.

    Usage:

        Say you have a function definition:

        >>> def my_function(a, b):
        ...     pass

        You can simply use this utility as follows:

        >>> from .utils import timeit
        >>>
        >>> @timeit
        ... def my_function(a, b):
        ...     pass

    Note that you can use this decorator as many times as you want.
    """
    f_name = getattr(fun, "__name__", "<unnamed function>")
    data: list[float] = []

    def print_stats() -> None:
        mean = stats.mean(data)
        std = stats.stdev(data)
        print(
            f"{f_name} statistics: mean execution time of {mean:.2}s. (std: {std:.2}s.)"
        )

    @wraps(fun)
    def wrapper(*args, **kwargs):
        start = time()
        ret = fun(*args, **kwargs)
        end = time()
        data.append(end - start)
        return ret

    atexit.register(print_stats)

    return wrapper
