"""
classifier_zmq.py
ELEC PROJECT - 210x
Key given by Jerome : dhhnIfhwZxTJCv7135lIm3zFtr96r3H3_xtKXRxU
"""

import pickle
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import zmq
from classification.utils.plots import plot_specgram

# -----------------------------
# Configuration
# -----------------------------
project_root = Path(__file__).resolve().parents[2]
model_file = project_root / "classification" / "data" / "models" / "knn_model.pickle"
model = pickle.load(open(model_file, "rb"))

MELVEC_LENGTH = 20
N_MELVECS = 20
EXPECTED_LEN = 412  # header (4) + payload (400) + sécurité
dt = np.dtype(np.uint16).newbyteorder("<")

# ZMQ parameters
ZMQ_IP = "127.0.0.1"  # loopback si même PC
ZMQ_PORT = 10000        # doit correspondre au port du ZMQ Sink GNU Radio

# -----------------------------
# Fonction de classification
# -----------------------------
def classify_melvec(melvec, msg_counter):
    if len(melvec) < EXPECTED_LEN:
        print(f"Paquet trop court ignoré ({len(melvec)} éléments)")
        return

    print(f"--- Paquet #{msg_counter} reçu ---")

    # Extraction MEL payload et reshape
    mel_payload = melvec[4:404]
    mel_matrix = mel_payload.reshape((N_MELVECS, MELVEC_LENGTH))

    # Construction feature vector (mean + std + max)
    feat_mean = mel_matrix.mean(axis=1)
    feat_std  = mel_matrix.std(axis=1)
    feat_max  = mel_matrix.max(axis=1)[:10]
    feature_vector = np.concatenate([feat_mean, feat_std, feat_max]).reshape(1, -1)

    # Classification
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

    # Plot MEL spectrogram
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


# -----------------------------
# Main ZMQ loop
# -----------------------------
if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{ZMQ_IP}:{ZMQ_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")  # subscribe à tous les messages

    print(f"Listening for ZMQ messages on tcp://{ZMQ_IP}:{ZMQ_PORT} ...")
    msg_counter = 0

    while True:
        try:
            msg = socket.recv()  # reçoit le message en bytes
            melvec = np.frombuffer(msg, dtype=dt)
            msg_counter += 1
            classify_melvec(melvec, msg_counter)
        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except Exception as e:
            print("Error receiving or processing packet:", e)
