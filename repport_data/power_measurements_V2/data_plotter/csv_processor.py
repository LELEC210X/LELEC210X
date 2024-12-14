# csv_processor.py
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import logging
from data_types import ChannelMetadata, SignalData

logger = logging.getLogger(__name__)

class OscilloscopeCSVProcessor:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.metadata: Dict[str, ChannelMetadata] = {}
        self.signals: Dict[str, SignalData] = {}
        self._process_file()

    def _extract_value(self, text: str) -> float:
        """Extract numerical value from text with units"""
        if not text or text == '?' or text.strip() == '':
            return None
            
        multipliers = {
            'u': 1e-6,
            'm': 1e-3,
            'k': 1e3,
            'M': 1e6
        }
        
        # Remove units and get numerical value
        value_str = ''.join(c for c in text if c.isdigit() or c in '.-')
        try:
            value = float(value_str)
            # Apply multiplier if present
            for unit, mult in multipliers.items():
                if unit in text:
                    value *= mult
                    break
            return value
        except ValueError:
            return None

    def _process_file(self) -> None:
        try:
            with open(self.file_path, 'r') as f:
                header_lines = [f.readline().strip() for _ in range(7)]
                
            self.metadata = self._parse_metadata(header_lines)
            df = pd.read_csv(self.file_path, skiprows=8)
            
            for channel in self.metadata:
                time, voltage = self._extract_channel_data(df, channel)
                self.signals[channel] = SignalData(
                    raw_signal=voltage,
                    processed_signal=voltage.copy(),
                    time=time,
                    metadata=self.metadata[channel]
                )
                
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            raise

    def _parse_metadata(self, header_lines: List[str]) -> Dict[str, ChannelMetadata]:
        """Parse header metadata for each channel"""
        try:
            channels = {}
            # Get channel names from first line
            _, *channel_names = header_lines[0].strip().split(',')
            
            # Initialize metadata dict for each channel
            for ch_name in channel_names:
                channels[ch_name] = {
                    'name': ch_name,
                    'frequency': None,
                    'period': None,
                    'pk_pk': None,
                    'probe_attenuation': 1.0,
                    'voltage_per_adc': None,
                    'time_interval': None
                }
            
            # Parse each metadata line
            metadata_keys = ['Frequency', 'Period', 'PK-PK', 
                           'Probe attenuation', 'Voltage per ADC value',
                           'Time interval']
            
            for line in header_lines[1:7]:
                key, *values = line.strip().split(',')
                key = key.strip(' :')
                
                if key in metadata_keys:
                    for ch_name, value in zip(channel_names, values):
                        parsed_value = self._extract_value(value)
                        key_mapped = key.lower().replace(' ', '_')
                        channels[ch_name][key_mapped] = parsed_value

            # Create ChannelMetadata objects
            return {
                ch_name: ChannelMetadata(
                    name=ch_name,
                    probe_attenuation=metadata['probe_attenuation'],
                    voltage_per_adc=metadata['voltage_per_adc'],
                    time_interval=metadata['time_interval'],
                    pk_pk=metadata['pk_pk'],
                    frequency=metadata['frequency'],
                    period=metadata['period']
                ) for ch_name, metadata in channels.items()
            }
            
        except Exception as e:
            logger.error(f"Error parsing metadata: {str(e)}")
            raise

    def _extract_channel_data(self, df: pd.DataFrame, channel: str) -> tuple[np.ndarray, np.ndarray]:
        """Extract channel data from DataFrame"""
        voltage_column = f"{channel}_Voltage(mV)"
        if voltage_column not in df.columns:
            raise ValueError(f"Column {voltage_column} not found in CSV")
            
        voltage_data = df[voltage_column].values * 1e-3  # Convert mV to V
        time_data = np.arange(len(df)) * self.metadata[channel].time_interval
        return time_data, voltage_data