import base64

from PIL import Image
import io
import os
from pathlib import Path
import uuid



def convert_bytes_image_to_base64(image_bytes: bytes) -> str:
    """
    Convert image bytes to base64 string.
    """
    
    return base64.b64encode(image_bytes).decode('utf-8')


def save_as_webp(image_bytes: bytes,  quality: int = 100):
    """
    Convert image bytes to WEBP and save it to the given path.
    `quality` controls the compression (0-100). Lower means smaller file, lower quality.
    """
    uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Generate a random UUID filename
    filename = f"{uuid.uuid4()}.webp"
    output_path = uploads_dir / filename

    # Open the image, convert, and save as webp
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image.save(output_path, format="WEBP", quality=quality, method=6)

    print(f"Saved image as: {output_path}")
    return output_path
