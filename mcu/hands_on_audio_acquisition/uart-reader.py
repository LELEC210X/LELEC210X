"""
uart-reader.py
FUSION: Audio Acquisition + CNN Classification (PC-side processing)
"""

import argparse
import sys
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import serial
import soundfile as sf
import librosa
from pathlib import Path
from serial.tools import list_ports
from datetime import datetime

# TensorFlow / Keras
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Réduit le bruit des logs TF
from tensorflow import keras

# --- CONFIGURATION ---
PRINT_PREFIX = "SND:HEX:"  # On écoute le prefixe RAW AUDIO (H2b)
FREQ_SAMPLING = 10200
VAL_MAX_ADC = 4096
VDD = 3.3

# Paramètres DSP (Doivent être proches de ceux utilisés pour l'entrainement)
N_MELS = 20
N_TIMESTEPS = 20 # Le CNN attend 20x20 = 400 features

# Chemins (Adaptés à ta structure)
project_root = Path(__file__).resolve().parents[2]
MODEL_PATH = project_root / "classification" / "data" / "models" / "models_cnn" / "best_model.h5"
METADATA_PATH = project_root / "classification" / "data" / "models" / "models_cnn" / "model_config.pkl"

# --- CHARGEMENT DU MODELE ---
print("Chargement du modèle CNN...", end="", flush=True)
try:
    model = keras.models.load_model(MODEL_PATH)
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    classnames = metadata["classnames"]
    print(f" OK. Classes: {classnames}")
except Exception as e:
    print(f"\nErreur chargement modèle: {e}")
    sys.exit(1)


def parse_buffer(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX) :])
    else:
        # Affiche les messages de debug (ex: "Hello World", "Button stop")
        print(f"[MCU] {line}")
        return None

def reader(port=None):
    ser = serial.Serial(port=port, baudrate=115200)
    print(f"Connecté à {port}. En attente de données...")
    while True:
        line = ""
        # Lecture ligne par ligne
        while not line.endswith("\n"):
            line += ser.read_until(b"\n", size=1042).decode("ascii", errors='ignore')
        
        line = line.strip()
        buffer = parse_buffer(line)
        
        if buffer is not None:
            # Conversion Raw Bytes -> Uint16
            dt = np.dtype(np.uint16).newbyteorder("<")
            buffer_array = np.frombuffer(buffer, dtype=dt)
            yield buffer_array

def generate_audio_file(buf, label):
    """
    Sauvegarde le fichier WAV dans audio_files/LABEL/acquisition_MOIS_JOUR_HEURE_MIN_SEC.wav
    """
    timestamp = datetime.now().strftime("%m_%d_%H_%M_%S")
    filename = f"acquisition_{timestamp}.wav"

    clean_label = "".join(x for x in str(label) if x.isalnum() or x in "._- ")
    folder_path = os.path.join("audio_files", clean_label)
    
    os.makedirs(folder_path, exist_ok=True)
    full_path = os.path.join(folder_path, filename)
    buf_float = np.asarray(buf, dtype=np.float64)
    buf_float = buf_float - np.mean(buf_float)
    max_val = max(abs(buf_float))
    if max_val > 0:
        buf_float /= max_val

    sf.write(full_path, buf_float, FREQ_SAMPLING)
    return full_path

def raw_to_mel_features(audio_buffer, sr):
    """
    Transforme l'audio brut en vecteur 400 (20x20) pour le CNN.
    Simule le DSP qui sera fait plus tard sur le MCU.
    """
    # 1. Normalisation du signal audio (comme pour le wav)
    y = np.array(audio_buffer, dtype=np.float32)
    y = y - np.mean(y)
    y = y / (np.max(np.abs(y)) + 1e-9)

    # 2. Calcul du Mel Spectrogramme avec Librosa
    # On ajuste hop_length pour essayer d'obtenir environ 20 frames temporelles
    # Ceci est une approximation.
    hop_length = len(y) // N_TIMESTEPS
    
    mels = librosa.feature.melspectrogram(
        y=y, 
        sr=sr, 
        n_mels=N_MELS, 
        n_fft=1024, 
        hop_length=hop_length,
        fmax=sr/2
    )
    
    # Convertir en dB (Log scale) car les modèles préfèrent souvent les log-mels
    mels_db = librosa.power_to_db(mels, ref=np.max)
    
    # 3. Redimensionnement forcé à 20x20 (Interpolation)
    # C'est nécessaire car la taille du buffer audio peut varier légèrement
    import scipy.ndimage
    zoom_factor = [N_MELS / mels_db.shape[0], N_TIMESTEPS / mels_db.shape[1]]
    mels_resized = scipy.ndimage.zoom(mels_db, zoom_factor, order=1)
    
    # S'assurer qu'on a bien 20x20 exactement
    mels_final = mels_resized[:N_MELS, :N_TIMESTEPS]
    
    # 4. Aplatir (Flatten) -> (400,)
    feature_vector = mels_final.flatten()
    
    # 5. Normalisation L2 (CRITIQUE pour le CNN)
    norm = np.linalg.norm(feature_vector)
    feature_vector = feature_vector / (norm + 1e-8)
    
    return feature_vector, mels_final

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--port", help="Port for serial communication")
    args = argParser.parse_args()

    if args.port is None:
        print("Ports disponibles :")
        for p in list(list_ports.comports()):
            print(f" - {p.device}")
        print("Usage: uv run uart-reader.py -p /dev/cu.usbmodem...")
    else:
        plt.ion() # Mode interactif pour le plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        plt.tight_layout(pad=4)
        
        input_stream = reader(port=args.port)
        msg_counter = 0
        for raw_audio in input_stream:
            msg_counter += 1
            print(f"\n--- Acquisition #{msg_counter} ---")

            # ETAPE 1 : D'ABORD LA PRÉDICTION (pour avoir le label)
            prediction = "unknown" # Valeur par défaut
            mel_matrix = np.zeros((20, 20)) # Valeur par défaut

            try:
                features, mel_matrix = raw_to_mel_features(raw_audio, FREQ_SAMPLING)
                
                # Reshape pour Keras (1, 400)
                input_tensor = features.reshape(1, -1)
                
                # Prédiction
                probabilities = model.predict(input_tensor, verbose=0)[0]
                pred_idx = np.argmax(probabilities)
                prediction = classnames[pred_idx]
                confidence = probabilities[pred_idx]
                
                print(f"--> PRÉDICTION CNN : {prediction} ({confidence:.1%})")
                
            except Exception as e:
                print(f"Erreur Classification: {e}")
                prediction = "error"

            # ETAPE 2 : ENSUITE LA SAUVEGARDE (dans le bon dossier)
            path = generate_audio_file(raw_audio, prediction)
            print(f"Audio sauvegardé : {path}")

            # ETAPE 3 : VISUALISATION (Inchangé)
            # ... (Laisse ton code de plot ici : ax1.clear(), ax2.clear()...)
            ax1.clear()
            times = np.linspace(0, len(raw_audio)/FREQ_SAMPLING, len(raw_audio))
            voltage_mV = raw_audio * VDD / VAL_MAX_ADC * 1e3
            ax1.plot(times, voltage_mV)
            ax1.set_title(f"Waveform") # Tu peux simplifier le titre
            
            ax2.clear()
            ax2.imshow(mel_matrix, origin='lower', aspect='auto', cmap='viridis')
            ax2.set_title(f"Class: {prediction}") # Affiche la classe prédite

            plt.draw()
            plt.pause(0.001)