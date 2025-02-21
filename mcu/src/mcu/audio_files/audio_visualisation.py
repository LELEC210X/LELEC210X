import librosa
import numpy as np
import librosa.display
import matplotlib.pyplot as plt

# Charger le fichier audio
filename = "audio_6.wav"
y, sr = librosa.load(filename, sr=None)  # sr=None pour conserver le taux d'échantillonnage original
start = int(1.5 * 10200)
print(sr)
y = y[start:] # skip the first second

# threshold = np.mean(y)
# start_index = np.argmax(np.abs(y) > 0.5)
# print(start_index)
# y = y[start_index:]

# Tracer l'onde sonore
plt.figure(figsize=(10, 4))
librosa.display.waveshow(y, sr=sr)
plt.xlabel("Temps (s)")
plt.ylabel("Amplitude")
plt.title("Waveform de l'audio")
plt.show()