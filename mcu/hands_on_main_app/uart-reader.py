"""
uart-reader.py
ELEC PROJECT - 210x
"""

import argparse
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import serial
from serial.tools import list_ports

from classification.utils.plots import plot_specgram


project_root = Path(__file__).resolve().parents[2]

model_file = project_root / "classification" / "data" / "models" / "knn_model.pickle"
model = pickle.load(open(model_file, "rb"))
print(model)
CLASSES = model.classes_ if hasattr(model, "classes_") else None

PRINT_PREFIX = "DF:HEX:"
FREQ_SAMPLING = 10200
MELVEC_LENGTH = 20
N_MELVECS = 20

dt = np.dtype(np.uint16).newbyteorder("<")


def parse_buffer(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX) :])
    else:
        print(line)
        return None


def reader(port=None):
    ser = serial.Serial(port=port, baudrate=115200)
    while True:
        line = ""
        while not line.endswith("\n"):
            line += ser.read_until(b"\n", size=2 * N_MELVECS * MELVEC_LENGTH).decode(
                "ascii"
            )
            print(line)
        line = line.strip()
        buffer = parse_buffer(line)
        if buffer is not None:
            buffer_array = np.frombuffer(buffer, dtype=dt)

            yield buffer_array


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--port", help="Port for serial communication")
    args = argParser.parse_args()
    print("uart-reader launched...\n")

    if args.port is None:
        print(
            "No port specified, here is a list of serial communication port available"
        )
        print("================")
        port = list(list_ports.comports())
        for p in port:
            print(p.device)
        print("================")
        print("Launch this script with [-p PORT_REF] to access the communication port")

    else:
        input_stream = reader(port=args.port)
        msg_counter = 0

        for melvec in input_stream:
            # On vérifie qu'on a bien reçu assez de données (412 éléments attendus)
            if len(melvec) < 412:
                print(f"Paquet trop court ignoré ({len(melvec)} éléments)")
                continue

            msg_counter += 1
            print(f"--- Paquet #{msg_counter} reçu ---")

            # --------------------------------------------
            # 1) Extraction et Reshape des données MEL
            # --------------------------------------------
            # Le header fait 8 octets (soit 4 éléments uint16)
            # La payload fait 800 octets (soit 400 éléments uint16)
            # On commence donc à l'indice 4 et on s'arrête à 4 + 400 = 404
            
            mel_payload = melvec[4:404]
            mel_matrix = mel_payload.reshape((N_MELVECS, MELVEC_LENGTH))

            # --------------------------------------------
            # 2) Build 50-feature vector (mean + std + max)
            # --------------------------------------------
            feat_mean = mel_matrix.mean(axis=1)          # 20 features
            feat_std  = mel_matrix.std(axis=1)           # 20 features
            feat_max  = mel_matrix.max(axis=1)[:10]      # 10 features

            feature_vector = np.concatenate(
                [feat_mean, feat_std, feat_max]
            ).reshape(1, -1)

            # --------------------------------------------
            # 3) Classifie avec votre modèle
            # --------------------------------------------
            try:
                prediction = model.predict(feature_vector)[0]
                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(feature_vector)[0]
                    confidence = np.max(proba)
                    print(f"Prediction: {prediction} ({confidence*100:.1f}% confidence)")
                else:
                    print(f"Prediction: {prediction}")
            except Exception as e:
                print("Error during classification:", e)

            # --------------------------------------------
            # 4) Plot MEL spectrogram
            # --------------------------------------------
            # On affiche la transposée pour avoir le temps en X et les fréquences en Y
            plot_specgram(
                mel_matrix.T,
                ax=plt.gca(),
                is_mel=True,
                title=f"MEL Spectrogram #{msg_counter}",
                xlabel="Mel vector",
            )
            plt.draw()
            plt.pause(0.001)
            plt.clf()