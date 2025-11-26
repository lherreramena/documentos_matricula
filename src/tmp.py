
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import json
import os

PLANTILLA_PDF = "CONTRATO-MATRICULA-2025-La-Florida.pdf"
JSON_DATOS = "datos_contratos.json"

def crear_overlay(datos, output_overlay):
    c = canvas.Canvas(output_overlay, pagesize=letter)
    c.setFont("Helvetica", 10)

    # Cubrir campos vacíos con rectángulos blancos
    c.setFillColorRGB(1, 1, 1)  # Blanco
    c.rect(95, 695, 400, 60, fill=True, stroke=False)  # Bloque apoderado
    c.rect(95, 630, 400, 60, fill=True, stroke=False)  # Bloque alumnos
    c.rect(95, 60, 400, 40, fill=True, stroke=False)   # Bloque firma

    # Escribir datos
    c.setFillColorRGB(0, 0, 0)  # Negro
    c.drawString(100, 700, f"Don(ña): {datos['apoderado']['nombre']} en su calidad de: {datos['apoderado']['calidad']}")
    c.drawString(100, 685, f"Profesión: {datos['apoderado']['profesion']} RUT: {datos['apoderado']['rut']}")
    c.drawString(100, 670, f"Domicilio: {datos['apoderado']['domicilio']['calle']} N° {datos['apoderado']['domicilio']['numero']} "
                           f"Casa: {datos['apoderado']['domicilio']['casa']} Depto: {datos['apoderado']['domicilio']['depto']} "
                           f"Comuna: {datos['apoderado']['domicilio']['comuna']}")

    y = 640
    for alumno in datos['alumnos']:
        c.drawString(100, y, f"Nombre Completo: {alumno['nombre']}      Curso: {alumno['curso']}")
        y -= 15

    c.drawString(100, 80, f"Nombre: {datos['firma']['nombre']}  C.I.: {datos['firma']['ci']}  La Florida {datos['firma']['fecha']}")

    c.save()

def fusionar_pdf(plantilla, overlay, output_final):
    reader = PdfReader(plantilla)
    overlay_reader = PdfReader(overlay)
    writer = PdfWriter()

    for i in range(len(reader.pages)):
        base_page = reader.pages[i]
        if i < len(overlay_reader.pages):
            base_page.merge_page(overlay_reader.pages[i])
        writer.add_page(base_page)

    with open(output_final, "wb") as f:
        writer.write(f)

def generar_contratos():
    with open(JSON_DATOS, "r", encoding="utf-8") as f:
        contratos = json.load(f)["contratos"]

    os.makedirs("Contratos_PDF_Corregidos", exist_ok=True)

    for i, contrato in enumerate(contratos, start=1):
        overlay_file = f"overlay_{i}.pdf"
        output_file = os.path.join("Contratos_PDF_Corregidos", f"CONTRATO-MATRICULA-CORREGIDO-{i}.pdf")

        crear_overlay(contrato, overlay_file)
        fusionar_pdf(PLANTILLA_PDF, overlay_file, output_file)

        print(f"✅ Contrato PDF corregido: {output_file}")

if __name__ == "__main__":
    generar_contratos()
