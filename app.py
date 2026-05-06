import streamlit as st
from scripts.generate_datamatrix import generate_datamatrix
import requests
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Générateur 2D-Codes Data Matrix & PDF417",
    page_icon="https://img.icons8.com/external-duo-tone-yogi-aprelliyanto/60/external-search-file-document-duo-tone-yogi-aprelliyanto.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* Fond global */
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
}

/* Titre */
h1 {
    text-align: center;
    color: white;
    font-weight: 700;
    margin-bottom: 25px;
}

/* Text area */
textarea {
    border-radius: 12px !important;
    border: 2px solid #334155 !important;
    background-color: #0b1220 !important;
    color: white !important;
    transition: all 0.3s ease-in-out;
}

textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.5);
    transform: scale(1.01);
}

/* Slider */
.stSlider > div {
    color: white;
}

/* Selectbox */
.stSelectbox > div > div {
    border-radius: 12px !important;
}

/* bouton */
.stButton > button {
    background: linear-gradient(90deg, #3b82f6, #6366f1);
    color: white;
    border: none;
    padding: 0.7rem 2rem;
    border-radius: 12px;
    font-weight: bold;
    transition: all 0.3s ease-in-out;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    width: 100%;
}

.stButton > button:hover {
    transform: scale(1.05);
}

/* Checkbox */
.stCheckbox {
    color: white;
}

/* Centre les images */
img {
    display: block;
    margin: 0 auto;
}

</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------

st.title("Générateur de Codes 2D")

# Sélection du type de code-barres
barcode_type = st.selectbox(
    "Type de code-barres",
    ["DataMatrix", "Data Matrix (ECC200) - 2D Barcode", "PDF417", "Code-128"],
    index=0
)

data = st.text_area("Texte à encoder")

# Options disponibles pour les deux types
dpi = st.slider(
    "Image Resolution (DPI)",
    min_value=72,
    max_value=300,
    value=150,
    step=1
)

use_escape = st.checkbox("Evaluate escape sequences (\\n for ENTER)")

# ---------------- BOUTON CENTRÉ ----------------
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    generate = st.button("Générer")

# ---------------- RESULT ----------------

if generate:
    if data.strip():
        # Traiter les escape sequences si activé
        processed_data = data
        if use_escape:
            processed_data = processed_data.encode().decode("unicode_escape")

        if barcode_type == "DataMatrix":
            
            img_buffer = generate_datamatrix(processed_data, dpi=dpi)

            # 🔥 CENTRAGE DATAMATRIX
            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:
                st.image(img_buffer, caption="DataMatrix généré", use_column_width=True)
                st.download_button(
                    label="📥 Télécharger l'image",
                    data=img_buffer,
                    file_name=f"datamatrix_{dpi}dpi.png",
                    mime="image/png"
                )

        elif barcode_type == "Data Matrix (ECC200) - 2D Barcode":
            # Encoder les données pour l'URL
            encoded_data = processed_data.replace(" ", "+").replace("\n", "%0A")
            gs1_url = f"https://barcode.tec-it.com/barcode.ashx?data={encoded_data}&code=GS1DataMatrix&translate-esc=on&showhrt=no&dpi={dpi}&dmsize=Default"

            try:
                # Récupérer l'image GS1DataMatrix
                response = requests.get(gs1_url, timeout=10)
                gs1_buffer = BytesIO(response.content)

                # 🔥 CENTRAGE GS1DATAMATRIX
                col1, col2, col3 = st.columns([1, 1, 1])

                with col2:
                    st.image(gs1_buffer, caption="Data Matrix (ECC200) généré", use_column_width=True)
                    st.download_button(
                        label="📥 Télécharger l'image",
                        data=gs1_buffer.getvalue(),
                        file_name=f"gs1datamatrix_{dpi}dpi.png",
                        mime="image/png"
                    )

                    # Crédit TEC-IT
                    st.markdown("""
                    <div style='text-align: center; font-size: 12px; margin-top: 10px;'>
                        <a href='https://www.tec-it.com' title='Barcode Software by TEC-IT' target='_blank' style='color: #3b82f6; text-decoration: none;'>
                            Powered by TEC-IT
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Erreur lors de la génération du Data Matrix (ECC200): {e}")

        elif barcode_type == "PDF417":
            # Encoder les données pour l'URL
            encoded_data = processed_data.replace(" ", "+").replace("\n", "%0A")
            pdf417_url = f"https://barcode.tec-it.com/barcode.ashx?data={encoded_data}&code=PDF417&translate-esc=on&showhrt=no&dpi={dpi}"

            try:
                # Récupérer l'image PDF417
                response = requests.get(pdf417_url, timeout=10)
                pdf417_buffer = BytesIO(response.content)

                # 🔥 CENTRAGE PDF417
                col1, col2, col3 = st.columns([1, 1, 1])

                with col2:
                    st.image(pdf417_buffer, caption="PDF417 généré", use_column_width=True)
                    st.download_button(
                        label="📥 Télécharger l'image",
                        data=pdf417_buffer.getvalue(),
                        file_name=f"pdf417_{dpi}dpi.png",
                        mime="image/png"
                    )

                    # Crédit TEC-IT
                    st.markdown("""
                    <div style='text-align: center; font-size: 12px; margin-top: 10px;'>
                        <a href='https://www.tec-it.com' title='Barcode Software by TEC-IT' target='_blank' style='color: #3b82f6; text-decoration: none;'>
                            Powered by TEC-IT
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Erreur lors de la génération du PDF417: {e}")

        elif barcode_type == "Code-128":
            # Encoder les données pour l'URL
            encoded_data = processed_data.replace(" ", "+").replace("\n", "%0A")
            code128_url = f"https://barcode.tec-it.com/barcode.ashx?data={encoded_data}&code=Code128&translate-esc=on&showhrt=no&dpi={dpi}"

            try:
                # Récupérer l'image Code128
                response = requests.get(code128_url, timeout=10)
                code128_buffer = BytesIO(response.content)

                # 🔥 CENTRAGE CODE128
                col1, col2, col3 = st.columns([1, 1, 1])

                with col2:
                    st.image(code128_buffer, caption="Code-128 généré", use_column_width=True)
                    st.download_button(
                        label="📥 Télécharger l'image",
                        data=code128_buffer.getvalue(),
                        file_name=f"code128_{dpi}dpi.png",
                        mime="image/png"
                    )

                    # Crédit TEC-IT
                    st.markdown("""
                    <div style='text-align: center; font-size: 12px; margin-top: 10px;'>
                        <a href='https://www.tec-it.com' title='Barcode Software by TEC-IT' target='_blank' style='color: #3b82f6; text-decoration: none;'>
                            Powered by TEC-IT
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Erreur lors de la génération du Code-128: {e}")

    else:
        st.warning("Veuillez entrer un texte à encoder")
