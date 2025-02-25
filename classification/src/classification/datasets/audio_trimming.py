import os
import librosa
import numpy as np
import soundfile as sf

# Dossier d'entrée et de sortie
input_folder = "soundfiles_2"
output_folder = "soundfiles_3"
os.makedirs(output_folder, exist_ok=True)

# Paramètre : taille des fenêtres (en secondes)
frame_duration = 0.05  # 50 ms

# Parcourir tous les fichiers .wav
for file_name in os.listdir(input_folder):
    if file_name.endswith(".wav"):
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, file_name)

        # Charger l'audio
        audio, sr = librosa.load(input_path, sr=None)

        # Calculer la taille d'une fenêtre en samples
        frame_size = int(sr * frame_duration)

        # Découper l'audio en fenêtres de 0.1s
        num_frames = len(audio) // frame_size

        # Calculer la moyenne absolue du signal complet
        global_mean = np.mean(np.abs(audio))

        # Stocker les frames utiles
        trimmed_audio = []

        for i in range(num_frames):
            start = i * frame_size
            end = start + frame_size
            frame = audio[start:end]

            # Moyenne absolue de la frame
            frame_mean = np.mean(np.abs(frame))

            # Si la frame est "significative", on la garde
            if frame_mean > (global_mean * 0.9):  # Seuil ajustable
                trimmed_audio.append(frame)

        # Recombiner les frames conservées
        if trimmed_audio:
            final_audio = np.concatenate(trimmed_audio)
        else:
            final_audio = np.array([])  # Silence si tout était du bruit

        # Sauvegarde du fichier
        if len(final_audio) > 0:
            sf.write(output_path, final_audio, sr)
            print(f"✔ {file_name} traité et sauvegardé.")
        else:
            print(f"✖ {file_name} semble être que du silence, ignoré.")

print("✅ Tous les fichiers ont été traités.")
