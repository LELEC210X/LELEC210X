import json
import pickle
import sys
from datetime import datetime

import numpy as np
import requests
from tensorflow import keras

"""
Usage : uv run auth --tcp-address tcp://127.0.0.1:10000 --no-authenticate | uv run python classifier_pipe.py
"""

# --- CONFIGURATION ---
HOSTNAME = "http://localhost:5001"
GROUP_KEY = "HEwRwpUXlF3aTkpQusc4bMa30NCxhqWnHnjuPu05"
# GROUP_KEY = "dhhnIfhwZxTJCv7135lIm3zFtr96r3H3_xtKXRxU"

MODEL_PATH = "classification/data/models/models_cnn/best_model.h5"
METADATA_PATH = "classification/data/models/models_cnn/model_config.pkl"
PRINT_PREFIX = "DF:HEX:"
GUESS_FILE = "/tmp/latest_guess.json"

CONFIDENCE_THRESHOLD = 0.6
AUTO_SUBMIT = False

# --- CHARGEMENT DU MODELE ---
try:
    model = keras.models.load_model(MODEL_PATH)
    print(f"Modele CNN charge depuis {MODEL_PATH}", file=sys.stderr)
except FileNotFoundError:
    print(f"Erreur: Impossible de trouver {MODEL_PATH}", file=sys.stderr)
    sys.exit(1)

try:
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    classnames = metadata["classnames"]
    print(f"Classes: {classnames}", file=sys.stderr)
except FileNotFoundError:
    print(f"Erreur: Impossible de trouver {METADATA_PATH}", file=sys.stderr)
    sys.exit(1)


def submit_guess(guess):
    url = f"{HOSTNAME}/lelec210x/leaderboard/submit/{GROUP_KEY}/{guess}"
    try:
        response = requests.post(url, timeout=1.0)
        print("\n--- [DEBUG SERVEUR] ---", file=sys.stderr)
        print(f"Statut : {response.status_code} {response.reason}", file=sys.stderr)
        print(f"Headers : {response.headers}", file=sys.stderr)
        print(f"Contenu brut (bytes) : {response.content}", file=sys.stderr)
        print(f"Texte decode : {response.text}", file=sys.stderr)
        try:
            print(f"JSON : {response.json()}", file=sys.stderr)
        except Exception:
            pass
        print("------------------------\n", file=sys.stderr)

        if response.ok:
            print(f"Succes : '{guess}' bien enregistre.", file=sys.stderr)
            return True
        else:
            print("Le serveur a repondu avec une erreur.", file=sys.stderr)
            return False

    except requests.exceptions.Timeout:
        print("Erreur : Le serveur met trop de temps a repondre.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Erreur critique lors de l'envoi : {e}", file=sys.stderr)
        return False


def save_guess_to_file(guess, probabilities):
    """
    Sauvegarde le guess et le vecteur de probabilites dans un fichier JSON
    pour que l'interface Streamlit puisse le recuperer.
    """
    guess_data = {
        "value": guess,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "iso_timestamp": datetime.now().isoformat(),
        "probabilities": {
            classname: float(round(prob, 4))
            for classname, prob in zip(classnames, probabilities)
        },
        "confidence": float(round(np.max(probabilities), 4)),
    }

    try:
        with open(GUESS_FILE, "w") as f:
            json.dump(guess_data, f, indent=2)
        print(f"Guess '{guess}' sauvegarde dans {GUESS_FILE}", file=sys.stderr)
        print(
            "Ouvrez l'interface Streamlit pour l'envoyer manuellement", file=sys.stderr
        )
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}", file=sys.stderr)
        return False


def process_line(line):
    line = line.strip()
    if not line.startswith(PRINT_PREFIX):
        return

    hex_payload = line[len(PRINT_PREFIX) :]

    try:
        # Décoder les données
        # Décoder les données
        raw_bytes = bytes.fromhex(hex_payload)
        data = np.frombuffer(raw_bytes, dtype=np.dtype("<u2"))
        data = np.frombuffer(raw_bytes, dtype=np.dtype("<u2"))

        if len(data) != 400:
            print(f"Taille incorrecte: {len(data)} != 400", file=sys.stderr)
            return

        # Flatten du vecteur brut 20x20 = 400 dimensions
        feature_vector = data.astype(np.float32).flatten()

        # Normalisation L2 (identique au preprocessing d'entrainement)
        norm = np.linalg.norm(feature_vector)
        feature_vector = feature_vector / (norm + 1e-8)

        # Reshape pour le modele : (1, 400)
        feature_vector = feature_vector.reshape(1, -1)

        # Inference CNN
        probabilities = model.predict(feature_vector, verbose=0)[0]
        predicted_idx = np.argmax(probabilities)
        prediction = classnames[predicted_idx]
        confidence = probabilities[predicted_idx]

        # Affichage du vecteur de probabilites
        print(
            f"Son detecte : {prediction} (confiance: {confidence:.2%})", file=sys.stderr
        )
        print("Vecteur de probabilites :", file=sys.stderr)
        for classname, prob in zip(classnames, probabilities):
            bar = "#" * int(prob * 20)
            print(f"  {classname:<15}: {prob:.4f}  {bar}", file=sys.stderr)

        # Seuil de confiance
        if confidence < CONFIDENCE_THRESHOLD:
            print(
                f"Confiance insuffisante ({confidence:.2%} < {CONFIDENCE_THRESHOLD:.0%}), prediction ignoree.",
                file=sys.stderr,
            )
            return

        if AUTO_SUBMIT:
            submit_guess(prediction)
        else:
            save_guess_to_file(prediction, probabilities)

    except Exception as e:
        print(f"Erreur traitement : {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)


def main():
    print("=" * 60, file=sys.stderr)
    print("LELEC210X CNN Classifier Pipeline", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Modele  : {MODEL_PATH}", file=sys.stderr)
    print(f"Classes : {classnames}", file=sys.stderr)
    print(f"Seuil   : {CONFIDENCE_THRESHOLD:.0%}", file=sys.stderr)

    if AUTO_SUBMIT:
        print("Mode    : AUTO-SUBMIT", file=sys.stderr)
        print(f"Serveur : {HOSTNAME}", file=sys.stderr)
        print(f"Cle     : {GROUP_KEY[:20]}...", file=sys.stderr)
    else:
        print("Mode    : MANUEL (sauvegarde fichier)", file=sys.stderr)
        print(f"Fichier : {GUESS_FILE}", file=sys.stderr)

    print("=" * 60, file=sys.stderr)
    print("En attente de donnees depuis le pipe...", file=sys.stderr)

    for line in sys.stdin:
        process_line(line)


if __name__ == "__main__":
    main()
