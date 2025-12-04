
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import json
import os
import logging

from utils import mm_a_pixeles


# Archivos
PLANTILLA_PDF = "CONTRATO-MATRICULA-2025-La-Florida.pdf"
JSON_DATOS = "datos_contratos.json"
COORDENADAS_DATOS = "datos_coordenadas.json"


def draw_string_for_dict(datos, coords, c_obj):
    if isinstance(datos, dict):
        for key in datos:
            if key in coords:
                draw_string_for_dict(datos=datos[key], coords=coords[key], c_obj=c_obj)
    elif isinstance(datos, list):
        for i, item in enumerate(datos):
            draw_string_for_dict(datos=item, coords=coords[i], c_obj=c_obj)
    else:
        x = coords[0]
        y = coords[1]
        c_obj.drawString(x, y, datos)

def crear_overlay_from_dict(datos, coords, output_overlay):
    """
    Crea un PDF overlay con los datos del contrato usando reportlab.
    """
    c = canvas.Canvas(output_overlay, pagesize=letter)

    # Coordenadas aproximadas (ajustar según el PDF)
    c.setFont("Helvetica-Bold", 10)

    for hoja in datos:
        #c.showPage()
        logging.debug(f"Hoja: {hoja}")
        datos_hoja = datos[hoja]
        coords_hoja = coords[hoja]
        for key in datos_hoja:
            draw_string_for_dict(datos=datos_hoja[key], coords=coords_hoja[key], c_obj=c)

    c.save()


def crear_overlay(datos, output_overlay):
    """
    Crea un PDF overlay con los datos del contrato usando reportlab.
    """
    c = canvas.Canvas(output_overlay, pagesize=letter)

    # Coordenadas aproximadas (ajustar según el PDF)
    c.setFont("Helvetica-Bold", 10)

    y_offset = mm_a_pixeles(0)
    logging.debug(f"y_offset= {y_offset}")

    # Coordenadas aproximadas para un PDF tamaño Carta.
    # Estas coordenadas (x, y) están ajustadas para la plantilla de La Florida.
    
    # 1. Fecha en la cabecera (Santiago a [día] de [mes] de 2025)
    #c.drawString(88, 747, f"{datos['firma']['fecha']['dia']} de {datos['firma']['fecha']['mes']}") 
    #for offset in range(0,100,10):
    #    c.drawString(118+offset, 650-offset, f"offset={offset}->{datos['firma']['fecha']['value']}")
    y_start_date = 630
    c.drawString(123, y_start_date, datos['firma']['fecha']['value'])

    # Don(ña): / Calidad:
    y_identity = y_start_date-58
    y_profesion = y_identity - 23
    x_profesion=162
    c.drawString(92, y_identity, datos['apoderado']['nombre'])
    c.drawString(298, y_identity, datos['apoderado']['calidad'])
    c.drawString(x_profesion, y_profesion, datos['apoderado']['profesion'])
    c.drawString(x_profesion+160, y_profesion, datos['apoderado']['rut'])
    
    # Domicilio: Calle, N°, Casa, Depto, Comuna
    dom = datos['apoderado']['domicilio']
    # La información de domicilio se encuentra dispersa, ajustamos:
    y_address = y_profesion - 23
    x_address = 48
    c.drawString(x_address, y_address, dom['calle'])
    c.drawString(x_address+141, y_address, dom['numero']) 
    c.drawString(x_address+207, y_address, dom['casa'])
    c.drawString(x_address+258, y_address, dom['depto'])
    c.drawString(x_address+322, y_address, dom['comuna'])

    y_alumno = y_profesion - 129
    x_alumno = 135
    for alumno in datos['alumnos']:
        c.drawString(x_alumno, y_alumno, alumno['nombre'])
        c.drawString(x_alumno+283, y_alumno, alumno['curso'])
        y_alumno -= 25

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
    json_coords = os.path.join(data_src, COORDENADAS_DATOS)
    
    with open(json_data, "r", encoding="utf-8") as f:
        contratos = json.load(f)["contratos"]

    with open(json_coords, "r", encoding="utf-8") as f:
        coords_dict = json.load(f)

    os.makedirs("Contratos_PDF_Completados", exist_ok=True)

    for contrac_name in contratos:
        output_name = contrac_name + "_completado.pdf"

        overlay_file = contrac_name + "_overlay.pdf"
        output_file = os.path.join("Contratos_PDF_Completados", output_name)

        #crear_overlay(contrato, overlay_file)
        crear_overlay_from_dict(contratos[contrac_name], coords_dict[contrac_name], overlay_file)
        fusionar_pdf(contrac_name, overlay_file, output_file)

        logging.info(f"✅ Contrato PDF completado: {output_file}")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    generar_contratos()
