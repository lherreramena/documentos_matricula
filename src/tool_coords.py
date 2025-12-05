import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from PyPDF2 import PdfReader, PdfWriter
import json


# Configuración
# Coloca aquí los nombres de los archivos PDF que necesitas medir
# Asumimos que están en la carpeta './assets/docs' como en tu script original
DOCUMENTOS_A_MEDIR = [
    "COMPROBANTE-CHEQUES-2025",
    "COMPROBANTE-DE-MATRICULA-2025",
    "FICHA-DE-MATRICULA-2025-La-Florida-1",
    "Ficha-de-Salud-2026",
    "Sobre-el-Centro-General-de-Padres-y-Apoderados-2026-La-Florida"
]

PATH_DOCS = './assets/docs'
OUTPUT_DIR = './pdf_con_grillas'
JSON_DATOS = "datos_contratos.json"
COORDENADAS_DATOS = "datos_coordenadas.json"

def crear_pdf_grilla(output_filename):
    """Crea un PDF transparente con una grilla de coordenadas X,Y."""
    c = canvas.Canvas(output_filename, pagesize=letter)
    width, height = letter # 612.0, 792.0 puntos aprox
    
    c.setFont("Helvetica", 5)
    c.setStrokeColor(colors.red)
    c.setFillColor(colors.red)
    
    # Dibujar líneas verticales (Eje X)
    # Saltos de 20 puntos para precisión, líneas fuertes cada 100
    for x in range(0, int(width) + 1, 10):
        if x % 100 == 0:
            c.setLineWidth(1)
            c.setStrokeAlpha(0.6)
        elif x % 50 == 0:
            c.setLineWidth(0.5)
            c.setStrokeAlpha(0.4)
        else:
            c.setLineWidth(0.1)
            c.setStrokeAlpha(0.2)
            
        c.line(x, 0, x, height)
        # Etiqueta numérica
        if x % 50 == 0:
            c.drawString(x + 2, 10, str(x))
            c.drawString(x + 2, height - 20, str(x))

    # Dibujar líneas horizontales (Eje Y)
    for y in range(0, int(height) + 1, 10):
        if y % 100 == 0:
            c.setLineWidth(1)
            c.setStrokeAlpha(0.6)
        elif y % 50 == 0:
            c.setLineWidth(0.5)
            c.setStrokeAlpha(0.4)
        else:
            c.setLineWidth(0.1)
            c.setStrokeAlpha(0.2)
            
        c.line(0, y, width, y)
        # Etiqueta numérica
        if y % 50 == 0:
            c.drawString(10, y + 2, str(y))
            c.drawString(width - 20, y + 2, str(y))
            
    c.save()

def superponer_grilla():
    data_src = './assets/json'
    json_data = os.path.join(data_src, JSON_DATOS)
    json_coords = os.path.join(data_src, COORDENADAS_DATOS)

    with open(json_data, "r", encoding="utf-8") as f:
        contratos = json.load(f)["contratos"]

    with open(json_coords, "r", encoding="utf-8") as f:
        coords_dict = json.load(f)["coordenadas"]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Crear el overlay de la grilla una sola vez
    grid_pdf_name = "temp_grid_overlay.pdf"
    crear_pdf_grilla(grid_pdf_name)
    
    reader_grid = PdfReader(grid_pdf_name)
    page_grid = reader_grid.pages[0]

    for contrac_name in contratos:
        output_name = contrac_name + "_completado.pdf"

        overlay_file = contrac_name + "_overlay.pdf"
        output_file = os.path.join(OUTPUT_DIR, output_name)

        input_path = os.path.join(PATH_DOCS, contrac_name + ".pdf")
        output_path = os.path.join(OUTPUT_DIR, contrac_name + "_GRILLA.pdf")

        if not os.path.exists(input_path):
            print(f"⚠️ Archivo no encontrado: {input_path}")
            continue

        reader_source = PdfReader(input_path)
        writer = PdfWriter()

        # Fusionar cada página del documento con la grilla
        for page in reader_source.pages:
            page.merge_page(page_grid)
            writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)
            
        print(f"✅ Grilla generada para: {output_path}")

    # Limpieza
    if os.path.exists(grid_pdf_name):
        os.remove(grid_pdf_name)



if __name__ == "__main__":
    superponer_grilla()
