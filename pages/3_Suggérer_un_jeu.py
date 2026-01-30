
import streamlit as st
import pandas as pd

from utils.supabase_client import supabase
import os

from groq import Groq
from dotenv import load_dotenv
import json 
import re


groq_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=groq_key)

st.title("Suggérer un jeu")



# --- Charger les tables de référence ---
def load_reference_table(table_name, label_col):
    data = supabase.table(table_name).select("*").execute()
    df = pd.DataFrame(data.data)
    return df

duree_df = load_reference_table("duree", "duree_descr")
meca_df = load_reference_table("mecanique", "mecanique_descr")
theme_df = load_reference_table("theme", "theme_descr")
coop_df = load_reference_table("type_coop", "type_coop_descr")

# Trouver l'index de "NC" dans chaque table pour l'écrire par défaut
idx_duree = duree_df["duree_descr"].tolist().index("NC")
idx_meca = meca_df["mecanique_descr"].tolist().index("NC")
idx_theme = theme_df["theme_descr"].tolist().index("NC")
idx_coop = coop_df["type_coop_descr"].tolist().index("NC")


# Mise en forme esthétique
st.markdown("""
<style>

/* Tous les champs texte */
input[type="text"] {
    background-color: #f0f7ff;
    border: 2px solid #4a90e2;
    border-radius: 6px;
    padding: 8px;
    font-size: 24px;
    color: #003366;
    font-weight: 800;
}

/* Label personnalisé pour Nom du jeu */
.nom-jeu-label {
    color: #003366;
    font-weight: 700;
    font-size: 18px;
    margin-bottom: 4px;
}

</style>
""", unsafe_allow_html=True)


st.write("")
# -------- NOM DU JEU --------
nom = st.text_input(
    "Nom du jeu",
    value=st.session_state.get("nom_auto", "")
)
st.session_state["nom_auto"] = nom


