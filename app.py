# app.py
"""
Générateur 2D‑Codes DataMatrix (affichage des images pré-générées)

Ce fichier est une version complète et prête à copier-coller.
Il suppose que les images DataMatrix sont pré-générées et stockées dans :
    static/datamatrix/<id>.png

Flux attendu :
- Tu fournis un workflow GitHub Actions qui génère les PNG et les commit dans static/datamatrix/.
- Streamlit Cloud déploie le site depuis le repo ; l'app sert alors les PNG statiques.
- Cette application n'essaie pas de générer des DataMatrix à la volée : elle affiche uniquement les images présentes.

Fonctionnalités :
- Liste des images DataMatrix présentes dans static/datamatrix/
- Aperçu, téléchargement et affichage d'une image sélectionnée
- Affichage de la chaîne encodée (si un fichier .txt associé existe)
- Message clair et instructions si aucune image n'est trouvée
- UI complète avec CSS pour un rendu soigné
"""

import os
import io
import base64
import streamlit as st
from PIL import Image

# --- Configuration ---
DM_DIR = "static/datamatrix"  # dossier où les PNG pré-générés doivent être placés
METADATA_DIR = "static/datamatrix_meta"  # optionnel : fichiers .txt ou .json décrivant la payload
APP_TITLE = "Générateur 2D‑Codes DataMatrix (pré‑généré)"
APP_SUBTITLE = "Affichage des DataMatrix générés via CI (GitHub Actions)"

