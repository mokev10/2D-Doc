import streamlit as st
from scripts.generate_datamatrix import generate_datamatrix

st.title("📦 Générateur DataMatrix")

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
