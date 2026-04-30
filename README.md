# Générateur 2D‑Doc CIN TD1 (DataMatrix par défaut)

**Projet pédagogique** — application Streamlit qui génère des codes 2D factices pour une **CIN format TD1**, avec **DataMatrix** comme symbologie par défaut et un fallback en **QR Code** si l’environnement ne permet pas l’encodage DataMatrix. Le rendu visuel imite l’exemple fourni (fond, carte, diviseur vertical).

---

## Contenu du dépôt

- `app.py` — application Streamlit complète (génération DataMatrix/QR, UI, CSS).
- `requirements.txt` — dépendances Python.
- `Dockerfile` — image Docker recommandée pour exécuter l’app avec support DataMatrix.
- `.dockerignore` — exclusions pour le build Docker.
- `docker-compose.yml` — configuration de développement local (optionnelle).
- `README.md` — ce fichier.

---

## Prérequis

### Local (développement)
- Python 3.10+ recommandé.
- `pip` à jour :
```bash
python -m pip install --upgrade pip setuptools wheel
