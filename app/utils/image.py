import base64

def convert_bytes_image_to_base64(image_bytes: bytes) -> str:
    """
    Convert image bytes to base64 string.
    """
    
    return base64.b64encode(image_bytes).decode('utf-8')