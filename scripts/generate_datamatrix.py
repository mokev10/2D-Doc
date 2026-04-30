import treepoem
import io

def generate_datamatrix(data: str):
    image = treepoem.generate_barcode(
        barcode_type='datamatrix',
        data=data
    )

    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
