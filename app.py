import streamlit as st
from scripts.generate_datamatrix import generate_datamatrix

st.set_page_config(
    page_title="Générateur 2D-Codes Data Matrix",
    page_icon="📦",
    layout="wide",
)

st.title("Générateur DataMatrix")

data = st.text_area("Texte à encoder")

# 🔹 DPI slider
dpi = st.slider("Image Resolution (DPI)", 72, 300, 150)

use_escape = st.checkbox("Activer escape sequences (\\n = saut de ligne)")

if st.button("Générer"):
    if data:

        if use_escape:
            data = data.encode().decode("unicode_escape")

        # 🔥 on transmet le DPI comme paramètre
        img_buffer = generate_datamatrix(data, dpi=dpi)

        st.image(img_buffer)

        st.download_button(
            label="Télécharger",
            data=img_buffer,
            file_name=f"datamatrix_{dpi}dpi.png",
            mime="image/png"
        )
    else:
        st.warning("Entre un texte")
