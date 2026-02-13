"""
ELEC PROJECT - 210x - Updated with Leaderboard Submission
"""

import argparse
import pickle
from pathlib import Path
import numpy as np
import serial
import requests  # <--- Ajouté pour le leaderboard
import matplotlib.pyplot as plt
from serial.tools import list_ports
from classification.utils.plots import plot_specgram

# --- CONFIGURATION LEADERBOARD ---
# Utilise 5001 si tu as suivi mon conseil précédent pour éviter le conflit AirPlay
HOSTNAME = "http://localhost:5000" 
# Remplace par la clé générée avec 'uv run leaderboard config generate-key "TonGroupe"'
GROUP_KEY = "5nL3LDIAtNr828vkOh9yzvMoY4CKEL7E6l122fv2" 

project_root = Path(__file__).resolve().parents[2]
model_file = project_root / "classification" / "data" / "models" / "knn_model.pickle"
model = pickle.load(open(model_file, "rb"))

PRINT_PREFIX = "DF:HEX:"
N_MELVECS = 20
MELVEC_LENGTH = 20

dt = np.dtype(np.uint16).newbyteorder("<")

def submit_guess(guess):
    """ Envoie la prédiction au serveur de leaderboard """
    url = f"{HOSTNAME}/lelec210x/leaderboard/submit/{GROUP_KEY}/{guess}"
    try:
        response = requests.post(url, timeout=1)
        if response.status_code == 200:
            print(f"Succès: '{guess}' envoyé au leaderboard.")
        else:
            print(f"Serveur a répondu avec l'erreur: {response.status_code}")
    except Exception as e:
        print(f"Erreur lors de l'envoi au leaderboard: {e}")

def parse_buffer(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX) :])
    else:
        # On affiche quand même les messages de debug du MCU
        if line: print(f"[MCU DEBUG] {line}")
        return None

def reader(port=None):
    ser = serial.Serial(port=port, baudrate=115200)
    while True:
        line = ser.readline().decode("ascii", errors="ignore")
        buffer = parse_buffer(line)
        if buffer is not None:
            yield np.frombuffer(buffer, dtype=dt)

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--port", help="Port for serial communication")
    args = argParser.parse_args()

    if args.port is None:
        print("Ports disponibles :", [p.device for p in list_ports.comports()])
        print("Relancez avec [-p PORT]")
    else:
        input_stream = reader(port=args.port)
        msg_counter = 0
        last_guess = None

        print(f"Lecture sur {args.port}... Envoi vers {HOSTNAME}")

        for melvec in input_stream:
            # Vérification de la taille (Header 4 uint16 + Payload 400 uint16 = 404)
            if len(melvec) < 404:
                continue

            msg_counter += 1
            
            # 1) Extraction et Reshape (On saute les 4 premiers uint16 du header)
            mel_payload = melvec[4:404]
            mel_matrix = mel_payload.reshape((N_MELVECS, MELVEC_LENGTH))

            # 2) Feature Engineering (Vérifie que c'est identique à ton entraînement !)
            feat_mean = mel_matrix.mean(axis=1)
            feat_std  = mel_matrix.std(axis=1)
            feat_max  = mel_matrix.max(axis=1)[:10]

            feature_vector = np.concatenate([feat_mean, feat_std, feat_max]).reshape(1, -1)

            # 3) Classification
            try:
                prediction = model.predict(feature_vector)[0]
                print(f"\n--- Paquet #{msg_counter} ---")
                print(f"Prediction: {prediction}")

                # 4) Envoi au leaderboard (On évite de renvoyer si c'est le même que le précédent)
                if prediction != last_guess:
                    submit_guess(prediction)
                    last_guess = prediction

            except Exception as e:
                print("Erreur classification:", e)

            # 5) Affichage optionnel
            plot_specgram(mel_matrix.T, ax=plt.gca(), is_mel=True, title=f"Détection: {prediction}")
            plt.draw()
            plt.pause(0.01)
            plt.clf()