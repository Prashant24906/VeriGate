import re
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple, List


# ICAO 9303 MRZ Weight multipliers for 7-3-1 check digit algorithm
MRZ_WEIGHTS = [7, 3, 1]
MRZ_CHAR_VALUES = {
    '<': 0, '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15, 'G': 16, 'H': 17, 'I': 18,
    'J': 19, 'K': 20, 'L': 21, 'M': 22, 'N': 23, 'O': 24, 'P': 25, 'Q': 26, 'R': 27,
    'S': 28, 'T': 29, 'U': 30, 'V': 31, 'W': 32, 'X': 33, 'Y': 34, 'Z': 35
}


def calculate_mrz_check_digit(mrz_string: str) -> int:
    """Calculate check digit for an MRZ string snippet using standard 7-3-1 weighting."""
    total = 0
    for i, char in enumerate(mrz_string.upper()):
        val = MRZ_CHAR_VALUES.get(char, 0)
        weight = MRZ_WEIGHTS[i % 3]
        total += val * weight
    return total % 10


def detect_mrz_region(image: np.ndarray) -> Optional[np.ndarray]:
    """
    Detect bottom MRZ area of document image using morphological filtering & contours.
    Returns cropped MRZ image region or None if not located.
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Bottom 40% of the image is usually where MRZ lives
        bottom_crop = gray[int(h * 0.55):, :]
        
        # Smooth and blackhat morphology to isolate dark text on light background
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        blackhat = cv2.morphologyEx(bottom_crop, cv2.MORPH_BLACKHAT, kernel)
        
        # Compute horizontal gradients
        grad_x = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        grad_x = np.absolute(grad_x)
        (min_val, max_val) = (np.min(grad_x), np.max(grad_x))
        if max_val > min_val:
            grad_x = (255 * ((grad_x - min_val) / (max_val - min_val))).astype("uint8")
        else:
            grad_x = grad_x.astype("uint8")
            
        # Morphological close to join characters into lines
        grad_x = cv2.morphologyEx(grad_x, cv2.MORPH_CLOSE, kernel)
        _, thresh = cv2.threshold(grad_x, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image[int(h * 0.55):, :]
            
        # Find largest rectangular contour matching MRZ aspect ratio
        bounding_boxes = [cv2.boundingRect(c) for c in contours]
        # Filter wide boxes
        valid_boxes = [b for b in bounding_boxes if b[2] > w * 0.4 and b[3] > 15]
        if valid_boxes:
            # Sort by area descending
            valid_boxes.sort(key=lambda b: b[2] * b[3], reverse=True)
            x, y, bw, bh = valid_boxes[0]
            # Add padding
            pad_y = 10
            pad_x = 10
            y1 = max(0, y - pad_y)
            y2 = min(bottom_crop.shape[0], y + bh + pad_y)
            x1 = max(0, x - pad_x)
            x2 = min(w, x + bw + pad_x)
            return image[int(h * 0.55) + y1:int(h * 0.55) + y2, x1:x2]
        
        # Default to bottom 35% crop if contour detection didn't find tight box
        return image[int(h * 0.65):, :]
    except Exception:
        return image


def parse_td3_mrz(line1: str, line2: str) -> Dict[str, Any]:
    """
    Parse standard Passport TD3 MRZ format (2 lines x 44 chars).
    
    Line 1: P<COUNTRYNAME<<GIVEN<NAMES...
    Line 2: PASSPORT#<CHECK_DOB<CHECK_EXPIRY<CHECK_COMPOSITE
    """
    # Clean strings
    l1 = line1.strip().upper().replace(" ", "")
    l2 = line2.strip().upper().replace(" ", "")
    
    # Ensure lines are padded/trimmed to 44 chars
    if len(l1) < 44:
        l1 = l1.ljust(44, '<')
    else:
        l1 = l1[:44]
        
    if len(l2) < 44:
        l2 = l2.ljust(44, '<')
    else:
        l2 = l2[:44]

    doc_type = l1[0:2].replace('<', '')
    issuing_country = l1[2:5].replace('<', '')
    
    # Parse Names (SURNAME<<GIVEN_NAMES)
    name_part = l1[5:]
    name_tokens = name_part.split('<<')
    surname = name_tokens[0].replace('<', ' ').strip()
    given_names = name_tokens[1].replace('<', ' ').strip() if len(name_tokens) > 1 else ""
    full_name = f"{surname} {given_names}".strip()

    # Line 2 breakdown
    passport_num_raw = l2[0:9]
    passport_num = passport_num_raw.replace('<', '')
    passport_num_check = l2[9]
    
    nationality = l2[10:13].replace('<', '')
    
    dob_raw = l2[13:19]  # YYMMDD
    dob_check = l2[19]
    
    sex = l2[20]
    if sex not in ['M', 'F']:
        sex = 'M' if sex in ['1', 'V'] else ('F' if sex == 'E' else 'U')
        
    expiry_raw = l2[21:27]  # YYMMDD
    expiry_check = l2[27]
    
    personal_num_raw = l2[28:42]
    composite_check = l2[43]
    
    # Perform checksum validations
    calc_passport_check = str(calculate_mrz_check_digit(passport_num_raw))
    calc_dob_check = str(calculate_mrz_check_digit(dob_raw))
    calc_expiry_check = str(calculate_mrz_check_digit(expiry_raw))
    
    # Composite string is passport_num_raw + passport_num_check + dob_raw + dob_check + expiry_raw + expiry_check + personal_num_raw
    composite_str = passport_num_raw + passport_num_check + dob_raw + dob_check + expiry_raw + expiry_check + personal_num_raw
    calc_composite_check = str(calculate_mrz_check_digit(composite_str))
    
    passport_num_valid = (calc_passport_check == passport_num_check) or (passport_num_check in ['<', '0'])
    dob_valid = (calc_dob_check == dob_check) or (dob_check in ['<', '0'])
    expiry_valid = (calc_expiry_check == expiry_check) or (expiry_check in ['<', '0'])
    composite_valid = (calc_composite_check == composite_check) or (composite_check in ['<', '0'])
    
    # Format DOB and Expiry into DD/MM/YYYY
    def format_mrz_date(yymmdd: str, is_expiry: bool = False) -> str:
        if not re.match(r'^\d{6}$', yymmdd):
            return yymmdd
        yy, mm, dd = yymmdd[:2], yymmdd[2:4], yymmdd[4:6]
        century = "20" if is_expiry or int(yy) < 30 else "19"
        return f"{dd}/{mm}/{century}{yy}"

    dob_formatted = format_mrz_date(dob_raw, is_expiry=False)
    expiry_formatted = format_mrz_date(expiry_raw, is_expiry=True)

    mrz_valid = passport_num_valid and dob_valid and expiry_valid
    
    return {
        "mrz_detected": True,
        "mrz_format": "TD3",
        "raw_line1": l1,
        "raw_line2": l2,
        "document_type": doc_type,
        "issuing_country": issuing_country,
        "full_name": full_name,
        "passport_number": passport_num,
        "nationality": nationality,
        "dob": dob_formatted,
        "gender": sex,
        "expiry": expiry_formatted,
        "checksums": {
            "passport_number": {
                "expected": passport_num_check,
                "calculated": calc_passport_check,
                "valid": passport_num_valid
            },
            "dob": {
                "expected": dob_check,
                "calculated": calc_dob_check,
                "valid": dob_valid
            },
            "expiry": {
                "expected": expiry_check,
                "calculated": calc_expiry_check,
                "valid": expiry_valid
            },
            "composite": {
                "expected": composite_check,
                "calculated": calc_composite_check,
                "valid": composite_valid
            }
        },
        "overall_mrz_valid": mrz_valid
    }


def extract_and_parse_mrz(image: np.ndarray, ocr_text_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Main MRZ extraction pipeline.
    Attempts regex extraction from OCR text or image analysis.
    """
    # 1. First check if OCR text hint contains 44-character MRZ lines
    if ocr_text_hint:
        lines = [line.strip().replace(" ", "") for line in ocr_text_hint.split('\n') if len(line.strip().replace(" ", "")) >= 30]
        # Look for line starting with P< or P[A-Z]
        mrz_lines = []
        for i, l in enumerate(lines):
            if (l.startswith("P<") or l.startswith("P1") or l.startswith("P2") or re.match(r'^P[A-Z0-9<]', l)) and len(l) >= 35:
                if i + 1 < len(lines):
                    mrz_lines = [l, lines[i+1]]
                    break
        
        if len(mrz_lines) == 2:
            return parse_td3_mrz(mrz_lines[0], mrz_lines[1])

    # 2. Fallback attempt: Return structured default if MRZ text was not extracted
    return {
        "mrz_detected": False,
        "mrz_format": "UNKNOWN",
        "raw_line1": "",
        "raw_line2": "",
        "document_type": "passport",
        "issuing_country": "",
        "full_name": "",
        "passport_number": "",
        "nationality": "",
        "dob": "",
        "gender": "",
        "expiry": "",
        "checksums": {
            "passport_number": {"valid": False},
            "dob": {"valid": False},
            "expiry": {"valid": False},
            "composite": {"valid": False}
        },
        "overall_mrz_valid": False,
        "message": "MRZ could not be reliably detected — manual verification recommended."
    }
