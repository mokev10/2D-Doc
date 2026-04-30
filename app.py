import streamlit as st
import segno
import io
import base64
from PIL import Image
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# Option DataMatrix si disponible
try:
    from pylibdmtx import encode as dmtx_encode
    DATAMATRIX_AVAILABLE = True
except Exception:
    DATAMATRIX_AVAILABLE = False

st.set_page_config(page_title="Générateur 2D-Doc CIN TD1", layout="centered")

st.title("Générateur 2D‑Doc factice pour CIN TD1")

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

symbologie = st.selectbox("Symbologie", options=["QR Code"] + (["DataMatrix"] if DATAMATRIX_AVAILABLE else []))

st.markdown("**Remarque** : ceci est un 2D‑Doc factice pour tests. Il ne sera pas reconnu comme authentique par l’ANTS.")

# --- Construire la zone message ---
def build_message(doc_type, issuer, fields):
    # Séparateurs factices : GS (\x1d) et US (\x1f)
    parts = [f"TYPE:{doc_type}", f"ISS:{issuer}"]
    for k, v in fields.items():
        parts.append(f"{k}:{v}")
    return "\x1d".join(parts)

fields = {
    "NOM": nom,
    "PRENOM": prenom,
    "DOB": dob.isoformat(),
    "NUM": num
}
message = build_message(doc_type, issuer, fields)

# --- Signature factice ECDSA pour test ---
def sign_message_ecdsa(message_bytes):
    # Génère une clé privée éphémère (test uniquement)
    private_key = ec.generate_private_key(ec.SECP256R1())
    signature = private_key.sign(message_bytes, ec.ECDSA(hashes.SHA256()))
    # Exporter la clé publique pour affichage si besoin (PEM)
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return signature, public_key

signature, public_key_pem = sign_message_ecdsa(message.encode("utf-8"))
signature_b64 = base64.b64encode(signature).decode("ascii")

# --- Construire la chaîne 2D-Doc finale ---
header = "DC03FR01"  # en-tête factice ; remplacer par en-tête conforme si disponible
two_d_doc_string = header + message + "\x1f" + "SIG:" + signature_b64

st.subheader("Aperçu 2D‑Doc (chaîne encodée)")
st.code(two_d_doc_string[:400] + ("..." if len(two_d_doc_string) > 400 else ""), language="text")

# --- Génération image selon symbologie ---
def make_qr_png_bytes(data, scale=6, border=4):
    qr = segno.make(data, error='h')
    buf = io.BytesIO()
    qr.save(buf, kind='png', scale=scale, border=border)
    buf.seek(0)
    return buf.read()

def make_datamatrix_png_bytes(data):
    # Utilise pylibdmtx.encode si disponible
    # encode retourne un objet bytes contenant l'image PNG
    encoded = dmtx_encode(data.encode('utf-8'))
    # pylibdmtx.encode peut renvoyer bytes ou un objet; on convertit en bytes si nécessaire
    if isinstance(encoded, bytes):
        return encoded
    # Si c'est un PIL Image, convertir
    if hasattr(encoded, "tobytes"):
        buf = io.BytesIO()
        encoded.save(buf, format="PNG")
        return buf.getvalue()
    raise RuntimeError("Impossible de générer DataMatrix avec la bibliothèque installée.")

if st.button("Générer 2D‑Doc"):
    try:
        if symbologie == "QR Code":
            png_bytes = make_qr_png_bytes(two_d_doc_string)
        else:
            png_bytes = make_datamatrix_png_bytes(two_d_doc_string)

        # Afficher l'image
        img = Image.open(io.BytesIO(png_bytes))
        st.image(img, caption="2D‑Doc factice", use_column_width=False)

        # Afficher clé publique de test et signature
        st.subheader("Signature et clé publique de test")
        st.code(f"Signature (base64): {signature_b64}", language="text")
        st.code(public_key_pem.decode("utf-8"), language="text")

        # Bouton de téléchargement
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
st.caption("Usage pédagogique uniquement. Pour un 2D‑Doc officiel, utiliser les certificats et spécifications ANTS.")
