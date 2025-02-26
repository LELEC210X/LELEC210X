import os
import librosa
import numpy as np
import soundfile as sf
import random

# Input and output folders
input_folder = "soundfiles"
output_folder = "soundfiles_augmented"
os.makedirs(output_folder, exist_ok=True)

# Parameter: window size (in seconds)
frame_duration = 0.03  # 30 ms

# Iterate over all .wav files containing specific keywords
keywords = ['chainsaw', 'fire', 'fireworks', 'gun']

for file_name in os.listdir(input_folder):
    if file_name.endswith(".wav") and any(keyword in file_name for keyword in keywords):
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, file_name)

        # Load audio
        audio, sr = librosa.load(input_path, sr=None)

        # Compute window size in samples
        frame_size = int(sr * frame_duration)

        # Split audio into frames of 0.1s
        num_frames = len(audio) // frame_size

        # Compute the absolute mean of the entire signal
        global_mean = np.mean(np.abs(audio))

        # Store relevant frames
        trimmed_audio = []

        for i in range(num_frames):
            start = i * frame_size
            end = start + frame_size
            frame = audio[start:end]

            # Absolute mean of the frame
            frame_mean = np.mean(np.abs(frame))

            # Keep the frame if it is "significant"
            if frame_mean > (global_mean * 0.4):  # Adjustable threshold
                trimmed_audio.append(frame)

        # Reassemble the kept frames
        if trimmed_audio:
            final_audio = np.concatenate(trimmed_audio)
        else:
            final_audio = np.array([])  # Silence if everything was noise

        # Save the processed file
        if len(final_audio) > 0:
            sf.write(output_path, final_audio, sr)
            print(f"✔ {file_name} processed")
        else:
            print(f"✖ {file_name} ignored")

print("✅ Every file processed")


# Data augmentation
# Types of augmentations: 'pitch', 'noise', 'shift', 'stretch'
def augment_audio(audio, sr, type='pitch', factor=1.5):
    if type == 'pos_pitch' or type == 'neg_pitch':
        return librosa.effects.pitch_shift(y=audio, sr=sr, n_steps=factor)  # Corrected here
    elif type == 'noise':
        signal_power = np.mean(audio ** 2)
        noise_power = signal_power / 10  # SNR of 20dB means signal power is 10x noise power
        noise_std = np.sqrt(noise_power)
        noise = np.random.normal(0, noise_std, len(audio))
        return audio + noise
    elif type == 'shift':
        return np.roll(audio, int(len(audio) * random.randint(0,factor*1000)/1000))
    elif type == 'slow_stretch' or type == 'fast_stretch':
        return librosa.effects.time_stretch(y=audio, rate=factor)
    else:
        return audio

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Augmentation
augmentation_types = ['pos_pitch', 'neg_pitch', 'noise', 'shift', 'fast_stretch', 'slow_stretch']
augmentation_factors = [2, -2, 0.05, 1, 1.2, 0.7]

for file_name in os.listdir(input_folder):
    if file_name.endswith(".wav") and any(keyword in file_name for keyword in keywords):
        input_path = os.path.join(input_folder, file_name)

        # Load audio
        audio, sr = librosa.load(input_path, sr=None)

        for type, factor in zip(augmentation_types, augmentation_factors):
            augmented_audio = augment_audio(audio, sr, type, factor)
            output_path = os.path.join(output_folder, f"{file_name}_{type}.wav")
            sf.write(output_path, augmented_audio, sr)
            print(f"✔ {file_name} augmented with {type}")

print("✅ All files have been augmented.")
