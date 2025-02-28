import librosa
import numpy as np
import librosa.display
import matplotlib.pyplot as plt
from scipy.fft import fft
import scipy.signal as sg


# Charger le fichier audio
filename = "audio_6.wav"
y, sr = librosa.load(filename, sr=None)  # sr=None pour conserver le taux d'échantillonnage original
start = int(1.5 * 10200)
print(sr) #sr = 10200
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



# load "Clap sound effect [sXRRSaM2uJ4].wav"
filename = "Clap sound effect [sXRRSaM2uJ4].wav"
y_2, sr_2 = librosa.load(filename, sr=None)  # sr=None pour conserver le taux d'échantillonnage original
print(sr_2)
# Tracer l'onde sonore
# plt.figure(figsize=(10, 4))
# librosa.display.waveshow(y_2, sr=sr_2)
# plt.xlabel("Temps (s)")
# plt.ylabel("Amplitude")
# plt.title("Waveform de l'audio")
# plt.show()

# Tracer l'onde sonore
# plt.figure(figsize=(10, 4))
# librosa.display.waveshow(y, sr=None)
# plt.xlabel("Temps (s)")
# plt.ylabel("Amplitude")
# plt.title("Waveform de l'audio")
# plt.show()

y_3 = sg.resample_poly(y_2, 17, 80)

# Tracer l'onde sonore
plt.figure(figsize=(10, 4))
librosa.display.waveshow(y_3[1438:], sr=sr)
plt.xlabel("Temps (s)")
plt.ylabel("Amplitude")
plt.title("Waveform de l'audio")
# plt.show()

y_3 = y_3[1438:]
index_max_3 = y_3.argmax()
print(index_max_3)
index_max = y.argmax()
print(index_max)



# compute the FFT of the signal using scipy, we will then divide the FFT of another .wav file by this FFT to get the transfer function
from scipy.fft import fft, ifft
import scipy.signal as sg
n_fft = y_3.size
spect = fft(y[:n_fft])

spect_3 = fft(y_3[:n_fft])
impulse_resp = ifft(spect/spect_3)
np.save("impulse_resp_array.npy", impulse_resp.real)
print(impulse_resp.size)
print(impulse_resp)

plt.figure(figsize=(10, 4))
librosa.display.waveshow(impulse_resp.real, sr=sr)
plt.xlabel("Temps (s)")
plt.ylabel("Amplitude")
plt.title("Waveform de l'impulse response")
plt.show()


#plot spect and spect_3
plt.figure(figsize=(10, 4))
plt.plot(np.abs(spect), label="spect")
plt.plot(np.abs(spect_3), label="spect_3")
plt.legend()
plt.show()
