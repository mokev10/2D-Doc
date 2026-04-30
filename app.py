import streamlit as st
from scripts.generate_datamatrix import generate_datamatrix

# ✅ DOIT être en premier
st.set_page_config(
    page_title="Générateur 2D-Codes Data Matrix",
    page_icon="https://img.icons8.com/external-duo-tone-yogi-aprelliyanto/24/external-search-file-document-duo-tone-yogi-aprelliyanto.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Générateur DataMatrix")

data = st.text_input("Texte à encoder")

if st.button("Générer"):
    if data:
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
