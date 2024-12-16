# signal_processor.py
import numpy as np
import librosa
from typing import Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from data_types import SignalData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalProcessor:
    def __init__(self, signal_data: SignalData):
        self.signal_data = signal_data
        self._validate_data()

    def _validate_data(self) -> None:
        """Validate signal data arrays"""
        if not hasattr(self.signal_data, 'time') or not hasattr(self.signal_data, 'raw_signal'):
            raise ValueError("Signal data missing required attributes")
        
        # Initialize processed_signal if needed
        if not hasattr(self.signal_data, 'processed_signal') or self.signal_data.processed_signal is None:
            self.signal_data.processed_signal = self.signal_data.raw_signal.copy()
        
        # Ensure arrays are non-empty
        if len(self.signal_data.raw_signal) == 0:
            raise ValueError("Signal data cannot be empty")
            
        # Realign arrays if needed
        min_len = min(len(self.signal_data.processed_signal), len(self.signal_data.time))
        self.signal_data.processed_signal = self.signal_data.processed_signal[:min_len]
        self.signal_data.time = self.signal_data.time[:min_len]

    def _trim_signal(self, signal: np.ndarray, time: np.ndarray, 
                    start_trim: int = 0, end_trim: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        """Trim signal and time arrays"""
        if end_trim == 0:
            return signal[start_trim:], time[start_trim:]
        return signal[start_trim:-end_trim], time[start_trim:-end_trim]

    def _apply_moving_average(self, signal: np.ndarray, window_size: int = 1) -> np.ndarray:
        """Apply moving average filter to signal"""
        if window_size <= 1 or len(signal) == 0:
            return signal
            
        if len(signal) < window_size:
            window_size = len(signal)
            
        window = np.ones(window_size) / window_size
        return np.convolve(signal, window, mode='valid')

    def _apply_offsets(self, signal: np.ndarray, time: np.ndarray,
                      voltage_offset: float = 0.0, time_offset: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """Apply voltage and time offsets"""
        return signal - voltage_offset, time - time_offset

    def _apply_scaling(self, signal: np.ndarray, time: np.ndarray,
                      voltage_scale: float = 1.0, time_scale: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """Apply voltage and time scaling"""
        return signal * voltage_scale, time * time_scale

    def process_signal(self, start_trim: int = 0, end_trim: int = 0, 
                      window_size: int = 1, voltage_offset: float = 0.0, 
                      time_offset: float = 0.0, voltage_scale: float = 1.0, 
                      time_scale: float = 1.0) -> None:
        """Process signal with given parameters"""
        try:
            # Validate and get initial arrays
            self._validate_data()
            processed = self.signal_data.raw_signal.copy()
            time = self.signal_data.time.copy()

            if len(processed) == 0:
                return

            # Apply trimming
            total_points = len(processed)
            start_idx = min(int((start_trim / 100) * total_points), total_points-1)
            end_idx = min(int((end_trim / 100) * total_points), total_points)
            
            if start_idx >= end_idx:
                start_idx = 0
                end_idx = total_points
            
            if end_idx > start_idx:
                processed = processed[start_idx:end_idx]
                time = time[start_idx:end_idx]
                # Reset time to start at 0
                time = time - time[0]
            
            # Apply voltage offset and scaling
            processed = (processed - voltage_offset) * voltage_scale
            
            # Apply smoothing
            if window_size > 1 and len(processed) > window_size:
                processed = self._apply_moving_average(processed, window_size)
                time = time[:len(processed)]
            
            # Apply time offset last
            time = time + time_offset

            self.signal_data.processed_signal = processed
            self.signal_data.time = time

        except Exception as e:
            logger.error(f"Error processing signal: {str(e)}")
            raise

    def _update_spectrograms(self) -> None:
        """Update all spectral representations"""
        try:
            self.signal_data.fft = np.fft.fft(self.signal_data.processed_signal)
            self.signal_data.melspectrogram = librosa.feature.melspectrogram(
                y=self.signal_data.processed_signal, 
                sr=1/(self.signal_data.time[1] - self.signal_data.time[0])
            )
            self.signal_data.spectrogram = np.abs(librosa.stft(self.signal_data.processed_signal))
        except Exception as e:
            logger.error(f"Error computing spectrograms: {str(e)}")
            raise