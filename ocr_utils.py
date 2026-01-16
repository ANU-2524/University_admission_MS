import pytesseract
from PIL import Image
import re
import os

# Try to find tesseract binary
# On Windows, it's often in C:\Program Files\Tesseract-OCR\tesseract.exe
# On Linux/Mac, it's usually in /usr/bin/tesseract
tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

def extract_marks_from_image(image_path):
    """
    Attempts to extract marks from an image using OCR.
    This is a simplified version for demonstration.
    """
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        # Look for patterns like "Total Marks: 95" or "Percentage: 95.5"
        marks_match = re.search(r'(?:Marks|Total|Percentage|Score)\D*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if marks_match:
            return float(marks_match.group(1))
        return None
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def verify_applicant_marks(applicant):
    """
    Verifies if the marks entered by the applicant match the document.
    """
    if not applicant.marksheet_path or not os.path.exists(applicant.marksheet_path):
        return False, "Marksheet not found"
    
    extracted_marks = extract_marks_from_image(applicant.marksheet_path)
    if extracted_marks is None:
        return False, "Could not read marks from document"
    
    # Allow a small margin of error or exact match
    if abs(extracted_marks - applicant.marks_12) < 1.0:
        return True, "Marks verified successfully"
    else:
        return False, f"Marks mismatch: Form says {applicant.marks_12}, Document says {extracted_marks}"