# -------- BOUTON IA --------
# Bouton IA pour générer le principe + joueurs + âge
if st.button("🔮... pré-remplir les infos avec une IA..."):
    if nom.strip() == "":
        st.warning("Veuillez d'abord saisir le nom du jeu.")
    else:
        prompt = (
            f"Tu es un assistant spécialisé en jeux de société. Pour le jeu '{nom}', fournis les informations suivantes dans EXACTEMENT ce format :\n"
            f"min=<nombre> / max=<nombre> / age=<nombre> / principe=<texte>\n\n"
            f"Exemple : min=2 / max=4 / age=8 / principe=Un jeu rapide où...\n\n"
            f"CONTRAINTES IMPORTANTES :\n" 
            f"- Ne mets rien d'autre que cette ligne.\n" 
            f"- Pas de retour à la ligne.\n" 
            f"- Pas de guillemets.\n" 
            f"- Pas de texte avant ou après.\n" 
            f"- Le principe doit faire 50 à 100 mots. Le ton doit donner envie de découvrir le jeu.\n" 
            f"- Si tu ne connais pas le jeu, indique dans le principe du jeu uniquement : Je ne connais pas ce jeu.\n"
        )

        with st.spinner("L’IA réfléchit..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )

        

        raw = response.choices[0].message.content.strip()

        # Exemple de réponse : "min=2 / max=4 / age=8 / principe=Le jeu consiste à..."
        try:
            parts = [p.strip() for p in raw.split("/", 3)]
            data = {}
            for part in parts:
                if "=" in part:
                    key, value = part.split("=", 1)
                    data[key.strip()] = value.strip()
        except Exception:
            st.error("Impossible de lire la réponse de l'IA.")
            st.write(raw)


        # Stockage dans session_state
        st.session_state["nb_players_min_auto"] = int(data.get("min", 1))
        st.session_state["nb_players_max_auto"] = int(data.get("max", 4))
        st.session_state["age_mini_auto"] = int(data.get("age", 8))
        st.session_state["principe_jeu_auto"] = data.get("principe", "")


st.write("")
# -------- FORMULAIRE AVEC LES INFORMATIONS SUR LE JEU --------
with st.form("add_game_form"):
    
    st.subheader("Détails sur le jeu")

    principe_jeu = st.text_area(
        "Principe du jeu :",
        value=st.session_state.get("principe_jeu_auto", "")
    )

    col1, col2 = st.columns(2)

    with col1:
        nb_players_min = st.number_input(
            "Nombre de joueurs minimum",
            min_value=1,
            step=1,
            value=st.session_state.get("nb_players_min_auto", 1)
        )

        age_mini = st.number_input(
            "Âge minimum",
            min_value=1,
            step=1,
            value=st.session_state.get("age_mini_auto", 8)
        )

        theme = st.selectbox("Thème", theme_df["theme_descr"].tolist(), index=idx_theme)

    with col2:
        nb_players_max = st.number_input(
            "Nombre de joueurs maximum",
            min_value=1,
            step=1,
            value=st.session_state.get("nb_players_max_auto", 4)
        )

        duree = st.selectbox("Durée", duree_df["duree_descr"].tolist(), index=idx_duree)
        type_coop = st.selectbox("Type de coopération", coop_df["type_coop_descr"].tolist(), index=idx_coop)

    mecanique = st.selectbox("Mécanique", meca_df["mecanique_descr"].tolist(), index=idx_meca)

    submitted = st.form_submit_button("Ajouter le jeu dans la base")





# Vérifie si le jeu existe déjà dans la base
existing_games = supabase.table("list_games").select("nom").execute()
existing_names = [g["nom"].strip().lower() for g in existing_games.data]


# --- Insertion dans la base ---
if submitted:

    # --- Vérifications avant insertion ---
    errors = []
    # Vérification doublon (insensible à la casse)
    if nom.strip().lower() in existing_names:
        errors.append(f"Le jeu '{nom}' existe déjà dans la base.")


    if nom.strip() == "":
        errors.append("Le nom du jeu ne peut pas être vide.")

    
    if principe_jeu.strip() == "":
        errors.append("Mettez qq mots sur le principe du jeu.")

    if nb_players_min > nb_players_max:
        errors.append("Le nombre de joueurs minimum doit être inférieur ou égal au maximum.")

    if age_mini < 1:
        errors.append("L'âge minimum doit être supérieur ou égal à 1.")

    if age_mini > 80:
        errors.append("Un âge supérieur à 80 ? Vous êtes sûr ?")

    # Si erreurs → on les affiche et on arrête là
    if errors:
        for err in errors:
            st.error(err)
        st.stop()

    # --- Récupérer les IDs correspondants ---
    duree_id = int(duree_df.loc[duree_df["duree_descr"] == duree, "id"].iloc[0])
    mecanique_id = int(meca_df.loc[meca_df["mecanique_descr"] == mecanique, "id"].iloc[0])
    theme_id = int(theme_df.loc[theme_df["theme_descr"] == theme, "id"].iloc[0])
    type_coop_id = int(coop_df.loc[coop_df["type_coop_descr"] == type_coop, "id"].iloc[0])
    avis_cath="A COMPLETER (ligne non revue)"

    # --- Construire l'objet à insérer ---
    new_game = {
        "nom": nom,
        "nb_players_min": nb_players_min,
        "nb_players_max": nb_players_max,
        "age_mini": age_mini,
        "principe_jeu": principe_jeu,
        "avis_cath": avis_cath,
        "duree_id": duree_id,
        "mecanique_id": mecanique_id,
        "theme_id": theme_id,
        "type_coop_id": type_coop_id
    }

    # --- Insertion ---
    result = supabase.table("list_games").insert(new_game).execute()

    if result.data:
        st.success(f"Le jeu **{nom}** a été ajouté avec succès.")
    else:
        st.error("Une erreur est survenue lors de l'ajout.")


