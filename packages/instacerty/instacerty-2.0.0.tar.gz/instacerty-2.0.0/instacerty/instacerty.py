from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from io import BytesIO
import qrcode
import tempfile
import os
from .utils import *


def generate_certificate(name,course,instructor,bg=None,is_badge=True,badge_img=None,is_signature=True,signature_img=None,save_path=None,certificate_number=None,issue_date=None):

    #Generate 12 Digit Certificate Number
    if certificate_number is None:
        certificate_number=get_certy_number()
    
    if save_path is None:
        save_path=get_save_directory()

    if save_path is not None:
        if not os.path.exists(save_path):
            os.makedirs(save_path)

    #Get current date
    if issue_date is None:
        current_date = get_current_date()
        issue_date=current_date

    # Generate QR code dynamically with certificate information
    qr_data = f"Certificate Number: {certificate_number}\nName: {name}\nCourse: {course}\nInstructor: {instructor}\nIssue Date: {issue_date}"
    qr_img = qrcode.make(qr_data)

    # Save the QR code to the certificate's qr_code field
    qr_io = BytesIO()  # Create an in-memory file object
    qr_img.save(qr_io, format='PNG')  # Save the QR code to the BytesIO object
    qr_io.seek(0)  # Move cursor to the beginning of the BytesIO object

    # Save QR code to a temporary file
    temp_qr_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    qr_img.save(temp_qr_file.name)

    ## Generate PDF certificate

    # Full path of where to save the PDF file
    pdf_file_name = f"{certificate_number}.pdf"
    file_path = os.path.join(save_path, pdf_file_name)

    pdf_buffer = BytesIO()
    p = canvas.Canvas(file_path,pagesize=landscape(A4))  # A4 Landscape
    width,height = landscape(A4)

    # background image
    if bg is None:
        watermark_path =get_local_image_path('bg.jpg')
        p.saveState()
        p.setFillAlpha(1)
        p.drawImage(watermark_path, 0, 0, width=width, height=height, mask='auto')
        p.restoreState()
    else:
        watermark_path = bg
        p.saveState()
        p.setFillAlpha(1)
        p.drawImage(watermark_path, 0, 0, width=width, height=height, mask='auto')
        p.restoreState()


    # Badge
    if is_badge and badge_img is None:
        badge_path = get_local_image_path('badge.png')
        p.drawImage(badge_path, width - 740, height - 500, width=120, height=120, mask='auto')  # position
    elif is_badge and badge_img is not None:
        badge_path = badge_img
        p.drawImage(badge_path, width - 740, height - 500, width=120, height=120, mask='auto')  # position


    # Signature
    if is_signature and signature_img is None:
        signature_path=get_local_image_path('signature.png')
        p.drawImage(signature_path, width // 2 - 50, 100, width=100, height=60,mask='auto') #position
    elif is_signature and signature_img is not None:
        signature_path=signature_img
        p.drawImage(signature_path, width // 2 - 50, 100, width=100, height=60,mask='auto') #position


    # Certificate Content
    p.setFont('Helvetica-Bold', 30)
    p.drawCentredString(width / 2.0, height - 150, "Certificate of Completion")
    p.setFont('Helvetica', 18)
    p.drawCentredString(width / 2.2, height - 200, f"This certifies that ")
    p.setFont('Helvetica-Bold', 20)  # Change to your desired font and size
    p.drawCentredString(width / 1.75, height - 200, f"{name}")
    p.setFont('Helvetica', 18)
    p.drawCentredString(width / 2.0, height - 250, f"has successfully completed the course {course}.")
    p.drawCentredString(width / 2.0, height - 300, f"Instructor: {instructor}")
    p.drawCentredString(width / 2.0, height - 350, f"Certificate Number: {certificate_number}")
    p.drawCentredString(width / 2.0, height - 400, f"Issue Date: {issue_date}")


    # Add QR code image to the PDF from the temporary file
    p.drawImage(temp_qr_file.name, 620, 110, width=120, height=120)

    # Finalize the PDF
    p.showPage()
    p.save()

    # Move to the beginning of the PDF buffer
    pdf_buffer.seek(0)

    # Remove temporary QR file (cleanup)
    temp_qr_file.close()

    # print(f'Certificate generated successfully!\nCertificate Number : {certificate_number}')

    return file_path
