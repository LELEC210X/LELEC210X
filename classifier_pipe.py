import sys
import pickle
import numpy as np
import requests
import json
from pathlib import Path
from datetime import datetime

"""
Usage : uv run auth --tcp-address tcp://127.0.0.1:10000 --no-authenticate | uv run python classifier_pipe.py
"""

# --- CONFIGURATION ---
# local : "http://localhost:5001"
# pour les démos : "http://lelec210x.sipr.ucl.ac.be"
HOSTNAME = "http://localhost:5001" 
GROUP_KEY = "HEwRwpUXlF3aTkpQusc4bMa30NCxhqWnHnjuPu05" # local key
#GROUP_KEY = "dhhnIfhwZxTJCv7135lIm3zFtr96r3H3_xtKXRxU" # key for demos

MODEL_PATH = "classification/data/models/random_forest_model.pickle"
PRINT_PREFIX = "DF:HEX:" 

# --- NOUVEAU : Fichier pour sauvegarder les guesses ---
GUESS_FILE = "/tmp/latest_guess.json"

# Mode de fonctionnement
AUTO_SUBMIT = False  # Mettre à True pour envoyer automatiquement comme avant

# --- CHARGEMENT DU MODÈLE ---
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print(f"Modèle chargé depuis {MODEL_PATH}", file=sys.stderr)
except FileNotFoundError:
    print(f"Erreur: Impossible de trouver {MODEL_PATH}", file=sys.stderr)
    sys.exit(1)

def submit_guess(guess):
    """
    Envoie la prédiction au serveur et affiche les détails de la réponse.
    """
    url = f"{HOSTNAME}/lelec210x/leaderboard/submit/{GROUP_KEY}/{guess}"
    
    try:
        response = requests.post(url, timeout=1.0)
        print("\n--- [DEBUG SERVEUR] ---", file=sys.stderr)
        print(f"Statut : {response.status_code} {response.reason}", file=sys.stderr)
        print(f"Headers : {response.headers}", file=sys.stderr)
        print(f"Contenu brut (bytes) : {response.content}", file=sys.stderr)
        print(f"Texte décodé : {response.text}", file=sys.stderr)
        try:
            print(f"JSON : {response.json()}", file=sys.stderr)
        except Exception:
            pass
        print("------------------------\n", file=sys.stderr)

        # 200 signifie OK, 404 non trouvé, 401 erreur d'authentification (clé de groupe invalide ?), 500 erreur serveur, 400 son détecté pas authorisé
        if response.ok:
            print(f"Succès : '{guess}' bien enregistré.", file=sys.stderr)
            return True
        else:
            print(f"Le serveur a répondu avec une erreur.", file=sys.stderr)
            return False

    except requests.exceptions.Timeout:
        print("Erreur : Le serveur met trop de temps à répondre.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Erreur critique lors de l'envoi : {e}", file=sys.stderr)
        return False

def save_guess_to_file(guess):
    """
    Sauvegarde le guess dans un fichier JSON pour que l'interface Streamlit puisse le récupérer.
    """
    guess_data = {
        "value": guess,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "iso_timestamp": datetime.now().isoformat()
    }
    
    try:
        with open(GUESS_FILE, "w") as f:
            json.dump(guess_data, f, indent=2)
        print(f"💾 Guess '{guess}' sauvegardé dans {GUESS_FILE}", file=sys.stderr)
        print(f"📱 Ouvrez l'interface Streamlit pour l'envoyer manuellement", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}", file=sys.stderr)
        return False

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

        # Prédiction avec le modèle
        #prediction = model.predict(features)[0]
        # OU brutforce pour tester :
        prediction = "fire"
        
        print(f"🎵 Son détecté : {prediction}", file=sys.stderr)
        
        # Choisir le mode de fonctionnement
        if AUTO_SUBMIT:
            # Mode automatique (comme avant)
            submit_guess(prediction)
        else:
            # Mode manuel : sauvegarder dans un fichier
            save_guess_to_file(prediction)

    except Exception as e:
        print(f"Erreur traitement : {e}", file=sys.stderr)

def main():
    print("=" * 60, file=sys.stderr)
    print("🎮 LELEC210X Classifier Pipeline", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    if AUTO_SUBMIT:
        print("⚡ Mode : AUTO-SUBMIT (envoi automatique)", file=sys.stderr)
        print(f"🎯 Serveur : {HOSTNAME}", file=sys.stderr)
        print(f"🔑 Clé : {GROUP_KEY[:20]}...", file=sys.stderr)
    else:
        print("📋 Mode : MANUEL (sauvegarde dans fichier)", file=sys.stderr)
        print(f"📁 Fichier : {GUESS_FILE}", file=sys.stderr)
        print("💡 Utilisez l'interface Streamlit pour envoyer les guesses", file=sys.stderr)
    
    print("=" * 60, file=sys.stderr)
    print("En attente de données depuis le pipe...", file=sys.stderr)
    print("", file=sys.stderr)
    
    for line in sys.stdin:
        process_line(line)

if __name__ == "__main__":
    main()