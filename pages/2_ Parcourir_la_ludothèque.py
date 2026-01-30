import streamlit as st
import pandas as pd
from utils.supabase_client import supabase

st.title("🔎 Parcourir la ludothèque")

# --- Charger les jeux ---
data = supabase.rpc("get_games").execute()
rows = data.data
st.markdown("""
<style>

/* Partie à gauche du point (inactive) */
.stSlider [data-baseweb="slider"] > div > div:nth-child(1) {
    background-color: #E0E0E0 !important;  /* gris clair */
}

/* Partie à droite du point (active) */
.stSlider [data-baseweb="slider"] > div > div:nth-child(2) {
    background-color: #0D47A1 !important;  /* bleu foncé */
}

/* Bouton rond */
.stSlider [data-baseweb="slider"] > div > div > div {
    background-color: #1976D2 !important;  /* bleu */
    border: 2px solid #0D47A1 !important;  /* bleu foncé */
}

</style>
""", unsafe_allow_html=True)


if rows:
    df = pd.DataFrame(rows)


    # Renommer les colonnes
    df = df.rename(columns={
        "nom": "Nom du jeu",
        "nb_players_min": "Nb de joueurs minimum",
        "nb_players_max": "Nb de joueurs maximum",
        "age_mini": "Âge minimum",
        "principe_jeu": "Principe",
        "avis_cath": "Recommandation de Catherine",
        "duree": "Durée",
        "mecanique": "Mécanique(s) de jeu",
        "theme": "Thème(s)",
        "type_coop": "Type(s) de coopération"
    })

    # --- Filtres ---
    col1, col2, col3 = st.columns(3)

    with col1:
        filtre_meca = st.multiselect(
            "Mécanique(s) de jeu",
            options=sorted(df["Mécanique(s) de jeu"].dropna().unique().tolist()),
            default=[]
        )
        filtre_coop = st.multiselect(
            "Type(s) de coopération",
            options=sorted(df["Type(s) de coopération"].dropna().unique().tolist()),
            default=[]
        )

    with col2:
        filtre_theme = st.multiselect(
            "Thème(s)",
            options=sorted(df["Thème(s)"].dropna().unique().tolist()),
            default=[]
        )
        filtre_duree = st.multiselect(
            "Durée(s)",
            options=sorted(df["Durée"].dropna().unique().tolist()),
            default=[]
        )


    with col3:
        age_min_filter = st.slider(
            "Âge minimum",
            min_value=int(df["Âge minimum"].min()),
            max_value=int(df["Âge minimum"].max()),
            value=int(df["Âge minimum"].min())
        )

        min_joueurs_global = int(df["Nb de joueurs minimum"].min())
        max_joueurs_global = int(df["Nb de joueurs maximum"].max())

        slider_joueurs = st.slider(
            "Nombre de joueurs minimum et maximum",
            min_value=min_joueurs_global,
            max_value=max_joueurs_global,
            value=(min_joueurs_global, max_joueurs_global)
        )

        min_sel, max_sel = slider_joueurs


    

    # --- Appliquer les filtres ---
    nb_lignes_deb = df.shape[0]
    if filtre_meca:
        df = df[df["Mécanique(s) de jeu"].isin(filtre_meca)]

    if filtre_theme:
        df = df[df["Thème(s)"].isin(filtre_theme)]

    if filtre_coop:
        df = df[df["Type(s) de coopération"].isin(filtre_coop)]

    if filtre_duree:
        df = df[df["Durée"].isin(filtre_duree)]

    df = df[df["Âge minimum"] >= age_min_filter]

    df = df[
        (df["Nb de joueurs minimum"] <= max_sel) &
        (df["Nb de joueurs maximum"] >= min_sel)
    ]
    nb_lignes_fin = df.shape[0]
    

    st.write("")
    st.write("")
    st.write(f"{nb_lignes_fin} jeux répondent aux filtres ({nb_lignes_deb} jeux présents dans la base):")

    # Colonnes affichées
    colonnes = [
        "Nom du jeu", "Durée",
        "Nb de joueurs minimum", "Nb de joueurs maximum",
        "Âge minimum", "Principe", "Recommandation de Catherine"
    ]
    df = df[colonnes]

    # 🎨 Style moderne
    styler = (
        df.style
        .set_properties(**{
            "padding": "10px",
            "border": "1px solid #E0E0E0"
        })
        .set_table_styles([
            {"selector": "th", "props": [
                ("background-color", "#1976D2"),
                ("color", "white"),
                ("font-weight", "bold"),
                ("padding", "10px")
            ]},
            {"selector": "tr:nth-child(even)", "props": [
                ("background-color", "#F5F5F5")
            ]},
            {"selector": "tr:hover", "props": [
                ("background-color", "#E3F2FD")
            ]}
        ])
    )

    st.write(styler)

else:
    st.info("Aucun jeu trouvé.")
