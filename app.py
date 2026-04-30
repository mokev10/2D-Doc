# app.py
import streamlit as st
import io
import base64
from PIL import Image
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# --- IMPORTANT: This app enforces DataMatrix only (pas de fallback QR) ---
# Si pylibdmtx n'est pas installé, l'application affichera un message clair
# et la génération sera désactivée. Pour exécuter l'app avec DataMatrix,
# déployez via Docker (Dockerfile fourni) ou installez libdmtx-dev + pylibdmtx.

# Tentative d'import DataMatrix (obligatoire)
try:
    from pylibdmtx import encode as dmtx_encode
    DATAMATRIX_AVAILABLE = True
except Exception:
    DATAMATRIX_AVAILABLE = False

# --- Page config (corrigé selon ta demande) ---
st.set_page_config(
    page_title="Générateur 2D-Codes Data Matrix",
    page_icon="https://img.icons8.com/external-duo-tone-yogi-aprelliyanto/24/external-search-file-document-duo-tone-yogi-aprelliyanto.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS pour rendu visuel similaire à l'exemple ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #eaf6fb;
        background-image:
            radial-gradient(circle at 10% 20%, rgba(255,255,255,0.6) 0px, rgba(255,255,255,0.0) 2px),
            radial-gradient(circle at 80% 80%, rgba(255,255,255,0.6) 0px, rgba(255,255,255,0.0) 2px),
            repeating-linear-gradient(45deg, rgba(0,0,0,0.02) 0px, rgba(0,0,0,0.02) 1px, transparent 1px, transparent 20px);
        background-size: 120px 120px, 120px 120px, 100% 100%;
    }
    .card {
        background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(250,250,255,0.95));
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(20,40,60,0.08);
        border: 1px solid rgba(0,0,0,0.04);
    }
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
    .qr-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(245,255,255,0.98));
        padding: 14px;
        border-radius: 10px;
        display: inline-block;
        border: 1px solid rgba(0,0,0,0.03);
    }
    .small-muted { color: #4b6b7a; font-size: 13px; }
    .stButton>button { background-color: #0b6fa4; color: white; border-radius: 8px; padding: 8px 14px; border: none; }
    .warning-box {
        background: #fff4e5;
        border-left: 4px solid #ffb020;
        padding: 10px 14px;
        border-radius: 6px;
        color: #6b4b00;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown(
    "<div style='display:flex;align-items:center;gap:12px'>"
    "<h2 style='margin:0'>Générateur 2D‑Codes Data Matrix</h2>"
    "<div class='small-muted'>Aperçu et export (factice) — DataMatrix obligatoire</div>"
    "</div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- Layout: left form + decorative divider + right preview ---
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

    # Symbologie forcée : DataMatrix (pas d'option pour QR)
    st.markdown("**Symbologie : DataMatrix (obligatoire)**", unsafe_allow_html=True)

    st.markdown("**Remarque** : ceci est un rendu factice pour tests. Il ne sera pas reconnu comme authentique par l’ANTS.", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with divider_col:
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
    st.subheader("Aperçu 2D‑Codes (chaîne encodée)")

    # Construire la zone message (séparateurs factices)
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
    two_d_string = header + message + "\x1f" + "SIG:" + signature_b64

    preview = two_d_string if len(two_d_string) <= 600 else two_d_string[:600] + "..."
    st.code(preview, language="text")

    # Si pylibdmtx absent : afficher message d'erreur explicite et désactiver génération
    if not DATAMATRIX_AVAILABLE:
        st.markdown(
            """
            <div class="warning-box">
            <strong>Erreur :</strong> <em>pylibdmtx (DataMatrix) n'est pas installé dans cet environnement.</em><br>
            Le rendu DataMatrix ne fonctionnera pas tant que la dépendance système <code>libdmtx</code> et le paquet Python <code>pylibdmtx</code> ne sont pas présents.<br><br>
            <strong>Solutions recommandées :</strong>
            <ul>
              <li>Déployer via <code>Docker</code> en utilisant le <code>Dockerfile</code> fourni (installe <code>libdmtx-dev</code> puis <code>pylibdmtx</code>).</li>
              <li>Ou déployer sur une plateforme qui accepte un <code>Dockerfile</code> (Render, Railway avec Docker, VPS, etc.).</li>
            </ul>
            L'application a désactivé la génération tant que DataMatrix n'est pas disponible.
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Bouton désactivé visuellement : on affiche un bouton inactif (non cliquable)
        st.button("Générer DataMatrix (indisponible)", disabled=True)
        # Afficher instructions courtes pour Docker (copier-coller)
        st.markdown("**Commande Docker recommandée (local / CI) :**")
        st.code(
            "docker build -t 2ddoc-app:latest . && docker run --rm -p 8501:8501 2ddoc-app:latest",
            language="bash",
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Génération DataMatrix (pylibdmtx disponible)
        def make_datamatrix_png_bytes(data: str) -> bytes:
            # pylibdmtx.encode retourne généralement bytes (PNG)
            encoded = dmtx_encode(data.encode('utf-8'))
            if isinstance(encoded, bytes):
                return encoded
            if hasattr(encoded, "save"):
                buf = io.BytesIO()
                encoded.save(buf, format="PNG")
                return buf.getvalue()
            raise RuntimeError("Format de sortie DataMatrix inattendu.")

        if st.button("Générer DataMatrix"):
            try:
                png_bytes = make_datamatrix_png_bytes(two_d_string)

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
                    file_name="2ddoc_datamatrix.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Erreur lors de la génération DataMatrix : {e}")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Usage pédagogique uniquement — pour production, respecter la spec ANTS et signer avec la clé officielle.")
