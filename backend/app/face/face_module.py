import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional
from app.config import config
from app.utils.helpers import cv2_to_base64

# Try importing DeepFace
try:
    from deepface import DeepFace
    HAS_DEEPFACE = True
except ImportError:
    HAS_DEEPFACE = False


# Helper for lazy cascade loading
def get_face_cascade():
    """Lazily load OpenCV Haar cascade to prevent import errors in serverless environments."""
    try:
        if hasattr(cv2, 'CascadeClassifier') and hasattr(cv2, 'data'):
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            cascade = cv2.CascadeClassifier(cascade_path)
            if not cascade.empty():
                return cascade
    except Exception:
        pass
    return None


def detect_and_crop_face(image: np.ndarray) -> Tuple[Optional[np.ndarray], bool, int]:
    """
    Detect face in image and return face crop, success flag, and total faces count.
    Uses Haar Cascade with scaleFactor=1.1 and minNeighbors=4.
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade = get_face_cascade()
        
        if cascade is not None:
            faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(40, 40))
        else:
            faces = []
        
        if len(faces) == 0:
            # Fallback crop center region if cascade fails or unavailable
            h, w = image.shape[:2]
            crop = image[int(h*0.1):int(h*0.7), int(w*0.15):int(w*0.85)]
            return crop, False, 0
            
        # Get largest face bounding box
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        x, y, w, h = faces[0]
        
        # Add padding around face
        pad_x = int(w * 0.15)
        pad_y = int(h * 0.15)
        img_h, img_w = image.shape[:2]
        
        y1 = max(0, y - pad_y)
        y2 = min(img_h, y + h + pad_y)
        x1 = max(0, x - pad_x)
        x2 = min(img_w, x + w + pad_x)
        
        face_crop = image[y1:y2, x1:x2]
        return face_crop, True, len(faces)
    except Exception:
        return None, False, 0


def compute_histogram_similarity(face1: np.ndarray, face2: np.ndarray) -> float:
    """
    Compute color & structural histogram correlation between two face crops.
    Returns similarity score between 0.0 and 1.0.
    """
    if face1 is None or face2 is None or face1.size == 0 or face2.size == 0:
        return 0.0
        
    try:
        f1_resized = cv2.resize(face1, (100, 100))
        f2_resized = cv2.resize(face2, (100, 100))
        
        hsv1 = cv2.cvtColor(f1_resized, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(f2_resized, cv2.COLOR_BGR2HSV)
        
        hist1 = cv2.calcHist([hsv1], [0, 1], None, [50, 60], [0, 180, 0, 256])
        hist2 = cv2.calcHist([hsv2], [0, 1], None, [50, 60], [0, 180, 0, 256])
        
        cv2.normalize(hist1, hist1, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 1, cv2.NORM_MINMAX)
        
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        # Normalize score to 0..1
        sim = max(0.0, min(1.0, float((correlation + 1.0) / 2.0)))
        return sim
    except Exception:
        return 0.0


def verify_face(document_image: np.ndarray, verification_image: np.ndarray) -> Dict[str, Any]:
    """
    1-to-1 Face Verification Interface.
    Compares face crop extracted from passport document against verification photograph.
    """
    if document_image is None or verification_image is None:
        return {
            "face_detected": False,
            "document_face_detected": False,
            "verification_face_detected": False,
            "similarity": 0.0,
            "match": False,
            "confidence": 0.0,
            "message": "Missing image input for face verification"
        }

    # 1. Detect and crop faces
    doc_crop, doc_face_found, doc_face_count = detect_and_crop_face(document_image)
    ver_crop, ver_face_found, ver_face_count = detect_and_crop_face(verification_image)

    doc_face_b64 = cv2_to_base64(doc_crop) if doc_crop is not None else ""
    ver_face_b64 = cv2_to_base64(ver_crop) if ver_crop is not None else ""

    if not doc_face_found and not ver_face_found:
        return {
            "face_detected": False,
            "document_face_detected": False,
            "verification_face_detected": False,
            "similarity": 0.0,
            "match": False,
            "confidence": 0.0,
            "document_face_b64": doc_face_b64,
            "verification_face_b64": ver_face_b64,
            "message": "No face could be detected in either document or verification photograph."
        }

    # 2. Compare faces
    similarity = 0.0
    engine_used = "OpenCV Feature Analysis"

    if HAS_DEEPFACE and doc_crop is not None and ver_crop is not None:
        try:
            # Run DeepFace verification
            res = DeepFace.verify(doc_crop, ver_crop, model_name="VGG-Face", enforce_detection=False)
            dist = res.get("distance", 0.5)
            similarity = float(max(0.0, min(1.0, 1.0 - dist)))
            engine_used = "DeepFace VGG-Face"
        except Exception:
            similarity = compute_histogram_similarity(doc_crop, ver_crop)
    else:
        similarity = compute_histogram_similarity(doc_crop, ver_crop)

    # Convert to percentage
    similarity_percent = round(similarity * 100.0, 1)
    
    # Check match threshold (default > 60.0%)
    is_match = similarity_percent >= (config.FACE_MATCH_THRESHOLD * 100.0)
    
    confidence = round(max(0.50, min(0.98, similarity + 0.20 if is_match else 0.85)), 2)

    msg = "Face verification successful. Identity matches passport photo." if is_match else "⚠ Identity mismatch detected. Verification face does not match passport photo."

    return {
        "face_detected": doc_face_found or ver_face_found,
        "document_face_detected": doc_face_found,
        "verification_face_detected": ver_face_found,
        "faces_detected_count": {
            "document": doc_face_count,
            "verification": ver_face_count
        },
        "similarity": similarity_percent,
        "similarity_decimal": round(similarity, 3),
        "match": is_match,
        "confidence": confidence,
        "engine_used": engine_used,
        "document_face_b64": doc_face_b64,
        "verification_face_b64": ver_face_b64,
        "message": msg
    }
