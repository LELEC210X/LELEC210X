"""
classifier.py
ELEC PROJECT - 210x
Adapté pour recevoir les feature vectors directement depuis GNU Radio / LimeSDR sur le même PC
"""

import pickle
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from classification.utils.plots import plot_specgram

# -----------------------------
# Configuration
# -----------------------------
project_root = Path(__file__).resolve().parents[2]
model_file = project_root / "classification" / "data" / "models" / "knn_model.pickle"
model = pickle.load(open(model_file, "rb"))

MELVEC_LENGTH = 20
N_MELVECS = 20
dt = np.dtype(np.uint16).newbyteorder("<")
EXPECTED_LEN = 412  # header (4) + payload (400) + sécurité

# -----------------------------
# Fonction principale
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
# Exemple d'utilisation
# -----------------------------
if __name__ == "__main__":
    import time

    # Simulation : générer un paquet aléatoire (pour test)
    msg_counter = 0
    while True:
        # Ici, remplace cette ligne par le flux réel venant de GNU Radio
        melvec = np.random.randint(0, 65535, EXPECTED_LEN, dtype=np.uint16)

        msg_counter += 1
        classify_melvec(melvec, msg_counter)

        time.sleep(0.1)  # pour simuler un flux de paquets
