
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import json
import os

# Archivos
PLANTILLA_PDF = "CONTRATO-MATRICULA-2025-La-Florida.pdf"
JSON_DATOS = "datos_contratos.json"

def crear_overlay(datos, output_overlay):
    """
    Crea un PDF overlay con los datos del contrato usando reportlab.
    """
    c = canvas.Canvas(output_overlay, pagesize=letter)

    # Coordenadas aproximadas (ajustar según el PDF)
    c.setFont("Helvetica", 10)

    # Datos del apoderado
    c.drawString(100, 700, f"Don(ña): {datos['apoderado']['nombre']} en su calidad de: {datos['apoderado']['calidad']}")
    c.drawString(100, 685, f"Profesión: {datos['apoderado']['profesion']} RUT: {datos['apoderado']['rut']}")
    c.drawString(100, 670, f"Domicilio: {datos['apoderado']['domicilio']['calle']} N° {datos['apoderado']['domicilio']['numero']} "
                           f"Casa: {datos['apoderado']['domicilio']['casa']} Depto: {datos['apoderado']['domicilio']['depto']} "
                           f"Comuna: {datos['apoderado']['domicilio']['comuna']}")

    # Alumnos
    y = 640
    for alumno in datos['alumnos']:
        c.drawString(100, y, f"Nombre Completo: {alumno['nombre']}      Curso: {alumno['curso']}")
        y -= 15

    # Firma
    c.drawString(100, 100, f"Nombre: {datos['firma']['nombre']}")
    c.drawString(100, 85, f"C.I.: {datos['firma']['ci']}")
    c.drawString(100, 70, f"La Florida {datos['firma']['fecha']}")

    c.save()

def fusionar_pdf(plantilla, overlay, output_final):
    """
    Fusiona el PDF original con el overlay.
    """
    contract_src = './assets/docs'
    contract_template = os.path.join(contract_src, plantilla) + ".pdf"

    reader = PdfReader(contract_template)
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
    data_src = './assets/json'
    json_data = os.path.join(data_src, JSON_DATOS)
    with open(json_data, "r", encoding="utf-8") as f:
    #with open(JSON_DATOS, "r", encoding="utf-8") as f:
        contratos = json.load(f)["contratos"]

    os.makedirs("Contratos_PDF_Completados", exist_ok=True)

    for contrac_name in contratos:
        #doc_completado = completar_contrato(contratos[contrac_name], contrac_name)
        output_name = contrac_name + "_completado.pdf"
        #output_file = os.path.join("Contratos_Completados", f"CONTRATO-MATRICULA-COMPLETADO-{i}.docx")
        output_file = os.path.join("Contratos_Completados", output_name)

    #for i, contrato in enumerate(contratos, start=1):
        overlay_file = contrac_name + "overlay.pdf"
        #output_file = os.path.join("Contratos_PDF_Completados", f"CONTRATO-MATRICULA-COMPLETADO-{i}.pdf")
        output_file = os.path.join("Contratos_PDF_Completados", output_name)

        #crear_overlay(contrato, overlay_file)
        crear_overlay(contratos[contrac_name], overlay_file)
        fusionar_pdf(contrac_name, overlay_file, output_file)

        print(f"✅ Contrato PDF completado: {output_file}")

if __name__ == "__main__":
    generar_contratos()
