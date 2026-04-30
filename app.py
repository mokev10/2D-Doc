# app.py
import streamlit as st
import segno
import io
import base64
from PIL import Image
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Tentative d'import DataMatrix (optionnel). Si absent, on continue sans erreur.
try:
    from pylibdmtx import encode as dmtx_encode
    DATAMATRIX_AVAILABLE = True
except Exception:
    DATAMATRIX_AVAILABLE = False

# --- Page config (corrigé) ---
st.set_page_config(
    page_title="Générateur 2D-Doc CIN TD1",
    page_icon="https://img.icons8.com/external-smashingstocks-detailed-outline-smashing-stocks/66/external-QR-Code-mobile-shopping-smashingstocks-detailed-outline-smashing-stocks.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS pour rendu proche de la première image (fond, carte, diviseur) ---
st.markdown(
    """
    <style>
    /* Page background pattern (soft blue geometric feel) */
    .stApp {
        background-color: #eaf6fb;
        background-image:
            radial-gradient(circle at 10% 20%, rgba(255,255,255,0.6) 0px, rgba(255,255,255,0.0) 2px),
            radial-gradient(circle at 80% 80%, rgba(255,255,255,0.6) 0px, rgba(255,255,255,0.0) 2px),
            repeating-linear-gradient(45deg, rgba(0,0,0,0.02) 0px, rgba(0,0,0,0.02) 1px, transparent 1px, transparent 20px);
        background-size: 120px 120px, 120px 120px, 100% 100%;
    }

    /* Card style for left and right panels */
    .card {
        background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(250,250,255,0.95));
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(20,40,60,0.08);
        border: 1px solid rgba(0,0,0,0.04);
    }

    /* Divider like on the sample: vertical decorative bar with small shapes */
    .vertical-divider {
        width: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .vertical-divider .bar {
        width: 2px;
        height: 320px;
        background: linear-gradient(180deg, #0b6fa4, #6fc3e8);
        border-radius: 2px;
        position: relative;
        box-shadow: 0 2px 6px rgba(11,111,164,0.12);
    }
    .vertical-divider .dot {
        position: absolute;
        left: -6px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #e6fbff;
        border: 2px solid rgba(11,111,164,0.12);
    }
    .vertical-divider .dot:nth-child(1) { top: 18px; transform: scale(0.9); }
    .vertical-divider .dot:nth-child(2) { top: 90px; transform: scale(0.7); }
    .vertical-divider .dot:nth-child(3) { top: 170px; transform: scale(1.0); }
    .vertical-divider .dot:nth-child(4) { top: 250px; transform: scale(0.8); }

    /* QR card styling */
    .qr-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(245,255,255,0.98));
        padding: 14px;
        border-radius: 10px;
        display: inline-block;
        border: 1px solid rgba(0,0,0,0.03);
    }

    /* Small header style */
    .small-muted {
        color: #4b6b7a;
        font-size: 13px;
    }

    /* Make Streamlit wide columns look nicer */
    .stButton>button {
        background-color: #0b6fa4;
        color: white;
        border-radius: 8px;
        padding: 8px 14px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Title area with subtle header like the sample ---
st.markdown("<div style='display:flex;align-items:center;gap:12px'><h2 style='margin:0'>Générateur 2D‑Doc CIN TD1</h2><div class='small-muted'>Aperçu et export (factice)</div></div>", unsafe_allow_html=True)
st.markdown("---")

# --- Layout: left form + vertical divider + right preview (like the first image) ---
left_col, divider_col, right_col = st.columns([2.6, 0.12, 1.6])

with left_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Données de la CIN")
    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom", value="RABEARIMANANA")
        prenom = st.text_input("Prénom", value="FANOMEZANTSOA")
    with col2:
        dob = st.date_input("Date de naissance")
        num = st.text_input("Numéro CIN", value="CIN12345678")

    doc_type = st.text_input("Code document (placeholder)", value="TD1CIN")
    issuer = st.text_input("Émetteur (placeholder)", value="FRANCE")

    symbologie_options = ["QR Code"]
    if DATAMATRIX_AVAILABLE:
        symbologie_options.append("DataMatrix")
    symbologie = st.selectbox("Symbologie", options=symbologie_options)

    st.markdown("**Remarque** : ceci est un 2D‑Doc factice pour tests. Il ne sera pas reconnu comme authentique par l’ANTS.", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with divider_col:
    # Render the decorative vertical divider using HTML/CSS
    st.markdown(
        """
        <div class="vertical-divider">
            <div style="position:relative">
                <div class="bar"></div>
                <div class="dot" style="top:18px"></div>
                <div class="dot" style="top:90px"></div>
                <div class="dot" style="top:170px"></div>
                <div class="dot" style="top:250px"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Aperçu 2D‑Doc (chaîne encodée)")
    # --- Build message and 2D-Doc string ---
    def build_message(doc_type: str, issuer: str, fields: dict) -> str:
        parts = [f"TYPE:{doc_type}", f"ISS:{issuer}"]
        for k, v in fields.items():
            parts.append(f"{k}:{v}")
        return "\x1d".join(parts)

    fields = {
        "NOM": nom.strip(),
        "PRENOM": prenom.strip(),
        "DOB": dob.isoformat(),
        "NUM": num.strip()
    }
    message = build_message(doc_type, issuer, fields)

    # Signature factice ECDSA for test
    def sign_message_ecdsa(message_bytes: bytes):
        private_key = ec.generate_private_key(ec.SECP256R1())
        signature = private_key.sign(message_bytes, ec.ECDSA(hashes.SHA256()))
        public_key_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return signature, public_key_pem

    signature, public_key_pem = sign_message_ecdsa(message.encode("utf-8"))
    signature_b64 = base64.b64encode(signature).decode("ascii")

    header = "DC03FR01"  # en-tête factice
    two_d_doc_string = header + message + "\x1f" + "SIG:" + signature_b64

    # Show encoded string preview (truncate if long)
    preview = two_d_doc_string if len(two_d_doc_string) <= 600 else two_d_doc_string[:600] + "..."
    st.code(preview, language="text")

    # Insert the requested explanatory rendering text exactly as provided
    st.markdown(
        """
        **Comment distinguer visuellement les deux symbologies :**

        - **Présence de trois grands carrés dans les coins supérieurs gauche/droit et inférieur gauche → QR Code.** Ces marqueurs (finder patterns) sont la signature visuelle du QR.

        - **Absence de ces marqueurs et motif plus homogène, parfois avec une bordure solide en forme de L → DataMatrix (ou autre symbologie 2D sans finder patterns).**

        - **Zone blanche autour du code (quiet zone) est typique des QR ; DataMatrix peut paraître plus « collé » au fond.**

        - **Si le code montre petits modules très serrés et pas de gros marqueurs, il s’agit très probablement d’un DataMatrix.**
        """,
        unsafe_allow_html=True,
    )

    # QR/DataMatrix generation functions
    def make_qr_png_bytes(data: str, scale: int = 6, border: int = 4) -> bytes:
        qr = segno.make(data, error='h')
        buf = io.BytesIO()
        qr.save(buf, kind='png', scale=scale, border=border)
        buf.seek(0)
        return buf.read()

    def make_datamatrix_png_bytes(data: str) -> bytes:
        if not DATAMATRIX_AVAILABLE:
            raise RuntimeError("pylibdmtx non disponible dans cet environnement.")
        encoded = dmtx_encode(data.encode('utf-8'))
        if isinstance(encoded, bytes):
            return encoded
        if hasattr(encoded, "save"):
            buf = io.BytesIO()
            encoded.save(buf, format="PNG")
            return buf.getvalue()
        raise RuntimeError("Format de sortie DataMatrix inattendu.")

    # Generate and display image inline with a styled card similar to the sample
    if st.button("Générer 2D‑Doc"):
        try:
            if symbologie == "QR Code":
                png_bytes = make_qr_png_bytes(two_d_doc_string)
            else:
                try:
                    png_bytes = make_datamatrix_png_bytes(two_d_doc_string)
                except Exception:
                    st.warning("DataMatrix non disponible. Génération QR effectuée à la place.")
                    png_bytes = make_qr_png_bytes(two_d_doc_string)

            # Display QR inside a small styled container to mimic printed card
            b64 = base64.b64encode(png_bytes).decode("ascii")
            st.markdown("<div class='qr-card' style='text-align:center'>", unsafe_allow_html=True)
            st.image(Image.open(io.BytesIO(png_bytes)), caption=None, use_column_width=False)
            st.markdown("</div>", unsafe_allow_html=True)

            # Show signature and public key for debug/test
            st.markdown("**Signature (base64)**")
            st.code(signature_b64, language="text")
            st.markdown("**Clé publique de test (PEM)**")
            st.code(public_key_pem.decode("utf-8"), language="text")

            # Download button
            st.download_button(
                label="Télécharger PNG",
                data=png_bytes,
                file_name="2ddoc_cin_td1.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Footer note ---
st.markdown("---")
st.caption("Rendu inspiré de l'exemple visuel. Usage pédagogique uniquement — pour production, respecter la spec ANTS et signer avec la clé officielle.")
