import os
import librosa
import numpy as np
import soundfile as sf
import random
import scipy.signal

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
        
        # Load audio
        audio, sr = librosa.load(input_path, sr=None)

        # Compute window size in samples
        frame_size = int(sr * frame_duration)

        # Compute the absolute mean of the entire signal
        global_mean = np.mean(np.abs(audio))

        # Store relevant frames
        trimmed_audio = []

        for i in range(len(audio) // frame_size):
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
            sf.write(os.path.join(output_folder, file_name), final_audio, sr)
            print(f"✔ {file_name} processed")
        else:
            print(f"✖ {file_name} ignored")

print("✅ Every file processed")

# Data augmentation
def augment_audio(audio, sr, type='pitch', factor=1.5):
    if type == 'pos_pitch' or type == 'neg_pitch':
        return librosa.effects.pitch_shift(y=audio, sr=sr, n_steps=factor)
    elif type == 'noise':
        signal_power = np.mean(audio ** 2)
        noise_power = signal_power / 10
        noise_std = np.sqrt(noise_power)
        noise = np.random.normal(0, noise_std, len(audio))
        return audio + noise
    elif type == 'shift':
        return np.roll(audio, int(len(audio) * random.uniform(0, factor) / 1000))
    elif type == 'slow_stretch' or type == 'fast_stretch':
        return librosa.effects.time_stretch(y=audio, rate=factor)
    else:
        return audio

# Augmentation
augmentation_types = ['pos_pitch', 'neg_pitch', 'noise', 'shift', 'fast_stretch', 'slow_stretch']
augmentation_factors = [2, -2, 0.05, 1, 1.2, 0.7]

for file_name in os.listdir(output_folder):
    if file_name.endswith(".wav"):
        input_path = os.path.join(output_folder, file_name)
        
        # Load audio
        audio, sr = librosa.load(input_path, sr=None)
        
        for type, factor in zip(augmentation_types, augmentation_factors):
            augmented_audio = augment_audio(audio, sr, type, factor)
            new_name = f"{os.path.splitext(file_name)[0]}_{type}.wav"
            sf.write(os.path.join(output_folder, new_name), augmented_audio, sr)
            print(f"✔ {file_name} augmented with {type}")

print("✅ All files have been augmented.")

# # Convolution with impulse response
# impulse_response_path = "Impulse_response.wav"
# impulse_response, sr_ir = librosa.load(impulse_response_path, sr=None)
# 
# for file_name in os.listdir(output_folder):
#     if file_name.endswith(".wav"):
#         input_path = os.path.join(output_folder, file_name)
#         
#         # Load audio
#         audio, sr = librosa.load(input_path, sr=None)
# 
#         # Resample impulse response if necessary
#         if sr != sr_ir:
#             impulse_response = librosa.resample(impulse_response, orig_sr=sr_ir, target_sr=sr)
#             sr_ir = sr
# 
#         # Convolve audio with impulse response
#         convolved_audio = scipy.signal.fftconvolve(audio, impulse_response, mode='full')
# 
#         # Save convolved audio with a clean name
#         clean_name = f"{os.path.splitext(file_name)[0]}_convolved.wav"
#         sf.write(os.path.join(output_folder, clean_name), convolved_audio, sr)
#         
#         # Remove original non-convolved files
#         os.remove(input_path)
#         print(f"✔ {file_name} convolved and saved as {clean_name}")
# 
# print("✅ All files have been convolved and cleaned.")


# Directory containing the audio files
directory = "soundfiles_augmented"

# File categories
classes = ['chainsaw', 'fireworks', 'fire', 'gun']

# Retrieve and sort the files
files = sorted(f for f in os.listdir(directory) if f.endswith(".wav"))

# Dictionary to store the counter for each class
counters = {cls: 0 for cls in classes}

# Rename the files
for file in files:
    for cls in classes:
        if file.startswith(cls):
            new_name = f"{cls}_{counters[cls]:03d}.wav"
            old_path = os.path.join(directory, file)
            new_path = os.path.join(directory, new_name)
            os.rename(old_path, new_path)
            counters[cls] += 1
            print(f"Renamed: {file} -> {new_name}")
            break
