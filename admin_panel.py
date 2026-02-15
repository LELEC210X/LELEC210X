import streamlit as st
import requests
import json

# --- CONFIGURATION ---
st.set_page_config(page_title="Leaderboard Admin", page_icon="🎮", layout="wide")

st.title("🎮 LELEC210X Leaderboard Controller")
st.markdown("Interface de gestion pour le serveur de compétition.")

# --- SIDEBAR : CONNEXION ---
with st.sidebar:
    st.header("🔌 Connexion")
    
    # Configuration de l'URL et du Port
    col_ip, col_port = st.columns([2, 1])
    host = col_ip.text_input("Host", value="localhost")
    port = col_port.text_input("Port", value="5001")
    
    base_url = f"http://{host}:{port}/lelec210x/leaderboard"
    
    st.markdown("---")
    
    # Clé Admin
    admin_key = st.text_input("🔑 Clé Admin (Key)", type="password", help="La clé générée avec --admin")
    
    if not admin_key:
        st.warning("Veuillez entrer une clé admin pour activer les commandes.")

# --- FONCTIONS UTILITAIRES ---
def send_request(method, endpoint, success_msg="Action réussie !"):
    """Envoie une requête à l'API et gère l'affichage."""
    url = f"{base_url}{endpoint}"
    try:
        if method == "POST":
            r = requests.post(url)
        elif method == "GET":
            r = requests.get(url)
        elif method == "PATCH":
            r = requests.patch(url)
        
        if r.status_code == 200:
            st.toast(success_msg, icon="✅")
            return r.json() if r.content else True
        elif r.status_code == 401:
            st.error("Erreur 401 : Clé invalide.")
        elif r.status_code == 403:
            st.error("Erreur 403 : Non autorisé (Avez-vous les droits admin ?).")
        else:
            st.error(f"Erreur {r.status_code}: {r.text}")
    except requests.exceptions.ConnectionError:
        st.error(f"Impossible de se connecter au serveur sur {base_url}. Vérifiez qu'il est lancé.")
    return None

# --- INTERFACE PRINCIPALE ---

if admin_key:
    # 1. STATUS & MONITORING
    st.subheader("📡 État du Serveur")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Bouton pour rafraichir le statut
        if st.button("Actualiser le statut"):
            status_data = send_request("GET", f"/status/{admin_key}", "Statut mis à jour")
            if status_data:
                st.info(f"Réponse du serveur : {status_data}") # Affiche le JSON brut ou formaté selon tes besoins
                # Si le JSON renvoie un état précis (ex: "RUNNING"), tu peux l'afficher ici plus joliment

    with col2:
        st.write("") # Spacer

    st.markdown("---")

    # 2. CONTRÔLE DE LA PARTIE (PLAY / PAUSE / RESTART)
    st.subheader("⏯️ Contrôle de la Partie")
    
    col_play, col_pause, col_restart = st.columns(3)
    
    with col_play:
        if st.button("▶️ LANCER (Play)", use_container_width=True, type="primary"):
            send_request("POST", f"/play/{admin_key}", "La partie a démarré !")
            
    with col_pause:
        if st.button("⏸️ PAUSE", use_container_width=True):
            send_request("POST", f"/pause/{admin_key}", "La partie est en pause.")
            
    with col_restart:
        if st.button("🔄 REDÉMARRER (Restart)", use_container_width=True, type="secondary"):
            # On demande une confirmation via une checkbox pour éviter les miss-click
            if st.checkbox("Sûr de vouloir restart ?"):
                send_request("POST", f"/restart/{admin_key}", "La partie a redémarré !")
            else:
                st.warning("Cochez la case pour confirmer le redémarrage.")

    st.markdown("---")

    # 3. GESTION DES ÉQUIPES (RENAME)
    st.subheader("✏️ Renommer une équipe")
    
    with st.form("rename_form"):
        col_new_name, col_submit = st.columns([3, 1])
        new_name = col_new_name.text_input("Nouveau nom d'équipe")
        submitted = col_submit.form_submit_button("Renommer")
        
        if submitted and new_name:
            # Attention : l'API demande /rename/{key}/{name}
            # Il faut s'assurer que le nom est "URL safe"
            import urllib.parse
            safe_name = urllib.parse.quote(new_name)
            send_request("PATCH", f"/rename/{admin_key}/{safe_name}", f"Équipe renommée en {new_name}")

    st.markdown("---")

    # 4. RÉSULTATS
    st.subheader("🏆 Résultats")
    if st.button("Obtenir les résultats"):
        results = send_request("POST", f"/results/{admin_key}", "Résultats récupérés")
        if results:
            st.json(results)

else:
    st.info("👈 Entrez votre clé Admin dans la barre latérale pour commencer.")