"""
Converters app
"""

import io
from PIL import Image


def convert_bytes_image_to_webp(bytes_image: bytes) -> bytes:
    """
    Convert bytes image to webp
    """
    ig_bf = io.BytesIO(bytes_image)
    img = Image.open(ig_bf)
    img_io = io.BytesIO()
    img.save(img_io, format="webp")
    return img_io.getvalue()