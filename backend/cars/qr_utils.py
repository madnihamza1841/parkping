import io
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from django.conf import settings


def generate_qr_image(car) -> bytes:
    _, web_url = car.get_deep_link()
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(web_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def generate_qr_pdf(car) -> bytes:
    _, web_url = car.get_deep_link()
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(web_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    # Save QR to temp buffer
    img_buf = io.BytesIO()
    img.save(img_buf, format='PNG')
    img_buf.seek(0)

    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=A4)
    width, height = A4

    qr_size = 10 * cm
    x = (width - qr_size) / 2
    y = (height - qr_size) / 2 + 2 * cm

    from reportlab.lib.utils import ImageReader
    c.drawImage(ImageReader(img_buf), x, y, width=qr_size, height=qr_size)

    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(width / 2, y - 1 * cm, car.nickname)

    c.setFont('Helvetica', 14)
    c.drawCentredString(width / 2, y - 1.8 * cm, car.plate_number)

    c.showPage()
    c.save()
    return pdf_buf.getvalue()
