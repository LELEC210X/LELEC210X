# data_types.py
from dataclasses import dataclass
import numpy as np
from typing import Optional

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
    time: np.ndarray
    metadata: ChannelMetadata
    processed_signal: Optional[np.ndarray] = None

    def __post_init__(self):
        if self.processed_signal is None:
            self.processed_signal = self.raw_signal.copy()