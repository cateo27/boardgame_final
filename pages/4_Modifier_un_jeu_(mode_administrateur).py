import streamlit as st
import pandas as pd
from utils.supabase_client import supabase

# Mot de passe admin
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

# Initialisation
if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

# Si pas encore authentifié
if not st.session_state.admin_ok:
    st.title("🔐 Accès administrateur")

    pwd = st.text_input("Mot de passe :", type="password")

    if st.button("Se connecter"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_ok = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
            st.stop()

    st.stop()



st.title("✏️ Modifier un jeu")


st.markdown("---")
if st.session_state.get("admin_ok", False):
    if st.button("🔒 Déconnecter le mode administrateur"):
        st.session_state.admin_ok = False
        st.rerun()

        
# ---------------------------------------------------------
# 1) Charger les tables de référence
# ---------------------------------------------------------
def load_reference_table(table_name, label_col):
    data = supabase.table(table_name).select("*").execute()
    return pd.DataFrame(data.data)

duree_df = load_reference_table("duree", "duree_descr")
meca_df = load_reference_table("mecanique", "mecanique_descr")
theme_df = load_reference_table("theme", "theme_descr")
coop_df = load_reference_table("type_coop", "type_coop_descr")

# ---------------------------------------------------------
# 2) Charger les jeux existants
# ---------------------------------------------------------
games = supabase.table("list_games").select("*").execute().data
df_games = pd.DataFrame(games)

# Jointures pour afficher les descriptions
df_games = (
    df_games
    .merge(duree_df, left_on="duree_id", right_on="id", suffixes=("", "_duree"))
    .merge(meca_df, left_on="mecanique_id", right_on="id", suffixes=("", "_meca"))
    .merge(theme_df, left_on="theme_id", right_on="id", suffixes=("", "_theme"))
    .merge(coop_df, left_on="type_coop_id", right_on="id", suffixes=("", "_coop"))
)

# ---------------------------------------------------------
# 3) Filtres
# ---------------------------------------------------------
st.subheader("🔎 Choisir un jeu à modifier")

col1, col2 = st.columns(2)

with col1:
    choix_nom = st.selectbox(
        "Choisir un jeu dans la liste",
        [""] + sorted(df_games["nom"].tolist())
    )

with col2:
    jeux_sans_reco = df_games[df_games["avis_cath"].str.contains("A COMPLETER", na=False)]
    choix_sans_reco = st.selectbox(
        "Ou choisir un jeu sans recommandation",
        [""] + sorted(jeux_sans_reco["nom"].tolist())
    )

# Déterminer le jeu sélectionné
jeu_selectionne = choix_nom if choix_nom != "" else choix_sans_reco

if jeu_selectionne == "":
    st.info("Sélectionnez un jeu pour afficher et modifier ses informations.")
    st.stop()

# ---------------------------------------------------------
# 4) Récupérer les infos du jeu sélectionné
# ---------------------------------------------------------
jeu = df_games[df_games["nom"] == jeu_selectionne].iloc[0]

# ---------------------------------------------------------
# 5) Formulaire de modification
# ---------------------------------------------------------
st.subheader(f"📝 Modifier : {jeu_selectionne}")

with st.form("edit_game_form"):

    principe_jeu = st.text_area("Principe du jeu", value=jeu["principe_jeu"])
    avis_cath = st.text_area("Votre recommandation", value=jeu["avis_cath"])

    col1, col2 = st.columns(2)

    with col1:
        nb_players_min = st.number_input(
            "Nombre de joueurs minimum",
            min_value=1,
            step=1,
            value=int(jeu["nb_players_min"])
        )

        age_mini = st.number_input(
            "Âge minimum",
            min_value=1,
            step=1,
            value=int(jeu["age_mini"])
        )

        theme = st.selectbox(
            "Thème",
            theme_df["theme_descr"].tolist(),
            index=theme_df["theme_descr"].tolist().index(jeu["theme_descr"])
        )

    with col2:
        nb_players_max = st.number_input(
            "Nombre de joueurs maximum",
            min_value=1,
            step=1,
            value=int(jeu["nb_players_max"])
        )

        duree = st.selectbox(
            "Durée",
            duree_df["duree_descr"].tolist(),
            index=duree_df["duree_descr"].tolist().index(jeu["duree_descr"])
        )

        type_coop = st.selectbox(
            "Type de coopération",
            coop_df["type_coop_descr"].tolist(),
            index=coop_df["type_coop_descr"].tolist().index(jeu["type_coop_descr"])
        )

    mecanique = st.selectbox(
        "Mécanique",
        meca_df["mecanique_descr"].tolist(),
        index=meca_df["mecanique_descr"].tolist().index(jeu["mecanique_descr"])
    )

    submitted = st.form_submit_button("💾 Sauvegarder les modifications")

# ---------------------------------------------------------
# 6) Sauvegarde dans Supabase
# ---------------------------------------------------------
if submitted:

    # Récupérer les IDs
    duree_id = int(duree_df.loc[duree_df["duree_descr"] == duree, "id"].iloc[0])
    mecanique_id = int(meca_df.loc[meca_df["mecanique_descr"] == mecanique, "id"].iloc[0])
    theme_id = int(theme_df.loc[theme_df["theme_descr"] == theme, "id"].iloc[0])
    type_coop_id = int(coop_df.loc[coop_df["type_coop_descr"] == type_coop, "id"].iloc[0])

    update_data = {
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

    result = supabase.table("list_games").update(update_data).eq("nom", jeu_selectionne).execute()

    if result.data:
        st.success(f"Le jeu **{jeu_selectionne}** a été mis à jour avec succès.")
    else:
        st.error("Une erreur est survenue lors de la mise à jour.")

# ---------------------------------------------------------
# 7) Bouton de suppression
# ---------------------------------------------------------

st.markdown("---")
st.subheader("🗑️ Suppression du jeu")

# Initialiser l'état si nécessaire
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

# Premier clic : demande de confirmation
if not st.session_state.confirm_delete:
    if st.button("❌ Supprimer ce jeu"):
        st.session_state.confirm_delete = True
        st.rerun()

# Deuxième clic : confirmation
else:
    st.warning(f"Voulez-vous vraiment supprimer **{jeu_selectionne}** ? Cette action est irréversible.")

    colA, colB = st.columns(2)

    with colA:
        if st.button("⚠️ Oui, supprimer définitivement"):
            delete_result = (
                supabase
                .table("list_games")
                .delete()
                .eq("nom", jeu_selectionne)
                .execute()
            )

            if delete_result.data:
                st.success(f"Le jeu **{jeu_selectionne}** a été supprimé avec succès.")
                st.session_state.confirm_delete = False
                st.stop()
            else:
                st.error("Une erreur est survenue lors de la suppression.")

    with colB:
        if st.button("Annuler"):
            st.session_state.confirm_delete = False
            st.rerun()

