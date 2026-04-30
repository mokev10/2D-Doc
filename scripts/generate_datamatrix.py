import requests
import io

def generate_datamatrix(data: str, dpi: int = 150):
    url = "https://barcode.tec-it.com/barcode.ashx"

    params = {
        "data": data,
        "code": "DataMatrix",
        "multiplebarcodes": "false",
        "translate-esc": "true",
        "dpi": dpi
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception("Erreur génération DataMatrix")

    return io.BytesIO(response.content)
