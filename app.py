import streamlit as st
from scripts.generate_datamatrix import generate_datamatrix

# ⚠️ DOIT être la première commande Streamlit
st.set_page_config(
    page_title="Générateur 2D-Codes Data Matrix",
    page_icon="https://img.icons8.com/external-duo-tone-yogi-aprelliyanto/24/external-search-file-document-duo-tone-yogi-aprelliyanto.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Générateur DataMatrix")

# ---------------- UI ----------------

data = st.text_area("Texte à encoder")

dpi = st.slider(
    "Image Resolution (DPI)",
    min_value=72,
    max_value=300,
    value=150,
    step=1
)

use_escape = st.checkbox("Activer escape sequences (\\n = retour ligne)")

# ---------------- Action ----------------

if st.button("Générer"):
    if data.strip():

        # escape sequences
        if use_escape:
            data = data.encode().decode("unicode_escape")

        img_buffer = generate_datamatrix(data, dpi=dpi)

        st.image(img_buffer, caption="DataMatrix généré")

        st.download_button(
            label="Télécharger l'image",
            data=img_buffer,
            file_name=f"datamatrix_{dpi}dpi.png",
            mime="image/png"
        )

    else:
        st.warning("Veuillez entrer un texte à encoder")
