"""
Test file, provided to easily check your implementations.

Run it from the radioconda prompt (Windows), or a terminal (Linux) at the root of the repository:

    python tests/test_chain.py

For this to work, the Python used for the execution must have GNU Radio installed.
This is why you must execute this from the radioconda prompt if you are on Windows.
"""

import importlib
import sys
import traceback
import types
from pathlib import Path

import numpy as np

# =============================================================================
# Load the block sources from python/
# =============================================================================

SRC_DIR = Path(__file__).resolve().parents[1] / "python"
_PKG = "_lelec210x_src"

if _PKG not in sys.modules:
    _pkg = types.ModuleType(_PKG)
    _pkg.__path__ = [str(SRC_DIR)]
    sys.modules[_PKG] = _pkg

packet_generator = importlib.import_module(f"{_PKG}.packet_generator")
demodulation = importlib.import_module(f"{_PKG}.demodulation")
synchronization = importlib.import_module(f"{_PKG}.synchronization")


# =============================================================================
# Parameters: same default values as in apps/Project_LELEC210X.grc
# =============================================================================

B = 50e3  # Data rate [bit/s]
FDEV = B / 2  # Frequency deviation [Hz]
FSAMP = 400e3  # Receiver sampling frequency [Hz]
R = int(FSAMP / B)  # Oversampling factor
N_MOOSE = 2  # Number of symbols per block in the Moose algorithm

PREAMBLE = np.array([int(bit) for bit in f"{0xAA:0>8b}"] * 4)  # 4 bytes 0xAA
SYNC_WORD = np.array([int(bit) for bit in f"{0x3E2A54B7:0>32b}"])


def add_cfo(x: np.ndarray, cfo: float) -> np.ndarray:
    """Add a CFO of `cfo` Hz, as done in packet_generator.general_work()."""
    n = np.arange(len(x))
    return x * np.exp(1j * 2 * np.pi * cfo * n / FSAMP).astype(np.complex64)


# =============================================================================
# Tests
# =============================================================================


def test_demodulate(size):
    rng = np.random.default_rng(1234)
    bits = rng.integers(2, size=size)  # Bits to send

    y = packet_generator.modulate(bits, B, R, FDEV)  # Ideal channel
    bits_hat = demodulation.demodulate(y, B, R, FDEV)

    np.testing.assert_equal(bits_hat, bits)


def test_cfo_estimation(size, cfo):
    rng = np.random.default_rng(1234)
    bits = rng.integers(2, size=size)  # Payload bits
    x = packet_generator.modulate(
        np.concatenate((PREAMBLE, SYNC_WORD, bits)), B, R, FDEV
    )

    y = add_cfo(x, cfo)  # Ideal channel + CFO
    cfo_hat = synchronization.cfo_estimation(y, B, R, FDEV, N_MOOSE)

    np.testing.assert_allclose(cfo_hat, cfo, rtol=1e-3, atol=1.0)


def main() -> int:
    cases = []
    for size in (1, 10, 100):
        cases.append((test_demodulate, {"size": size}))
    for size in (1, 10, 100):
        for cfo in (0, 100, 1000):
            cases.append((test_cfo_estimation, {"size": size, "cfo": cfo}))

    n_failed = 0
    for test, kwargs in cases:
        label = f"{test.__name__}({', '.join(f'{k}={v}' for k, v in kwargs.items())})"
        try:
            test(**kwargs)
            print(f"PASS  {label}")
        except Exception:
            n_failed += 1
            print(f"FAIL  {label}")
            print("      " + traceback.format_exc().strip().replace("\n", "\n      "))

    print(f"\n{len(cases) - n_failed}/{len(cases)} tests passed")
    return 1 if n_failed else 0


if __name__ == "__main__":
    sys.exit(main())
