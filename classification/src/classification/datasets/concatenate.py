from pydub import AudioSegment
import os

# Directory containing the .wav files
input_directory = "./"

# Output file name
output_file = "concatenated_birds.wav"

# Collect only birds_XX.wav files in the directory
wav_files = [f for f in sorted(os.listdir(input_directory)) if f.startswith('birds_') and f.endswith('.wav')]

# Ensure the files are sorted numerically if named like birds_00.wav
wav_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

# Initialize an empty AudioSegment
combined = AudioSegment.empty()

# Iterate and concatenate the files
for wav_file in wav_files:
    print(f"Processing {wav_file}...")
    audio = AudioSegment.from_wav(os.path.join(input_directory, wav_file))
    combined += audio

# Export the concatenated audio
combined.export(output_file, format="wav")
print(f"All files concatenated into {output_file}.")
