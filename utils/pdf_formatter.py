#pdf formation logic
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame, Spacer
from io import BytesIO
from reportlab.lib.enums import TA_LEFT, TA_CENTER

PAGE_SIZE = A4

def create_resume_pdf_bytes(resume_struct):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=PAGE_SIZE)
    width, height = PAGE_SIZE

    # Margins
    left_margin = 20 * mm
    right_margin = 20 * mm
    top_margin = height - 20 * mm
    x = left_margin
    y = top_margin

    # Header: name and title
    name = resume_struct.get("name","")
    title = resume_struct.get("title","")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, name)
    c.setFont("Helvetica", 11)
    c.drawString(x, y - 18, title)
    y -= 36

    # Summary
    if resume_struct.get("summary"):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "Summary")
        y -= 14
        c.setFont("Helvetica", 10)
        text = c.beginText(x, y)
        for line in _wrap_text(resume_struct["summary"], 90):
            text.textLine(line)
            y -= 12
        c.drawText(text)
        y -= 8

    # Experience
    if resume_struct.get("experience"):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "Experience")
        y -= 14
        c.setFont("Helvetica", 10)
        for ex in resume_struct["experience"]:
            role_line = f"{ex.get('role','')} — {ex.get('company','')} ({ex.get('duration','')})"
            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y, role_line)
            y -= 12
            c.setFont("Helvetica", 9)
            for line in _wrap_text(ex.get("description",""), 100):
                c.drawString(x + 6, y, line)
                y -= 10
            y -= 6
            if y < 80*mm:
                c.showPage()
                y = top_margin

    # Education
    if resume_struct.get("education"):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "Education")
        y -= 14
        c.setFont("Helvetica", 10)
        for ed in resume_struct["education"]:
            ed_line = f"{ed.get('degree','')} — {ed.get('institution','')} ({ed.get('years','')})"
            for line in _wrap_text(ed_line, 100):
                c.drawString(x, y, line)
                y -= 10
            y -= 6
            if y < 60*mm:
                c.showPage()
                y = top_margin

    # Skills
    if resume_struct.get("skills"):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "Skills")
        y -= 14
        c.setFont("Helvetica", 10)
        skills_line = ", ".join(resume_struct.get("skills",[]))
        for line in _wrap_text(skills_line, 120):
            c.drawString(x, y, line)
            y -= 10

    # Achievements
    if resume_struct.get("achievements"):
        y -= 8
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "Achievements")
        y -= 14
        c.setFont("Helvetica", 10)
        for a in resume_struct.get("achievements"):
            for line in _wrap_text(f"- {a}", 100):
                c.drawString(x, y, line)
                y -= 10
            y -= 4
            if y < 30*mm:
                c.showPage()
                y = top_margin

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def create_cover_letter_pdf_bytes(full_name, cover_text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=PAGE_SIZE)
    width, height = PAGE_SIZE
    left_margin = 20 * mm
    top_margin = height - 20 * mm
    x = left_margin
    y = top_margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, full_name)
    y -= 24
    c.setFont("Helvetica", 10)

    for line in _wrap_text(cover_text, 100):
        c.drawString(x, y, line)
        y -= 12
        if y < 30*mm:
            c.showPage()
            y = top_margin

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def _wrap_text(text, max_chars):
    # naive wrap
    words = text.split()
    lines = []
    current = []
    length = 0
    for w in words:
        if length + len(w) + 1 <= max_chars:
            current.append(w)
            length += len(w) + 1
        else:
            lines.append(" ".join(current))
            current = [w]
            length = len(w) + 1
    if current:
        lines.append(" ".join(current))
    # If empty, return at least empty string
    return lines or [""]
