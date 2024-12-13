# data_types.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

@dataclass
class ChannelMetadata:
    name: str
    probe_attenuation: float
    voltage_per_adc: float
    time_interval: float
    pk_pk: float
    frequency: Optional[float] = None
    period: Optional[float] = None

@dataclass
class SignalData:
    raw_signal: np.ndarray
    processed_signal: np.ndarray
    time: np.ndarray
    metadata: ChannelMetadata
    fft: Optional[np.ndarray] = None
    melspectrogram: Optional[np.ndarray] = None
    spectrogram: Optional[np.ndarray] = None