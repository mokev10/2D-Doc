# app.py
import streamlit as st
import io
import base64
from PIL import Image
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Essayer d'importer pylibdmtx (DataMatrix). Si absent, on proposera un fallback QR.
try:
    from pylibdmtx import encode as dmtx_encode
    DATAMATRIX_AVAILABLE = True
except Exception:
    DATAMATRIX_AVAILABLE = False

# Segno pour QR fallback si nécessaire
try:
    import segno
    SEGNO_AVAILABLE = True
except Exception:
    SEGNO_AVAILABLE = False

# --- Page config ---
st.set_page_config(
    page_title="Générateur 2D-Doc CIN TD1 (DataMatrix)",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS pour rendu visuel similaire ---
st.markdown(
    """
    <style>
    .stApp { background-color: #eaf6fb; }
    .card { background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(250,250,255,0.96)); border-radius:12px; padding:16px; box-shadow:0 6px 18px rgba(20,40,60,0.06); }
    .vertical-divider { width:28px; display:flex; align-items:center; justify-content:center; }
    .vertical-divider .bar { width:2px; height:320px; background:linear-gradient(180deg,#0b6fa4,#6fc3e8); border-radius:2px; position:relative; }
    .qr-card { background: #fff; padding:12px; border-radius:10px; display:inline-block; border:1px solid rgba(0,0,0,0.03); }
    .small-muted { color:#4b6b7a; font-size:13px; }
    .stButton>button { background-color:#0b6fa4; color:white; border-radius:8px; padding:8px 14px; border:none; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='display:flex;align-items:center;gap:12px'><h2 style='margin:0'>Générateur 2D‑Doc CIN TD1</h2><div class='small-muted'>DataMatrix par défaut (factice)</div></div>", unsafe_allow_html=True)
st.markdown("---")

# --- Layout ---
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

    # Symbologie par défaut : DataMatrix. On propose QR uniquement si DataMatrix indisponible.
    if DATAMATRIX_AVAILABLE:
        symbologie = st.selectbox("Symbologie", options=["DataMatrix", "QR Code"])
    else:
        symbologie = st.selectbox("Symbologie", options=(["QR Code"] if SEGNO_AVAILABLE else ["DataMatrix (non disponible)"]))
        if symbologie.startswith("DataMatrix") and not DATAMATRIX_AVAILABLE:
            st.warning("pylibdmtx (DataMatrix) non installé dans cet environnement. Le rendu DataMatrix ne fonctionnera pas ici.")

    st.markdown("**Remarque** : ceci est un 2D‑Doc factice pour tests. Il ne sera pas reconnu comme authentique par l’ANTS.", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with divider_col:
    st.markdown(
        """
        <div class="vertical-divider">
            <div style="position:relative">
                <div class="bar"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Aperçu 2D‑Doc (chaîne encodée)")

    # Construire message (séparateurs factices)
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

    # Signature factice ECDSA (test)
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

    preview = two_d_doc_string if len(two_d_doc_string) <= 600 else two_d_doc_string[:600] + "..."
    st.code(preview, language="text")

    # Explication visuelle (comme demandé)
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

    # --- Génération DataMatrix / QR ---
    def make_datamatrix_png_bytes(data: str) -> bytes:
        if not DATAMATRIX_AVAILABLE:
            raise RuntimeError("pylibdmtx non disponible dans cet environnement.")
        # pylibdmtx.encode retourne généralement bytes (PNG)
        encoded = dmtx_encode(data.encode('utf-8'))
        if isinstance(encoded, bytes):
            return encoded
        # Si c'est un PIL Image-like object
        if hasattr(encoded, "save"):
            buf = io.BytesIO()
            encoded.save(buf, format="PNG")
            return buf.getvalue()
        raise RuntimeError("Format de sortie DataMatrix inattendu.")

    def make_qr_png_bytes(data: str, scale: int = 6, border: int = 4) -> bytes:
        if not SEGNO_AVAILABLE:
            raise RuntimeError("segno non disponible pour QR fallback.")
        qr = segno.make(data, error='h')
        buf = io.BytesIO()
        qr.save(buf, kind='png', scale=scale, border=border)
        buf.seek(0)
        return buf.read()

    if st.button("Générer 2D‑Doc"):
        try:
            if symbologie == "DataMatrix":
                try:
                    png_bytes = make_datamatrix_png_bytes(two_d_doc_string)
                except Exception as e:
                    st.error(f"Impossible de générer DataMatrix ici : {e}")
                    if SEGNO_AVAILABLE:
                        st.info("Génération QR effectuée en fallback.")
                        png_bytes = make_qr_png_bytes(two_d_doc_string)
                    else:
                        raise
            else:
                png_bytes = make_qr_png_bytes(two_d_doc_string)

            # Affichage et téléchargement
            st.markdown("<div class='qr-card' style='text-align:center'>", unsafe_allow_html=True)
            st.image(Image.open(io.BytesIO(png_bytes)), use_column_width=False)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("**Signature (base64)**")
            st.code(signature_b64, language="text")
            st.markdown("**Clé publique de test (PEM)**")
            st.code(public_key_pem.decode("utf-8"), language="text")

            st.download_button(
                label="Télécharger PNG",
                data=png_bytes,
                file_name="2ddoc_datamatrix.png" if symbologie == "DataMatrix" else "2ddoc_qr.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Usage pédagogique uniquement — pour production, respecter la spec ANTS et signer avec la clé officielle.")
