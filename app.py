# app.py
"""
Générateur 2D-Codes Data Matrix — Application Streamlit complète et prête à copier-coller.

Objectif
- Afficher et gérer des images DataMatrix pré-générées stockées dans `static/datamatrix/`.
- Aucune génération à la volée : l'application suppose que les PNG ont été créés par CI (ex. GitHub Actions)
  et commités dans le dépôt.
- Interface claire : liste, filtre, aperçu, téléchargement, affichage de métadonnées (optionnel).

Structure attendue dans le dépôt
- static/datamatrix/<id>.png            # images DataMatrix pré-générées
- static/datamatrix_meta/<id>.txt|.json # (optionnel) chaîne encodée ou métadonnées
- data/datamatrix_inputs.json           # (optionnel) source utilisée par le CI pour générer les PNG
- scripts/generate_datamatrix.py        # (optionnel) script CI qui produit les PNG

Remarques
- Cette application force la symbologie DataMatrix : pas de fallback QR.
- Si aucune image n'est trouvée, l'app affiche des instructions claires pour la génération via CI.
"""

import os
import json
import streamlit as st
from pathlib import Path
from PIL import Image

# --- Page config (corrigé selon ta demande) ---
st.set_page_config(
    page_title="Générateur 2D-Codes Data Matrix",
    page_icon="https://img.icons8.com/external-duo-tone-yogi-aprelliyanto/24/external-search-file-document-duo-tone-yogi-aprelliyanto.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Configuration des chemins ---
DM_DIR = Path("static/datamatrix")           # dossier attendu pour les PNG
META_DIR = Path("static/datamatrix_meta")   # dossier optionnel pour métadonnées (.txt ou .json)
INPUTS_FILE = Path("data/datamatrix_inputs.json")  # optionnel, source pour CI
APP_TITLE = "Générateur 2D-Codes Data Matrix"
APP_SUBTITLE = "Affichage des DataMatrix pré-générés (pas de génération à la volée)"

# --- Styles simples pour lisibilité ---
st.markdown(
    """
    <style>
    .card { background: #ffffff; padding: 16px; border-radius: 10px; box-shadow: 0 6px 18px rgba(20,40,60,0.06); }
    .muted { color: #6b7a83; font-size: 13px; }
    .warning { background: #fff4e5; padding: 12px; border-left: 4px solid #ffb020; border-radius:6px; color:#6b4b00; }
    .info { background: #e8f6ff; padding: 10px; border-left: 4px solid #0b6fa4; border-radius:6px; color:#0b4b6a; }
    .small { font-size:12px; color:#6b7a83; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.markdown(f"<div style='display:flex;align-items:center;gap:12px'><h1 style='margin:0'>{APP_TITLE}</h1><div class='muted'>{APP_SUBTITLE}</div></div>", unsafe_allow_html=True)
st.markdown("---")

# --- Helpers ---
def list_png_files(directory: Path):
    """Retourne la liste triée des fichiers .png dans le dossier (ou [] si absent)."""
    if not directory.exists() or not directory.is_dir():
        return []
    files = [p.name for p in sorted(directory.iterdir()) if p.suffix.lower() == ".png" and p.is_file()]
    return files

def read_text_metadata(meta_dir: Path, id_name: str):
    """
    Lit un fichier .txt ou .json associé à l'id et retourne une chaîne (ou None).
    Priorité : .txt, puis .json (champ 'payload'/'data'/'value'/'text').
    """
    if not meta_dir.exists() or not meta_dir.is_dir():
        return None
    txt_path = meta_dir / f"{id_name}.txt"
    if txt_path.exists():
        try:
            return txt_path.read_text(encoding="utf-8").strip()
        except Exception:
            return None
    json_path = meta_dir / f"{id_name}.json"
    if json_path.exists():
        try:
            j = json.loads(json_path.read_text(encoding="utf-8"))
            for key in ("payload", "data", "value", "text"):
                if key in j:
                    return str(j[key])
            return json.dumps(j, ensure_ascii=False)
        except Exception:
            return None
    return None

def safe_open_image(path: Path):
    """Ouvre une image PIL en gérant les erreurs et renvoie (image, error_message)."""
    try:
        img = Image.open(path)
        img.load()
        return img, None
    except Exception as e:
        return None, str(e)

# --- Layout : sidebar (contrôles) + main (aperçu) ---
sidebar, main = st.columns([1, 2])

with sidebar:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("Contrôles")
    st.markdown("**Symbologie :** DataMatrix (images pré‑générées uniquement)")
    st.markdown("**Dossier attendu :** `static/datamatrix/`")
    st.markdown("---")

    # Bouton rafraîchir
    if st.button("Rafraîchir la liste d'images"):
        st.experimental_rerun()

    # Filtre
    filter_text = st.text_input("Filtrer par identifiant (texte partiel)", value="")

    st.markdown("---")
    st.markdown("**Actions rapides**")
    st.markdown("- Vérifier l'onglet **Actions** sur GitHub si aucune image n'apparaît.")
    st.markdown("- Les images doivent être générées par CI et commitées dans `static/datamatrix/`.")
    st.markdown("</div>", unsafe_allow_html=True)

with main:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("Aperçu des DataMatrix pré-générés")

    files = list_png_files(DM_DIR)
    if filter_text:
        files = [f for f in files if filter_text.lower() in f.lower()]

    if not files:
        st.markdown("<div class='warning'><strong>Aucune image DataMatrix trouvée.</strong></div>", unsafe_allow_html=True)
        st.markdown("Vérifie que ton workflow GitHub Actions a généré et commit les PNG dans `static/datamatrix/`.")
        st.markdown("Si tu veux, je peux te fournir le script `scripts/generate_datamatrix.py` et le workflow GitHub Actions prêts à coller.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Sélection de fichier
        selected = st.selectbox("Sélectionner une image", options=files, index=0)
        st.markdown("---")

        selected_path = DM_DIR / selected

        # Aperçu image
        img, err = safe_open_image(selected_path)
        if err:
            st.error(f"Erreur lors de l'ouverture de l'image `{selected}` : {err}")
            st.markdown("Vérifie que le fichier est un PNG valide et non corrompu. Si le workflow CI a échoué, consulte les logs dans GitHub Actions.")
        else:
            st.image(img, caption=selected, use_column_width=False)

            # Téléchargement
            try:
                with open(selected_path, "rb") as f:
                    img_bytes = f.read()
                st.download_button("Télécharger l'image PNG", data=img_bytes, file_name=selected, mime="image/png")
            except Exception as e:
                st.error(f"Impossible de préparer le téléchargement : {e}")

            # Métadonnées (chaîne encodée)
            id_name = Path(selected).stem
            meta = read_text_metadata(META_DIR, id_name)
            st.markdown("**Chaîne encodée (métadonnées)**")
            if meta:
                st.code(meta, language="text")
            else:
                st.markdown("<div class='muted'>Aucune métadonnée trouvée pour cet identifiant. (Place un fichier .txt ou .json dans static/datamatrix_meta/)</div>", unsafe_allow_html=True)

            # Informations fichier
            try:
                size_kb = selected_path.stat().st_size / 1024.0
                st.markdown(f"**Informations fichier**  \n- Nom : `{selected}`  \n- Taille : {size_kb:.1f} KB  \n- Chemin : `{selected_path}`")
            except Exception:
                st.markdown("Informations fichier indisponibles.")

        st.markdown("</div>", unsafe_allow_html=True)

# --- Bas de page : instructions claires pour la génération via CI (résumé) ---
st.markdown("---")
st.subheader("Rappel : comment générer les DataMatrix via GitHub Actions (résumé)")

st.markdown(
    """
    1. Prépare `data/datamatrix_inputs.json` : liste d'objets `{ "id": "<id>", "payload": "<chaîne à encoder>" }`.
    2. Ajoute `scripts/generate_datamatrix.py` qui lit ce fichier et écrit `static/datamatrix/<id>.png` en utilisant `pylibdmtx`.
    3. Ajoute un workflow GitHub Actions qui :
       - installe `libdmtx-dev` et les dépendances système,
       - installe `pylibdmtx` et `Pillow`,
       - exécute `python scripts/generate_datamatrix.py`,
       - commit et push les images générées dans le repo.
    4. Pousse sur `main`. Vérifie l'onglet Actions → job `Generate DataMatrix PNGs`.
    """
)

st.markdown("**Note** : si tu déploies directement sur Streamlit Cloud sans Docker, n'inclus pas `pylibdmtx` dans `requirements.txt` (l'installation échouera). Utilise la pré‑génération via CI ou déploie via Docker sur une plateforme qui accepte des images Docker.")