# --- Page config ---
st.set_page_config(
    page_title="Générateur 2D-Codes Data Matrix",
    page_icon="https://img.icons8.com/external-duo-tone-yogi-aprelliyanto/24/external-search-file-document-duo-tone-yogi-aprelliyanto.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS pour rendu visuel similaire ---
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
        background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(250,250,255,0.96));
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(20,40,60,0.06);
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
    .muted {
        color: #6b7a83;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown(
    f"<div style='display:flex;align-items:center;gap:12px'><h2 style='margin:0'>{APP_TITLE}</h2><div class='small-muted'>{APP_SUBTITLE}</div></div>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- Layout: sidebar for controls, main for preview ---
sidebar_col, main_col = st.columns([1, 3])

with sidebar_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Contrôles")
    st.markdown("**Symbologie :** DataMatrix (images pré‑générées uniquement)", unsafe_allow_html=True)
    st.markdown("**Dossier attendu** : `static/datamatrix/`", unsafe_allow_html=True)
    st.markdown("---")

    # Option : rafraîchir la liste (simple bouton)
    if st.button("Rafraîchir la liste d'images"):
        st.experimental_rerun()

    st.markdown("**Filtrer par identifiant**", unsafe_allow_html=True)
    filter_text = st.text_input("Recherche (id partiel)", value="")

    st.markdown("---")
    st.markdown("**Instructions rapides**", unsafe_allow_html=True)
    st.markdown(
        """
        - Les images DataMatrix doivent être générées par CI (GitHub Actions) et commit dans `static/datamatrix/`.
        - Nom de fichier attendu : `<id>.png` (ex : `cin_001.png`).
        - Optionnel : placer un fichier texte `static/datamatrix_meta/<id>.txt` contenant la chaîne encodée.
        - Si aucune image n'est trouvée, vérifie l'exécution du workflow GitHub Actions.
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# --- Helper functions ---
def list_datamatrix_files(directory: str):
    if not os.path.isdir(directory):
        return []
    files = [f for f in os.listdir(directory) if f.lower().endswith(".png")]
    files.sort()
    return files

def read_metadata_for_id(meta_dir: str, id_name: str):
    """
    Cherche un fichier texte ou JSON associé à l'id et retourne son contenu (string).
    Priorité : .txt, puis .json (champ 'payload' ou 'data').
    """
    if not os.path.isdir(meta_dir):
        return None
    txt_path = os.path.join(meta_dir, f"{id_name}.txt")
    if os.path.isfile(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return None
    json_path = os.path.join(meta_dir, f"{id_name}.json")
    if os.path.isfile(json_path):
        try:
            import json as _json
            with open(json_path, "r", encoding="utf-8") as f:
                j = _json.load(f)
            # Chercher champs usuels
            for key in ("payload", "data", "value", "text"):
                if key in j:
                    return str(j[key])
            # fallback : stringify
            return _json.dumps(j, ensure_ascii=False)
        except Exception:
            return None
    return None

def get_image_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

# --- Main area: list and preview ---
with main_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Aperçu des DataMatrix pré-générés")

    files = list_datamatrix_files(DM_DIR)
    if filter_text:
        files = [f for f in files if filter_text.lower() in f.lower()]

    if not files:
        st.markdown(
            """
            <div class="warning-box">
            <strong>Aucune image DataMatrix trouvée.</strong><br>
            Vérifie que ton workflow GitHub Actions a généré et committé les PNG dans <code>static/datamatrix/</code>.<br><br>
            Si tu veux, voici un rappel rapide du workflow recommandé :
            <ul>
              <li>Action CI installe <code>libdmtx-dev</code> et <code>pylibdmtx</code>.</li>
              <li>Le script <code>scripts/generate_datamatrix.py</code> lit <code>data/datamatrix_inputs.json</code> et écrit <code>static/datamatrix/&lt;id&gt;.png</code>.</li>
              <li>Le job commit et push les images générées dans le repo.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Sidebar selection of file
        st.markdown("**Images trouvées**", unsafe_allow_html=True)
        cols = st.columns([1, 2])
        with cols[0]:
            selected = st.selectbox("Sélectionner un fichier", options=files, index=0)
        with cols[1]:
            st.markdown("**Actions**")
            # Download selected image (serve bytes)
            selected_path = os.path.join(DM_DIR, selected)
            try:
                img_bytes = get_image_bytes(selected_path)
                st.download_button(
                    label="Télécharger l'image PNG",
                    data=img_bytes,
                    file_name=selected,
                    mime="image/png",
                )
            except Exception:
                st.error("Impossible de lire le fichier sélectionné pour le téléchargement.")

        # Display preview and metadata
        st.markdown("---")
        st.markdown(f"**Aperçu : {selected}**")
        try:
            image = Image.open(os.path.join(DM_DIR, selected))
            st.image(image, use_column_width=False)
        except Exception as e:
            st.error(f"Erreur lors de l'ouverture de l'image : {e}")

        # Show metadata if exists
        id_name = os.path.splitext(selected)[0]
        meta = read_metadata_for_id(METADATA_DIR, id_name)
        if meta:
            st.markdown("**Chaîne encodée (métadonnées)**")
            st.code(meta, language="text")
        else:
            st.markdown("**Chaîne encodée (métadonnées)**")
            st.markdown("<div class='muted'>Aucune métadonnée trouvée pour cet identifiant (fichier .txt ou .json attendu dans static/datamatrix_meta/).</div>", unsafe_allow_html=True)

        # Show small debug info
        st.markdown("---")
        st.markdown("**Informations fichier**")
        try:
            size_kb = os.path.getsize(os.path.join(DM_DIR, selected)) / 1024.0
            st.markdown(f"- Nom : **{selected}**  \n- Taille : **{size_kb:.1f} KB**  \n- Chemin : `{os.path.join(DM_DIR, selected)}`")
        except Exception:
            st.markdown("- Informations fichier indisponibles.")

        st.markdown("</div>", unsafe_allow_html=True)

# --- Footer with helpful links/instructions ---
st.markdown("---")
st.markdown(
    """
    **Notes de déploiement et recommandations**

    - Si tu veux générer les DataMatrix automatiquement depuis GitHub, utilise un workflow GitHub Actions
      qui installe `libdmtx-dev` puis `pylibdmtx`, exécute `scripts/generate_datamatrix.py` et commit les PNG dans `static/datamatrix/`.
    - N'ajoute pas `pylibdmtx` dans `requirements.txt` si tu déploies directement sur Streamlit Cloud sans Docker : l'installation échouera.
    - Pour un flux dynamique (génération à la volée), déploie l'application via Docker sur une plateforme qui accepte des images Docker.
    """,
    unsafe_allow_html=True,
)

# --- End ---
