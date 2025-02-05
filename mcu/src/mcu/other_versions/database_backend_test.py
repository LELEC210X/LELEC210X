import logging
import os
import sys
from shutil import rmtree
import pathlib as pathl
import datetime
from threading import Lock
from typing import Optional
import time
from typing import Any, Optional, Dict, List, Type, Callable, Literal
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

@dataclass
class SerialPacket:
    """Class to store the serial packet data"""
    uid: int
    obtained_at: datetime.datetime
    prefix: None | str
    data: Any

@dataclass
class NormalPacket(SerialPacket):
    """Class to store the normal packet data"""
    data: Any

@dataclass
class AudioPacket(SerialPacket):
    """Class to store the audio packet data"""
    data: np.ndarray
    fft: np.ndarray

@dataclass
class MelPacket(SerialPacket):
    """Class to store the mel packet data"""
    data: np.ndarray
    mel_number: int
    mel_length: int
    has_cbc: bool

@dataclass
class SettingsPacket(SerialPacket):
    """Class to store the settings packet data"""
    data: Dict[str, Any]

class LimitedQueue:
    """Class to store a limited queue"""
    def __init__(self, type: Type, max_length: int):
        self.type = type
        self.max_length = max_length
        self.__list = [] # 0 is the latest element, -1 is the oldest element
        self.__lock = Lock()

    def change_max_length(self, new_max_length: int):
        """Change the maximum length of the list"""
        with self.__lock:
            if new_max_length < self.max_length:
                self.__list = self.__list[:new_max_length]
            self.max_length = new_max_length

    def push(self, element: Any):
        """Add an element to the list"""
        with self.__lock:
            if len(self.__list) >= self.max_length:
                self.__list.pop()
            self.__list.insert(0, element)

    def pop(self) -> Any:
        """Remove the last element of the list"""
        with self.__lock:
            if len(self.__list) > 0:
                return self.__list.pop()
        return None
    
    def get(self, index: int) -> Any:
        """Get the element at the index"""
        with self.__lock:
            if index < len(self.__list):
                return self.__list[index]
        return None
    
    def __iter__(self):
        with self.__lock:
            for element in self.__list:
                yield element

    def __len__(self):
        with self.__lock:
            return len(self.__list)
        
    def __getitem__(self, index: int):
        with self.__lock:
            return self.__list[index]
        
    def __setitem__(self, index: int, value: Any):
        with self.__lock:
            self.__list[index] = value

class BackendCallbacks:
    """Class to store the callbacks of the backend

    Attributes:
    __callbacks: Dict[str, Callable[[SerialPacket | dict], bool]
    encoded_type: Type

    The can accept dictionaries or SerialPackets as input, depending on the use of the callback
    """
    __callbacks: Dict[str, Callable[[SerialPacket | dict], bool]]
    encoded_type: Type

    def __init__(self, type: Type):
        self.__callbacks = {}
        self.encoded_type = type

    def connect(self, callback_name: str, callback: Callable[[SerialPacket | dict], bool]):
        """Connect a callback to the backend"""
        self.__callbacks[callback_name] = callback

    def disconnect(self, callback_name: str):
        """Disconnect a callback from the backend"""
        if callback_name in self.__callbacks:
            del self.__callbacks[callback_name]

    def process_all(self, data: List[SerialPacket | dict]):
        """Process all the data with the callbacks"""
        for packet in data:
            self.process(packet)

    def process(self, packet: SerialPacket | dict):
        """Process the data with the callbacks"""
        if isinstance(packet, self.encoded_type):
            for callback in self.__callbacks.values():
                callback(packet)
        elif isinstance(packet, dict):
            for callback in self.__callbacks.values():
                callback(packet)

    def __len__(self):
        return len(self.__callbacks)
    
    def __getitem__(self, key: str):
        return self.__callbacks[key]
    
    def __setitem__(self, key: str, value: Callable[[SerialPacket | dict], bool]):
        self.__callbacks[key] = value

    def __delitem__(self, key: str):
        del self.__callbacks[key]

    def __iter__(self):
        for key in self.__callbacks:
            yield key

    def __contains__(self, key: str):
        return key in self.__callbacks

