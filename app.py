import streamlit as st
from scripts.generate_datamatrix import generate_datamatrix

st.set_page_config(
    page_title="Générateur 2D-Codes Data Matrix",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Générateur DataMatrix")

# 🔹 Option escape sequences
use_escape = st.checkbox("Activer escape sequences (\\n = saut de ligne)")

data = st.text_area("Texte à encoder")

if st.button("Générer"):
    if data:

        # 🔥 traitement escape sequences
        if use_escape:
            data = data.encode().decode("unicode_escape")

        img_buffer = generate_datamatrix(data)

        st.image(img_buffer)

        st.download_button(
            label="Télécharger",
            data=img_buffer,
            file_name="datamatrix.png",
            mime="image/png"
        )

    else:
        st.warning("Entre un texte")
