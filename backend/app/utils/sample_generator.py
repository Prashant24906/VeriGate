import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.config import SAMPLE_DOCS_DIR


def generate_face_avatar(name_seed: str, color_bg: tuple = (180, 200, 220)) -> np.ndarray:
    """Generate a clean synthetic face avatar image for testing."""
    img = Image.new("RGB", (250, 300), color=color_bg)
    draw = ImageDraw.Draw(img)
    
    # Draw head / silhouette
    draw.ellipse([65, 40, 185, 180], fill=(240, 210, 185), outline=(100, 80, 70), width=2)
    # Hair
    draw.ellipse([60, 25, 190, 100], fill=(50, 40, 35))
    # Eyes
    draw.ellipse([95, 95, 115, 115], fill=(255, 255, 255))
    draw.ellipse([102, 102, 110, 110], fill=(30, 30, 80))
    draw.ellipse([135, 95, 155, 115], fill=(255, 255, 255))
    draw.ellipse([140, 102, 148, 110], fill=(30, 30, 80))
    # Nose
    draw.line([125, 110, 120, 135, 130, 135], fill=(180, 140, 120), width=2)
    # Mouth
    draw.arc([105, 145, 145, 165], start=0, end=180, fill=(180, 60, 60), width=3)
    # Shirt / Shoulders
    draw.ellipse([25, 180, 225, 360], fill=(40, 80, 140))

    # Add text label at bottom
    draw.text((10, 275), f"SEED: {name_seed}", fill=(255, 255, 255))

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def generate_passport_image(
    name: str,
    passport_number: str,
    nationality: str,
    dob: str,
    gender: str,
    expiry: str,
    face_img: np.ndarray,
    tamper: bool = False
) -> np.ndarray:
    """
    Generate synthetic passport document image with MRZ zone and passport layout.
    """
    canvas = Image.new("RGB", (800, 520), color=(248, 245, 235))
    draw = ImageDraw.Draw(canvas)

    # Passport Header
    draw.rectangle([0, 0, 800, 70], fill=(20, 45, 85))
    draw.text((30, 20), f"REPUBLIC OF {nationality} — PASSPORT", fill=(255, 215, 0))

    # Sub header lines
    draw.line([0, 72, 800, 72], fill=(200, 170, 0), width=3)

    # Insert Face Photo
    face_pil = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)).resize((180, 220))
    canvas.paste(face_pil, (40, 100))
    draw.rectangle([40, 100, 220, 320], outline=(20, 45, 85), width=2)

    # Details Section
    x_lbl, x_val = 250, 420
    y_start = 95
    line_h = 35

    fields = [
        ("Type / Code", f"P / {nationality}"),
        ("Passport No.", passport_number),
        ("Surname & Given Name", name),
        ("Nationality", nationality),
        ("Date of Birth", dob),
        ("Sex", gender),
        ("Date of Expiry", expiry),
    ]

    for i, (label, val) in enumerate(fields):
        y = y_start + i * line_h
        draw.text((x_lbl, y), label.upper(), fill=(120, 120, 120))
        draw.text((x_val, y), str(val), fill=(10, 10, 10))

    # Draw Security Microprint lines background
    for y in range(350, 390, 8):
        draw.line([30, y, 770, y], fill=(230, 220, 200), width=1)

    # Draw 2-Line TD3 MRZ Zone at bottom
    draw.rectangle([0, 395, 800, 520], fill=(255, 255, 255))
    draw.line([0, 395, 800, 395], fill=(0, 0, 0), width=2)

    # Format MRZ lines
    # Line 1: P<INDNAME<<GIVEN<<<<<<<<<<<<<<<<<<<<<<<<<<
    name_mrz = name.replace(" ", "<<").upper()
    line1_body = f"P<{nationality}{name_mrz}"
    line1 = line1_body.ljust(44, '<')[:44]

    # Format DOB and Expiry into YYMMDD
    def to_yymmdd(d_str: str) -> str:
        parts = d_str.split('/')
        if len(parts) == 3:
            return parts[2][-2:] + parts[1] + parts[0]
        return "990815"

    dob_yymmdd = to_yymmdd(dob)
    exp_yymmdd = to_yymmdd(expiry)

    # Line 2: PASSPORT#<CHECK_DOB<CHECK_EXPIRY<CHECK_COMPOSITE
    line2_body = f"{passport_number}<0{nationality}{dob_yymmdd}0{gender}{exp_yymmdd}0<<<<<<<<<<<<<<"
    line2 = line2_body.ljust(44, '<')[:44]

    # Draw MRZ OCR-B styled text
    draw.text((40, 415), line1, fill=(0, 0, 0))
    draw.text((40, 455), line2, fill=(0, 0, 0))

    cv2_img = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)

    # Add artificial tampering overlay if requested
    if tamper:
        # Spliced text box over Passport Number
        cv2.rectangle(cv2_img, (415, 125), (580, 160), (240, 240, 240), -1)
        cv2.putText(cv2_img, "FORGED999", (420, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        # Add noise patch
        noise = np.random.randint(0, 150, (50, 120, 3), dtype=np.uint8)
        cv2_img[200:250, 450:570] = cv2.addWeighted(cv2_img[200:250, 450:570], 0.4, noise, 0.6, 0)

    return cv2_img


def generate_all_sample_cases():
    """Generate all 4 synthetic sample test cases."""
    SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Case 1: Genuine Passport
    face1 = generate_face_avatar("JOHN_DOE", (180, 210, 240))
    pass1 = generate_passport_image("JOHN DOE", "A1234567", "IND", "15/08/1999", "M", "15/08/2030", face1, tamper=False)
    cv2.imwrite(str(SAMPLE_DOCS_DIR / "case1_genuine_passport.png"), pass1)
    cv2.imwrite(str(SAMPLE_DOCS_DIR / "case1_genuine_face.png"), face1)

    # Case 2: Expired Passport
    face2 = generate_face_avatar("ALICE_SMITH", (220, 200, 220))
    pass2 = generate_passport_image("ALICE SMITH", "Z1122334", "IND", "10/10/1985", "F", "01/01/2020", face2, tamper=False)
    cv2.imwrite(str(SAMPLE_DOCS_DIR / "case2_expired_passport.png"), pass2)
    cv2.imwrite(str(SAMPLE_DOCS_DIR / "case2_expired_face.png"), face2)

    # Case 3: Tampered Passport
    face3 = generate_face_avatar("TAMPERED_DOC", (210, 230, 210))
    pass3 = generate_passport_image("JOHN DOE", "FORGED999", "IND", "15/08/1999", "M", "15/08/2030", face3, tamper=True)
    cv2.imwrite(str(SAMPLE_DOCS_DIR / "case3_tampered_passport.png"), pass3)
    cv2.imwrite(str(SAMPLE_DOCS_DIR / "case3_tampered_face.png"), face3)

    # Case 4: Wrong Person / Mismatched Face
    face4_doc = generate_face_avatar("IMPOSTOR_DOC", (240, 220, 180))
    face4_live = generate_face_avatar("IMPOSTOR_LIVE", (150, 150, 150))
    pass4 = generate_passport_image("BOB MARLEY", "M9988776", "IND", "20/05/1992", "M", "20/05/2032", face4_doc, tamper=False)
    cv2.imwrite(str(SAMPLE_DOCS_DIR / "case4_wrongperson_passport.png"), pass4)
    cv2.imwrite(str(SAMPLE_DOCS_DIR / "case4_wrongperson_face.png"), face4_live)


if __name__ == "__main__":
    generate_all_sample_cases()
    print("Synthetic sample test cases generated successfully.")
