import sys
import pickle
import numpy as np
import requests
from pathlib import Path
import tensorflow as tf
from tensorflow import keras

"""
Usage : uv run auth --tcp-address tcp://127.0.0.1:10000 --no-authenticate | uv run python classifier_pipe.py
"""

# --- CONFIGURATION ---
HOSTNAME = "http://localhost:5001" 
GROUP_KEY = "HEwRwpUXlF3aTkpQusc4bMa30NCxhqWnHnjuPu05"

# NOUVEAU: Chemins pour le modèle CNN
MODEL_PATH = "classification/data/models/cnn_linear_model.keras"
METADATA_PATH = "classification/data/models/cnn_model_metadata.pkl"
PRINT_PREFIX = "DF:HEX:" 

# --- CHARGEMENT DU MODÈLE CNN ---
try:
    # Charger le modèle Keras
    model = keras.models.load_model(MODEL_PATH)
    print(f"✅ Modèle CNN chargé depuis {MODEL_PATH}", file=sys.stderr)
    
    # Charger les métadonnées
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    classnames = metadata['classnames']
    print(f"✅ Classes: {classnames}", file=sys.stderr)
    
except FileNotFoundError as e:
    print(f"❌ Erreur: Impossible de trouver les fichiers du modèle", file=sys.stderr)
    print(f"   {e}", file=sys.stderr)
    sys.exit(1)

def submit_guess(guess):
    """Envoie la prédiction au serveur"""
    url = f"{HOSTNAME}/lelec210x/leaderboard/submit/{GROUP_KEY}/{guess}"
    
    try:
        response = requests.post(url, timeout=1.0)
        print("\n--- [DEBUG SERVEUR] ---", file=sys.stderr)
        print(f"Statut : {response.status_code} {response.reason}", file=sys.stderr)
        
        if response.ok:
            print(f"✅ Succès : '{guess}' bien enregistré.", file=sys.stderr)
        else:
            print(f"❌ Le serveur a répondu avec une erreur.", file=sys.stderr)
            print(f"   Réponse: {response.text}", file=sys.stderr)

    except requests.exceptions.Timeout:
        print("⏱️  Erreur : Le serveur met trop de temps à répondre.", file=sys.stderr)
    except Exception as e:
        print(f"❌ Erreur critique lors de l'envoi : {e}", file=sys.stderr)

def process_line(line):
    line = line.strip()
    if not line.startswith(PRINT_PREFIX):
        return

    hex_payload = line[len(PRINT_PREFIX):]
    
    try:
        # Décoder les données
        raw_bytes = bytes.fromhex(hex_payload)
        data = np.frombuffer(raw_bytes, dtype=np.dtype('<u2'))

        if len(data) != 400:
            print(f"⚠️  Taille incorrecte: {len(data)} != 400", file=sys.stderr)
            return

        # Reshape en matrice 20x20
        mel_matrix = data.reshape((20, 20))
        
        # NOUVEAU: Flatten et préparer pour le CNN
        feature_vector = mel_matrix.flatten()  # 400 dimensions
        
        # CRITIQUE: Normalisation L2 (comme pendant le training!)
        feature_vector_norm = feature_vector / (np.linalg.norm(feature_vector) + 1e-8)
        
        # Reshape pour le modèle: (1, 400)
        feature_vector_norm = feature_vector_norm.reshape(1, -1)
        
        # Prédiction avec le CNN
        probabilities = model.predict(feature_vector_norm, verbose=0)[0]
        predicted_idx = np.argmax(probabilities)
        predicted_class = classnames[predicted_idx]
        confidence = probabilities[predicted_idx]
        
        print(f"🎯 Son détecté : {predicted_class} (confiance: {confidence:.2%})", file=sys.stderr)
        print(f"   Probabilités: {dict(zip(classnames, probabilities))}", file=sys.stderr)
        
        # Soumettre seulement si confiance > seuil
        CONFIDENCE_THRESHOLD = 0.6
        if confidence >= CONFIDENCE_THRESHOLD:
            submit_guess(predicted_class)
        else:
            print(f"⚠️  Confiance trop faible ({confidence:.2%} < {CONFIDENCE_THRESHOLD:.0%}), pas de soumission", 
                  file=sys.stderr)

    except Exception as e:
        print(f"❌ Erreur traitement : {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

def main():
    print("="*60, file=sys.stderr)
    print("🎵 CLASSIFIER CNN EN TEMPS RÉEL", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"Modèle: {MODEL_PATH}", file=sys.stderr)
    print(f"Classes: {classnames}", file=sys.stderr)
    print("En attente de données depuis le pipe...", file=sys.stderr)
    print("="*60, file=sys.stderr)
    
    for line in sys.stdin:
        process_line(line)

if __name__ == "__main__":
    main()