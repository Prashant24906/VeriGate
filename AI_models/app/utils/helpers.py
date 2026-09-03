import io
import base64
import numpy as np
from PIL import Image
import cv2


def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Convert raw image bytes to OpenCV BGR image array."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes")
    return img


def cv2_to_bytes(img: np.ndarray, format: str = ".jpg") -> bytes:
    """Convert OpenCV BGR image array to bytes."""
    success, encoded_img = cv2.imencode(format, img)
    if not success:
        raise ValueError("Could not encode image to bytes")
    return encoded_img.tobytes()


def cv2_to_base64(img: np.ndarray, format: str = "png") -> str:
    """Convert OpenCV BGR image array to Base64 data URI string."""
    fmt_ext = f".{format}"
    success, encoded_img = cv2.imencode(fmt_ext, img)
    if not success:
        return ""
    b64_str = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
    return f"data:image/{format};base64,{b64_str}"


def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV BGR array."""
    rgb = np.array(pil_img.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """Convert OpenCV BGR array to PIL Image."""
    rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def create_heatmap_overlay(original: np.ndarray, diff_mask: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """
    Overlays a color heatmap on original image based on a single-channel difference mask.
    """
    # Normalize diff_mask to 0-255
    if diff_mask.max() > 0:
        norm_mask = (diff_mask / diff_mask.max() * 255).astype(np.uint8)
    else:
        norm_mask = diff_mask.astype(np.uint8)

    heatmap = cv2.applyColorMap(norm_mask, cv2.COLORMAP_JET)
    
    # Resize heatmap to match original if needed
    if heatmap.shape[:2] != original.shape[:2]:
        heatmap = cv2.resize(heatmap, (original.shape[1], original.shape[0]))
        
    overlay = cv2.addWeighted(original, 1 - alpha, heatmap, alpha, 0)
    return overlay