class DatabaseBackend:
    """
    Class to store the database backend, and process the data independently of the frontend
    """
    normal_queue:     LimitedQueue
    audio_queue:      LimitedQueue
    mel_queue:        LimitedQueue
    settings_queue:   LimitedQueue

    __normal_uid_counter:   int
    __audio_uid_counter:    int
    __mel_uid_counter:      int
    __settings_uid_counter: int

    __configuration_callbacks: BackendCallbacks # Callbacks to process the configuration data of the backend when it changes configuration
    __audio_callbacks:         BackendCallbacks # Callbacks to process the audio data
    __mel_callbacks:           BackendCallbacks # Callbacks to process the mel data
    __settings_callbacks:      BackendCallbacks # Callbacks to process the settings data

    def __init__(self, normal_max_length: int, audio_max_length: int, mel_max_length: int, settings_max_length: int):
        self.__normal_uid_counter   = 0
        self.__audio_uid_counter    = 0
        self.__mel_uid_counter      = 0
        self.__settings_uid_counter = 0

        self.normal_queue         = LimitedQueue(NormalPacket, normal_max_length)
        self.audio_queue          = LimitedQueue(AudioPacket, audio_max_length)
        self.mel_queue            = LimitedQueue(MelPacket, mel_max_length)
        self.settings_queue       = LimitedQueue(SettingsPacket, settings_max_length)

        self.configuration_callbacks = BackendCallbacks(dict)
        self.audio_callbacks         = BackendCallbacks(AudioPacket)
        self.mel_callbacks           = BackendCallbacks(MelPacket)
        self.settings_callbacks      = BackendCallbacks(SettingsPacket)

    def change_max_length(self, 
            normal_max_length:   int | None = None, 
            audio_max_length:    int | None = None, 
            mel_max_length:      int | None = None,
            settings_max_length: int | None = None
            ):
        """Change the maximum length of the queues"""
        if normal_max_length is not None and normal_max_length >= 0:
            self.normal_queue.change_max_length(normal_max_length)
        if audio_max_length is not None and audio_max_length >= 0:
            self.audio_queue.change_max_length(audio_max_length)
        if mel_max_length is not None and mel_max_length >= 0:
            self.mel_queue.change_max_length(mel_max_length)
        if settings_max_length is not None and settings_max_length >= 0:
            self.settings_queue.change_max_length(settings_max_length) 
        self.configuration_callbacks.process_all({
            "normal_max_length": len(self.normal_queue),
            "audio_max_length": len(self.audio_queue),
            "mel_max_length":  len(self.mel_queue),
            "settings_max_length": len(self.settings_queue)
        })

    def push_audio(self, audio_data: np.ndarray, prefix: None | str = None):
        """Add an audio packet to the queue"""
        self.__audio_uid_counter += 1
        self.audio_queue.push(AudioPacket(
            uid=self.__audio_uid_counter,
            obtained_at=datetime.datetime.now(),
            prefix=prefix,
            data=audio_data,
            fft=np.fft.fft(audio_data)
        ))
        self.audio_callbacks.process(self.audio_queue[0])

    def push_mel(self, mel_data: np.ndarray, mel_number: int, mel_length: int, has_cbc: bool, prefix: None | str = None):
        """Add a mel packet to the queue"""
        self.__mel_uid_counter += 1
        self.mel_queue.push(MelPacket(
            uid=self.__mel_uid_counter,
            obtained_at=datetime.datetime.now(),
            prefix=prefix,
            data=mel_data[:-12] if has_cbc else mel_data,
            mel_number=mel_number,
            mel_length=mel_length,
            has_cbc=has_cbc
        ))
        self.mel_callbacks.process(self.mel_queue[0])

    def push_settings(self, settings_data: Dict[str, Any], prefix: None | str = None):
        """Add a settings packet to the queue"""
        self.__settings_uid_counter += 1
        self.settings_queue.push(SettingsPacket(
            uid=self.__settings_uid_counter,
            obtained_at=datetime.datetime.now(),
            prefix=prefix,
            data=settings_data
        ))
        self.settings_callbacks.process(self.settings_queue[0])

if __name__ == "__main__":
    db = DatabaseBackend(10, 10, 10, 10)
    db.push_audio(np.random.rand(1000))
    db.push_mel(np.random.rand(1000), 1, 1000, False)
    db.push_settings({"a": 1, "b": 2})
    db.change_max_length(5, 5, 5, 5)
    print("Done")
    