from pylibdmtx.pylibdmtx import encode
from PIL import Image
import io

def generate_datamatrix(data: str):
    encoded = encode(data.encode("utf-8"))

    image = Image.frombytes(
        'RGB',
        (encoded.width, encoded.height),
        encoded.pixels
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
