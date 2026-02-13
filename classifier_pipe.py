import sys
import pickle
import numpy as np
import requests
from pathlib import Path

"""
Usage : uv run auth --tcp-address tcp://127.0.0.1:10000 --no-authenticate | uv run python classifier_pipe.py
"""

# --- CONFIGURATION ---
# local : "http://localhost:5001"
# pour les démos : "http://lelec210x.sipr.ucl.ac.be/lelec210x"
HOSTNAME = "http://lelec210x.sipr.ucl.ac.be" 
#GROUP_KEY = "kKAT5_L9VFTGS8mpQqcnKd_5JgkIyqDTUSYmaojK" # local key
GROUP_KEY = "dhhnIfhwZxTJCv7135lIm3zFtr96r3H3_xtKXRxU" # key for demos

MODEL_PATH = "classification/data/models/random_forest_model.pickle"
PRINT_PREFIX = "DF:HEX:" 

# --- CHARGEMENT DU MODÈLE ---
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print(f"Modèle chargé depuis {MODEL_PATH}", file=sys.stderr)
except FileNotFoundError:
    print(f"Erreur: Impossible de trouver {MODEL_PATH}", file=sys.stderr)
    sys.exit(1)

def submit_guess(guess):
    """Envoie la réponse au serveur"""
    url = f"http://lelec210x.sipr.ucl.ac.be/lelec210x/leaderboard/submit/{GROUP_KEY}/{guess}"
    try:
        guess1 = requests.post(url, timeout=0.5)
        print("guess1:",guess1.content)
        print(f"Envoyé au serveur : {guess}", file=sys.stderr)
    except Exception as e:
        print(f"Erreur envoi serveur : {e}", file=sys.stderr)

def process_line(line):
    line = line.strip()
    if not line.startswith(PRINT_PREFIX):
        return

    hex_payload = line[len(PRINT_PREFIX):]
    
    try:
        raw_bytes = bytes.fromhex(hex_payload)
        data = np.frombuffer(raw_bytes, dtype=np.dtype('<u2')) 

        if len(data) != 400:
            return

        mel_matrix = data.reshape((20, 20))
        
        feat_mean = mel_matrix.mean(axis=1)
        feat_std  = mel_matrix.std(axis=1)
        feat_max  = mel_matrix.max(axis=1)[:10]
        
        features = np.concatenate([feat_mean, feat_std, feat_max]).reshape(1, -1)

        prediction = model.predict(features)[0]
        print(f"Son détecté : {prediction}", file=sys.stderr)
        submit_guess(prediction)

    except Exception as e:
        print(f"Erreur traitement : {e}", file=sys.stderr)

def main():
    print("En attente de données depuis le pipe...", file=sys.stderr)
    for line in sys.stdin:
        process_line(line)

if __name__ == "__main__":
    main()