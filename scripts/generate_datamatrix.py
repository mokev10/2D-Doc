# scripts/generate_datamatrix.py
import os
import base64
from pylibdmtx import encode as dmtx_encode
from PIL import Image
import io
import json

# Exemple : lire un fichier JSON d'entrées à encoder
INPUT_FILE = "data/datamatrix_inputs.json"
OUT_DIR = "static/datamatrix"

os.makedirs(OUT_DIR, exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    items = json.load(f)  # liste d'objets { "id": "...", "payload": "..." }

for item in items:
    payload = item["payload"]
    png_bytes = dmtx_encode(payload.encode("utf-8"))
    # pylibdmtx.encode peut retourner bytes (PNG)
    if isinstance(png_bytes, bytes):
        out_path = os.path.join(OUT_DIR, f"{item['id']}.png")
        with open(out_path, "wb") as out:
            out.write(png_bytes)
        print("WROTE", out_path)
    else:
        # fallback si objet PIL-like
        buf = io.BytesIO()
        png_bytes.save(buf, format="PNG")
        out_path = os.path.join(OUT_DIR, f"{item['id']}.png")
        with open(out_path, "wb") as out:
            out.write(buf.getvalue())
        print("WROTE", out_path)
