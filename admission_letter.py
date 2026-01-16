from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_admission_pdf(applicant):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(300, 750, "UNIVERSITY ADMISSION LETTER")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 680, f"Application ID: {applicant.id}")
    p.drawString(100, 660, f"Name: {applicant.name}")
    p.drawString(100, 640, f"Rank: {applicant.rank}")
    p.drawString(100, 620, f"Category: {applicant.category}")
    p.drawString(100, 600, f"Final Score: {applicant.final_score:.2f}")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 550, f"Allocated Department: {applicant.allocated_department}")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 500, "Congratulations! Your admission has been confirmed.")
    p.drawString(100, 480, "Please report to the university campus for further instructions.")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
