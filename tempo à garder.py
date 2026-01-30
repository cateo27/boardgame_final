# tempo à garder



# venv\Scripts\activate
# streamlit run streamlit_app.py

import streamlit as st
from supabase import create_client, Client
import pandas as pd


# 🔑 Clés Supabase
url = "https://ymwdvqmfblnewoiicpkk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltd2R2cW1mYmxuZXdvaWljcGtrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk1OTQwNDUsImV4cCI6MjA4NTE3MDA0NX0.pYML1VPXRrehBlx6qnf9sWTrQ_gdiLLZ7FaQksLMpzY"

# 🔌 Connexion
supabase: Client = create_client(url, key)

st.title("🎲 Liste des jeux")

# Lecture de la base
data = supabase.rpc("get_games").execute()
rows = data.data
# rows est une liste de dictionnaires Python...

df = pd.DataFrame(rows)
st.dataframe(df)


