from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import io
from reportlab.lib.colors import black


def add_border_to_pdf(input_pdf, output_pdf):
    # Marginlar (sm da)
    left_margin = 2.8 * cm
    right_margin = 0.8 * cm
    top_margin = 3mM * cm
    bottom_margin = 2 * cm

    # Ramka o‘lchamlari
    width = A4[0] - (left_margin + right_margin)
    height = A4[1] - (top_margin + bottom_margin)
    x = left_margin
    y = bottom_margin

    # Kiruvchi PDFni o‘qish
    try:
        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        # Har bir sahifa uchun
        for page_num in range(len(reader.pages)):
            # Yangi PDF sahifasi uchun reportlab canvassi
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)

            # Ramka chizish
            can.setLineWidth(0.5)  # Chiziq qalinligi 0.5 pt
            can.setStrokeColor(black)  # Qora rang
            can.rect(x, y, width, height)  # Ramka chizish

            # Canvassni saqlash
            can.save()
            packet.seek(0)

            # Yangi PDF sahifasini yaratish
            border_pdf = PdfReader(packet)
            border_page = border_pdf.pages[0]

            # Asl sahifani olish
            original_page = reader.pages[page_num]

            # Asl sahifa va ramkani birlashtirish
            original_page.merge_page(border_page)

            # Yangi sahifani yozuvchiga qo‘shish
            writer.add_page(original_page)

        # Yangi PDFni saqlash
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)
        print(f"Muvaffaqiyat: {output_pdf} fayli yaratildi.")

    except Exception as e:
        print(f"Xato: PDF ishlov berishda muammo: {e}")


if __name__ == "__main__":
    input_pdf = "namuna.docx.pdf"  # Kiruvchi PDF fayl nomini bu yerga kiriting
    output_pdf = "output_with_border.pdf"  # Chiquvchi PDF fayl nomi
    add_border_to_pdf(input_pdf, output_pdf)
