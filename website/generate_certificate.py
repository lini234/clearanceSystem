from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def generate_certificate(surname, otherNames, matricNumber, college, department, staff_name, department_name, clearance_status, clearance_date, clearance_requests, certificate_path):
    c = canvas.Canvas(certificate_path, pagesize=letter)
    width, height = letter

    # Draw the header and other parts as before...
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 50, "CRAWFORD UNIVERSITY")

    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2.0, height - 70, "FAITH CITY, IGBESA")
    c.drawCentredString(width / 2.0, height - 85, "OGUN STATE")

    # Leave a spacing for the next item
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2.0, height - 110, "OFFICE OF THE DEAN STUDENT AFFAIRS")

    c.setFont("Helvetica-Bold", 14)
    title = "FINAL YEAR STUDENTS CLEARANCE FORM FOR 2022/2023 SESSION"
    c.drawCentredString(width / 2.0, height - 130, title)
    # Underline the title
    title_width = c.stringWidth(title, "Helvetica-Bold", 14)
    c.line((width - title_width) / 2, height - 132, (width + title_width) / 2, height - 132)

    # Draw a box for the passport below the title
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(width - 150, height - 260, 100, 120)
    c.setFont("Helvetica", 10)
    c.drawString(width - 140, height - 270, "Affix passport")

    # Student information fields
    fields = [
        f"Name: {surname} {otherNames}",
        f"Matric Number: {matricNumber}",
        f"College: {college}",
        f"Department: {department}",
        "Hall of Residence:",
        "Room Number:",
        "Phone Number:",
        "Parents Phone No:",
        "E-mail:"
    ]

    y_position = height - 150
    for field in fields:
        c.drawString(50, y_position, field)
        y_position -= 20

    # Clearance table
    clearance_data = [
        ["S/N", "Department", "Officer's Name", "Status", "Date"]
    ]
    for idx, request in enumerate(clearance_requests, start=1):
        clearance_data.append([
            str(idx),
            request.department.title,
            request.department.staff.surname + " " + request.department.staff.otherNames,
            request.status,
            request.clearance_date.strftime('%Y-%m-%d') if request.clearance_date else ""
        ])

    clearance_table = Table(clearance_data, colWidths=[30, 180, 130, 80, 80])
    clearance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    clearance_table.wrapOn(c, width, height)
    clearance_table.drawOn(c, 50, y_position - 170)

    # Clearance statement
    c.drawString(50, y_position - 310,
                 "This is to certify that the above named final year student has fulfilled all the necessary")
    c.drawString(50, y_position - 325, "obligations to the University and hence, been duly cleared.")

    # Registrar's signature and date
    c.drawString(50, y_position - 360, "Registrar (Stamp & Sign): _______________________")
    c.drawString(350, y_position - 360, "Date: ___________")

    # Save the PDF
    c.save()
