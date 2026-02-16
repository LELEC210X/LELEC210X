import streamlit as st
import requests
import json
from datetime import datetime
import time
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="LELEC210X Leaderboard", page_icon="🎮", layout="wide")

# --- INITIALISATION SESSION STATE ---
if 'guess_queue' not in st.session_state:
    st.session_state.guess_queue = []
if 'total_submitted' not in st.session_state:
    st.session_state.total_submitted = 0
if 'mode' not in st.session_state:
    st.session_state.mode = "user"

st.title("LELEC210X Leaderboard Controller")
st.markdown("Interface complète pour le serveur de compétition.")

# --- SIDEBAR : CONNEXION ---
with st.sidebar:
    st.header("Connexion")
    
    # Mode selection
    mode = st.radio("Mode", ["Utilisateur", "Admin"], index=0 if st.session_state.mode == "user" else 1)
    st.session_state.mode = "user" if mode == "Utilisateur" else "admin"
    
    st.markdown("---")
    
    # Configuration de l'URL et du Port
    col_ip, col_port = st.columns([2, 1])
    host = col_ip.text_input("Host", value="localhost")
    port = col_port.text_input("Port", value="5001")
    
    base_url = f"http://{host}:{port}/lelec210x/leaderboard"
    
    st.markdown("---")
    
    # Clé (admin ou normale selon le mode)
    key_label = "Clé Admin" if st.session_state.mode == "admin" else "Clé du Groupe"
    api_key = st.text_input(key_label, type="password", help="La clé générée pour votre groupe")
    
    if not api_key:
        st.warning(f"Veuillez entrer une clé pour activer les fonctionnalités.")
    
    st.markdown("---")
    
    # Test de connexion
    if st.button("🔍 Tester la connexion", use_container_width=True):
        if api_key:
            try:
                r = requests.get(f"{base_url}/check/{api_key}", timeout=2)
                if r.status_code == 200:
                    st.success("✅ Connexion réussie !")
                    st.json(r.json())
                elif r.status_code == 401:
                    st.error("❌ Clé invalide")
                else:
                    st.error(f"Erreur {r.status_code}")
            except requests.exceptions.ConnectionError:
                st.error(f"Impossible de se connecter à {base_url}")
            except Exception as e:
                st.error(f"Erreur: {e}")
        else:
            st.warning("Veuillez entrer une clé")

# --- FONCTIONS UTILITAIRES ---
def send_request(method, endpoint, success_msg="Action réussie !", show_response=False):
    """Envoie une requête à l'API et gère l'affichage."""
    url = f"{base_url}{endpoint}"
    try:
        if method == "POST":
            r = requests.post(url, timeout=5)
        elif method == "GET":
            r = requests.get(url, timeout=5)
        elif method == "PATCH":
            r = requests.patch(url, timeout=5)
        elif method == "DELETE":
            r = requests.delete(url, timeout=5)
        
        # Gestion des erreurs détaillée
        if r.status_code == 200:
            st.success(success_msg)
            response_data = r.json() if r.content else {"status": "success"}
            if show_response:
                st.json(response_data)
            return response_data
        elif r.status_code == 400:
            st.error("Erreur 400 : Requête invalide ou soumissions non autorisées")
            try:
                st.json(r.json())
            except:
                st.code(r.text)
        elif r.status_code == 401:
            st.error("Erreur 401 : Clé invalide")
        elif r.status_code == 403:
            st.error("Erreur 403 : Non autorisé (droits admin requis)")
        elif r.status_code == 404:
            st.error("Erreur 404 : Ressource non trouvée")
        elif r.status_code == 500:
            st.error("Erreur 500 : Erreur serveur")
            try:
                st.json(r.json())
            except:
                st.code(r.text)
        else:
            st.error(f"Erreur {r.status_code}")
            st.code(r.text)
            
    except requests.exceptions.Timeout:
        st.error(f"Timeout : Le serveur met trop de temps à répondre")
    except requests.exceptions.ConnectionError:
        st.error(f"Impossible de se connecter au serveur sur {base_url}")
    except Exception as e:
        st.error(f"Erreur : {e}")
    
    return None

