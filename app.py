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

# Page config
st.set_page_config(page_title="Générateur 2D-Doc CIN TD1", layout="centered")

st.title("Générateur 2D‑Doc factice pour CIN TD1")
st.markdown(
    "**Usage pédagogique uniquement.** Ce 2D‑Doc est factice et **ne sera pas** reconnu comme authentique par l'ANTS."
)

# --- Formulaire utilisateur ---
st.header("Données de la CIN")
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

# --- Construire la zone message ---
def build_message(doc_type: str, issuer: str, fields: dict) -> str:
    """
    Construit la zone message factice.
    Utilise GS (\x1d) comme séparateur de champs et US (\x1f) pour séparer message/signature.
    """
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

# --- Signature factice ECDSA pour test ---
def sign_message_ecdsa(message_bytes: bytes):
    """
    Génère une clé privée éphémère et signe le message.
    Retourne (signature_bytes, public_key_pem_bytes).
    Usage: test uniquement. En production, utiliser la clé officielle.
    """
    private_key = ec.generate_private_key(ec.SECP256R1())
    signature = private_key.sign(message_bytes, ec.ECDSA(hashes.SHA256()))
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return signature, public_key_pem

signature, public_key_pem = sign_message_ecdsa(message.encode("utf-8"))
signature_b64 = base64.b64encode(signature).decode("ascii")

# --- Construire la chaîne 2D-Doc finale ---
# NOTE: header factice. Pour production, remplacer par l'en-tête conforme ANTS.
header = "DC03FR01"
two_d_doc_string = header + message + "\x1f" + "SIG:" + signature_b64

st.subheader("Aperçu 2D‑Doc (chaîne encodée)")
preview = two_d_doc_string if len(two_d_doc_string) <= 800 else two_d_doc_string[:800] + "..."
st.code(preview, language="text")

# --- Génération image selon symbologie ---
def make_qr_png_bytes(data: str, scale: int = 6, border: int = 4) -> bytes:
    qr = segno.make(data, error='h')
    buf = io.BytesIO()
    qr.save(buf, kind='png', scale=scale, border=border)
    buf.seek(0)
    return buf.read()

def make_datamatrix_png_bytes(data: str) -> bytes:
    """
    Utilise pylibdmtx.encode si disponible.
    Retourne bytes PNG.
    """
    if not DATAMATRIX_AVAILABLE:
        raise RuntimeError("pylibdmtx non disponible dans cet environnement.")
    encoded = dmtx_encode(data.encode('utf-8'))
    # pylibdmtx.encode retourne généralement bytes (PNG). Si c'est un objet PIL, on convertit.
    if isinstance(encoded, bytes):
        return encoded
    if hasattr(encoded, "save"):
        buf = io.BytesIO()
        encoded.save(buf, format="PNG")
        return buf.getvalue()
    raise RuntimeError("Format de sortie DataMatrix inattendu.")

# --- Interface de génération et téléchargement ---
if st.button("Générer 2D‑Doc"):
    try:
        if symbologie == "QR Code":
            png_bytes = make_qr_png_bytes(two_d_doc_string)
        else:
            try:
                png_bytes = make_datamatrix_png_bytes(two_d_doc_string)
            except Exception as e:
                st.warning("DataMatrix non disponible ou erreur lors de la génération. Génération QR effectuée à la place.")
                png_bytes = make_qr_png_bytes(two_d_doc_string)

        # Afficher l'image
        img = Image.open(io.BytesIO(png_bytes))
        st.image(img, caption="2D‑Doc factice", use_column_width=False)

        # Afficher signature et clé publique de test
        st.subheader("Signature et clé publique de test")
        st.code(f"Signature (base64): {signature_b64}", language="text")
        st.code(public_key_pem.decode("utf-8"), language="text")

        # Téléchargement
        st.download_button(
            label="Télécharger PNG",
            data=png_bytes,
            file_name="2ddoc_cin_td1.png",
            mime="image/png"
        )
    except Exception as e:
        st.error(f"Erreur lors de la génération : {e}")

# --- Footer ---
st.markdown("---")
st.caption("Ne pas utiliser en production. Pour un 2D‑Doc officiel, respecter la spec ANTS et signer avec la clé officielle fournie par l'autorité.")
