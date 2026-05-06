import streamlit as st
from scripts.generate_datamatrix import generate_datamatrix

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
}

.stButton > button:hover {
    transform: scale(1.05);
}

/* Checkbox */
.stCheckbox {
    color: white;
}

/* ---------------- CENTRAGE IMAGE ---------------- */
.center-img {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    margin-top: 20px;
    padding: 20px;
    background: rgba(30, 41, 59, 0.6);
    border-radius: 12px;
    border: 1px solid #334155;
}

/* force image centrée */
.center-img img {
    display: block;
    margin-left: auto;
    margin-right: auto;
    max-width: 100%;
    height: auto;
}

/* Lien centré */
.center-img a {
    color: #3b82f6;
    text-decoration: none;
    margin-top: 15px;
    font-size: 14px;
}

.center-img a:hover {
    text-decoration: underline;
}

/* Logo centré */
.center-img a img {
    margin-top: 10px;
    height: auto;
}

</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------

st.title("Générateur de Codes 2D")

# Sélection du type de code-barres
barcode_type = st.selectbox(
    "Type de code-barres",
    ["DataMatrix", "PDF417"],
    index=0
)

data = st.text_area("Texte à encoder")

if barcode_type == "DataMatrix":
    dpi = st.slider(
        "Image Resolution (DPI)",
        min_value=72,
        max_value=300,
        value=150,
        step=1
    )

    use_escape = st.checkbox("Activer escape sequences (\\n = retour ligne)")
else:
    use_escape = False

# ---------------- BOUTON CENTRÉ ----------------
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    generate = st.button("Générer")

# ---------------- RESULT ----------------

if generate:
    if data.strip():
        if barcode_type == "DataMatrix":
            
            if use_escape:
                data = data.encode().decode("unicode_escape")

            img_buffer = generate_datamatrix(data, dpi=dpi)

            # 🔥 WRAPPER CENTRÉ COMPLET
            st.markdown('<div class="center-img">', unsafe_allow_html=True)

            st.image(img_buffer, caption="DataMatrix généré")

            st.download_button(
                label="Télécharger l'image",
                data=img_buffer,
                file_name=f"datamatrix_{dpi}dpi.png",
                mime="image/png"
            )

            st.markdown('</div>', unsafe_allow_html=True)

        else:  # PDF417
            # Encoder les données pour l'URL
            encoded_data = data.replace(" ", "+").replace("\n", "%0A")

            st.markdown(f"""
            <div class='center-img'>
                <img alt='PDF417 Barcode Generator TEC-IT' 
                     src='https://barcode.tec-it.com/barcode.ashx?data={encoded_data}&code=PDF417&translate-esc=on&showhrt=no'
                     style='max-width: 100%; height: auto;'/>
                <div style='padding-top: 12px; text-align: center; font-size: 13px; font-family: Source Sans Pro, Arial, sans-serif;'>
                    <a href='https://www.tec-it.com' title='Barcode Software by TEC-IT' target='_blank'>
                        TEC-IT Barcode Generator<br/>
                        <img alt='TEC-IT Barcode Software' border='0'
                             src='https://www.tec-it.com/pics/banner/web/TEC-IT_Logo_75x75.gif'
                             style='height: 50px; width: auto; margin-top: 8px;'>
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("Veuillez entrer un texte à encoder")