def load_guess_from_file(filepath="/tmp/latest_guess.json"):
    """Charge le dernier guess depuis un fichier JSON."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get('value'), data.get('timestamp')
    except Exception as e:
        st.warning(f"Erreur lecture fichier: {e}")
    return None, None

# --- INTERFACE PRINCIPALE ---

if not api_key:
    st.info("Veuillez entrer votre clé dans la barre latérale pour commencer.")
    st.stop()

# ========================================
# MODE ADMIN
# ========================================
if st.session_state.mode == "admin":
    
    # 1. STATUS & MONITORING
    st.header("État du serveur")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Actualiser le statut", use_container_width=True):
            status_data = send_request("GET", f"/status/{api_key}", "Statut mis à jour", show_response=True)
    
    with col2:
        # Auto-refresh option
        auto_refresh = st.checkbox("Auto-refresh (5s)")
        if auto_refresh:
            st.info("Actualisation automatique activée")
            time.sleep(5)
            st.rerun()

    st.markdown("---")

    # 2. CONTRÔLE DE LA PARTIE (PLAY / PAUSE / RESTART)
    st.header("⏯Contrôle de la Partie")
    
    col_play, col_pause, col_restart = st.columns(3)
    
    with col_play:
        if st.button("▶ PLAY", use_container_width=True, type="primary"):
            send_request("POST", f"/play/{api_key}", "✅ La partie a démarré !")
            
    with col_pause:
        if st.button("⏸ PAUSE", use_container_width=True):
            send_request("POST", f"/pause/{api_key}", "⏸️ La partie est en pause")
            
    with col_restart:
        if st.button("RESTART", use_container_width=True, type="secondary"):
            st.warning("⚠️ Confirmez le redémarrage ci-dessous")

    # Confirmation pour restart
    if st.checkbox("✅ Confirmer le redémarrage de la partie"):
        if st.button("🔴 REDÉMARRER MAINTENANT", type="primary"):
            send_request("POST", f"/restart/{api_key}", "🔄 La partie a redémarré !")

    st.markdown("---")

    # 3. GESTION DES ÉQUIPES (RENAME)
    st.header("✏️ Renommer une équipe")
    
    with st.form("rename_form"):
        new_name = st.text_input("Nouveau nom d'équipe")
        submitted = st.form_submit_button("💾 Renommer", use_container_width=True)
        
        if submitted and new_name:
            import urllib.parse
            safe_name = urllib.parse.quote(new_name)
            send_request("PATCH", f"/rename/{api_key}/{safe_name}", f"✅ Équipe renommée en '{new_name}'")

    st.markdown("---")

    # 4. RÉSULTATS
    st.header("🏆 Résultats du Contest")
    
    if st.button("Obtenir les résultats", use_container_width=True):
        results = send_request("POST", f"/results/{api_key}", "Résultats récupérés", show_response=True)

# ========================================
# MODE UTILISATEUR
# ========================================
else:
    
    # 1. DÉTECTION ET FILE D'ATTENTE
    st.header("🎯 Gestion des Guesses")
    
    tab1, tab2 = st.tabs(["Nouveau Guess", "File d'attente"])
    
    with tab1:
        st.subheader("Ajouter un guess manuellement")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_guess = st.text_input("Guess détecté", placeholder="ex: fire, dog_bark, siren...")
        
        with col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            if st.button("Ajouter", use_container_width=True, type="primary"):
                if new_guess:
                    guess_obj = {
                        "value": new_guess,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "id": int(time.time() * 1000)
                    }
                    st.session_state.guess_queue.append(guess_obj)
                    st.success(f"✅ Guess '{new_guess}' ajouté à la file")
                    st.rerun()
                else:
                    st.warning("Veuillez entrer un guess")
        
        st.markdown("---")
        
        # Option : charger depuis fichier
        st.subheader("📂 Charger depuis fichier")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            file_path = st.text_input("Chemin du fichier JSON", value="/tmp/latest_guess.json")
        
        with col2:
            st.write("")
            st.write("")
            if st.button("Charger", use_container_width=True):
                guess_value, guess_time = load_guess_from_file(file_path)
                if guess_value:
                    guess_obj = {
                        "value": guess_value,
                        "timestamp": guess_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "id": int(time.time() * 1000)
                    }
                    st.session_state.guess_queue.append(guess_obj)
                    st.success(f"✅ Guess '{guess_value}' chargé depuis le fichier")
                    st.rerun()
                else:
                    st.error("❌ Impossible de charger le guess depuis le fichier")
    
    with tab2:
        st.subheader(f"File d'attente ({len(st.session_state.guess_queue)} guesses)")
        
        if len(st.session_state.guess_queue) == 0:
            st.info("Aucun guess en attente")
        else:
            # Boutons d'action en masse
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Tout envoyer", use_container_width=True, type="primary"):
                    for guess in st.session_state.guess_queue:
                        result = send_request("POST", f"/submit/{api_key}/{guess['value']}", 
                                            f"✅ '{guess['value']}' envoyé", show_response=False)
                        if result:
                            st.session_state.total_submitted += 1
                    st.session_state.guess_queue = []
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Tout supprimer", use_container_width=True, type="secondary"):
                    st.session_state.guess_queue = []
                    st.rerun()
            
            st.markdown("---")
            
            # Affichage de chaque guess
            for i, guess in enumerate(st.session_state.guess_queue):
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{guess['value']}**")
                    
                    with col2:
                        st.caption(guess['timestamp'])
                    
                    with col3:
                        if st.button("📤", key=f"send_{guess['id']}", help="Envoyer"):
                            result = send_request("POST", f"/submit/{api_key}/{guess['value']}", 
                                                f"✅ Guess '{guess['value']}' envoyé !")
                            if result:
                                st.session_state.total_submitted += 1
                                st.session_state.guess_queue.pop(i)
                                st.rerun()
                    
                    with col4:
                        if st.button("❌", key=f"delete_{guess['id']}", help="Supprimer"):
                            st.session_state.guess_queue.pop(i)
                            st.rerun()
                    
                    st.divider()
    
    # Statistiques
    st.markdown("---")
    st.subheader("📊 Statistiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Guesses envoyés", st.session_state.total_submitted)
    
    with col2:
        st.metric("En file d'attente", len(st.session_state.guess_queue))
    
    st.markdown("---")
    
    # 2. CONSULTATION DES SOUMISSIONS
    st.header("Mes soumissions")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        round_num = st.number_input("Round", min_value=0, value=0, step=1, help="Laissez 0 pour tous")
    
    with col2:
        lap_num = st.number_input("Lap", min_value=0, value=0, step=1, help="Laissez 0 pour tous")
    
    with col3:
        st.write("")
        st.write("")
        get_btn = st.button("Récupérer", use_container_width=True)
    
    if get_btn:
        # Construction de l'endpoint
        endpoint = f"/submissions/{api_key}"
        if round_num > 0:
            endpoint += f"/{round_num}"
            if lap_num > 0:
                endpoint += f"/{lap_num}"
        elif lap_num > 0:
            endpoint += f"?lap={lap_num}"
        
        result = send_request("GET", endpoint, "Soumissions récupérées", show_response=True)
    
    st.markdown("---")
    
    # Suppression de soumissions
    st.subheader("🗑️ Supprimer des soumissions")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.warning("⚠️ Cette action est irréversible ! Utilisez les mêmes filtres Round/Lap que ci-dessus.")
    
    with col2:
        if st.button("Supprimer", use_container_width=True, type="secondary"):
            # Construction de l'endpoint
            endpoint = f"/submissions/{api_key}"
            if round_num > 0:
                endpoint += f"/{round_num}"
                if lap_num > 0:
                    endpoint += f"/{lap_num}"
            elif lap_num > 0:
                endpoint += f"?lap={lap_num}"
            
            result = send_request("DELETE", endpoint, "Soumissions supprimées", show_response=True)

# --- FOOTER ---
st.markdown("---")
st.caption(f"LELEC210X Leaderboard Controller | Mode: {st.session_state.mode.upper()} | Connecté à: {base_url}")