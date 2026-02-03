import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Ma Ludothèque",
    page_icon="🎲",
    layout="wide"
)

# Style personnalisé
st.markdown("""
<style>
h1 {
    color: #2c3e50;
    font-weight: 800;
    font-size: 48px;
    margin-bottom: 10px;
}

.info-box {
    background-color: #f0f7ff;
    border-left: 6px solid #4a90e2;
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
    font-size: 18px;
    color: #003366;
}

.small-section-title {
    font-size: 18px;
    font-style: italic;
    color: #444444;   /* gris foncé */
    margin-top: 30px;
    margin-bottom: 6px;
}

ul.info-list {
    list-style-type: "• ";
    padding-left: 1.2em;
    margin-top: 5px;
    font-size: 15px;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# Titre principal
st.title("🎲 Ma Ludothèque ♟️")

# Introduction
st.markdown("""
<div class="info-box">
    <B> Bienvenue dans ma ludothèque !</B> <BR> <BR> 
    A l'aide des menus à gauche, vous pouvez parcourir les jeux que je connais. <BR>
    Vous pouvez également m'en suggérer... J'ai hâte de découvrir vos recommandations !
</div> <BR><BR><BR>
""", unsafe_allow_html=True)


st.markdown('<div class="small-section-title">À propos de cette application :</div>', unsafe_allow_html=True)

st.markdown("""
<ul class="info-list"><I>
    <li>Pages développées et mises en ligne avec Streamlit ; hébergement sur GitHub</li>
    <li>Base de données construite avec Supabase</li>
    <li>Fonctionnalités IA générative intégrées grâce à une clé Groq</li></I>
</ul>

""", unsafe_allow_html=True)

st.markdown('<div class="small-section-title">Utilisation de fonctionnalités gratuites, donc un long temps de chargement est normal !</div>', unsafe_allow_html=True)

