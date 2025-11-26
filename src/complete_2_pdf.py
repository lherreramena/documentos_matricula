import json
import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

# Nombres de archivos. Asegúrate de que el PDF y el JSON estén en la misma carpeta.
PLANTILLA_PDF = "CONTRATO-MATRICULA-2025-La-Florida.pdf"
JSON_DATOS = "datos_contratos.json"
OUTPUT_DIR = "Contratos_PDF_Completados"

def crear_overlay(datos):
    """
    Crea un PDF overlay con los datos del contrato en memoria (BytesIO) usando reportlab.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # --- Configuración y Limpieza (Página 1) ---
    c.setFont("Helvetica", 10)

    # Coordenadas aproximadas para un PDF tamaño Carta.
    # Estas coordenadas (x, y) están ajustadas para la plantilla de La Florida.
    
    # 1. Fecha en la cabecera (Santiago a [día] de [mes] de 2025)
    c.drawString(88, 747, f"día {datos['firma']['fecha']['dia']} de {datos['firma']['fecha']['mes']}") 

    # 2. Cubrir campos vacíos (opcional, pero útil para limpiar posibles líneas)
    c.setFillColorRGB(1, 1, 1)  # Blanco
    c.rect(80, 665, 500, 70, fill=True, stroke=False) # Bloque apoderado (limpieza)
    c.rect(80, 595, 500, 60, fill=True, stroke=False) # Bloque alumnos (limpieza)

    # --- Escribir datos del Apoderado (Página 1) ---
    c.setFillColorRGB(0, 0, 0)  # Negro
    
    # Don(ña): / Calidad:
    c.drawString(88, 705, datos['apoderado']['nombre'])
    c.drawString(390, 690, datos['apoderado']['rut'])
    c.drawString(88, 690, datos['apoderado']['profesion'])
    c.drawString(88, 675, datos['apoderado']['calidad'])
    
    # Domicilio: Calle, N°, Casa, Depto, Comuna
    dom = datos['apoderado']['domicilio']
    # La información de domicilio se encuentra dispersa, ajustamos:
    c.drawString(140, 655, dom['calle'])
    c.drawString(370, 655, dom['numero']) 
    c.drawString(100, 640, dom['casa'])
    c.drawString(250, 640, dom['depto'])
    c.drawString(380, 640, dom['comuna'])

    # --- Escribir datos de los Alumnos (Página 1) ---
    y_alumnos = 578 # Punto de inicio para el primer alumno
    for i, alumno in enumerate(datos['alumnos']):
        if i >= 4: # Limitar a 4 alumnos según el espacio de la plantilla
            break
        
        # Nombre Completo
        c.drawString(88, y_alumnos, alumno['nombre'])
        
        # Curso (ajustado para que coincida con la columna derecha)
        c.drawString(380, y_alumnos, alumno['curso']) 
        
        y_alumnos -= 15

    # --- Escribir datos de Firma (Página 3) ---
    c.showPage() # Pasar a la página 2 (no se modifica), luego a la página 3.
    c.showPage() 
    
    # Se utiliza un rectángulo para limpiar el área del nombre y la fecha a rellenar
    c.setFillColorRGB(1, 1, 1) # Blanco
    c.rect(80, 70, 480, 60, fill=True, stroke=False)
    
    c.setFillColorRGB(0, 0, 0) # Negro
    
    # Nombre del Apoderado (bajo la firma)
    c.drawString(120, 120, datos['firma']['nombre'])
    
    # C.I. del Apoderado
    c.drawString(120, 105, datos['firma']['ci'])
    
    # Fecha de Firma (usando el formato del checkbox)
    fecha = datos['firma']['fecha']
    fecha_str = f"{fecha['dia']} de {fecha['mes']} de {fecha['año']}"
    c.drawString(140, 78, fecha_str)

    c.save()
    buffer.seek(0)
    return buffer

def fusionar_pdf(plantilla_path, overlay_buffer, output_final):
    """
    Fusiona la plantilla PDF con el overlay generado en memoria.
    """
    try:
        # 1. Leer la plantilla
        contract_src = './assets/docs'
        contract_template = os.path.join(contract_src, plantilla_path) + ".pdf"
        with open(contract_template, "rb") as f:
            reader = PdfReader(f)
            
        # 2. Leer el overlay
        overlay_reader = PdfReader(overlay_buffer)
        
        writer = PdfWriter()

        # 3. Fusionar página por página
        # La plantilla tiene 3 páginas. El overlay tiene una sola página (la que tiene contenido)
        # y se aplica a las páginas 1 y 3.
        
        # Página 1 (Datos de Apoderado y Alumnos)
        base_page_1 = reader.pages[0]
        overlay_page_1 = overlay_reader.pages[0]
        base_page_1.merge_page(overlay_page_1)
        writer.add_page(base_page_1)
        
        # Página 2 (Obligaciones, sin datos)
        writer.add_page(reader.pages[1])

        # Página 3 (Firmas y Fecha)
        base_page_3 = reader.pages[2]
        overlay_page_3 = overlay_reader.pages[1] # La segunda página del overlay (índice 1)
        base_page_3.merge_page(overlay_page_3)
        writer.add_page(base_page_3)


        # 4. Escribir el PDF final
        with open(output_final, "wb") as f:
            writer.write(f)
            
        return True
        
    except FileNotFoundError:
        print(f"\n❌ ERROR: No se encontró el archivo de plantilla: {plantilla_path}")
        print("Asegúrate de que el PDF 'CONTRATO-MATRICULA-2025-La-Florida.pdf' esté en la misma carpeta.")
        return False
    except Exception as e:
        print(f"\n❌ ERROR al fusionar PDFs: {e}")
        return False

def generar_contratos():
    """
    Función principal para cargar datos y generar el contrato.
    """
    try:
        data_src = './assets/json'
        json_data = os.path.join(data_src, JSON_DATOS)
        with open(json_data, "r", encoding="utf-8") as f:
#            contratos = json.load(f)["contratos"]
#        with open(JSON_DATOS, "r", encoding="utf-8") as f:
            data = json.load(f)
            contratos = data["contratos"]
            
    except FileNotFoundError:
        print(f"\n❌ ERROR: No se encontró el archivo de datos: {JSON_DATOS}")
        print("Crea el archivo 'datos_contratos.json' con el formato proporcionado.")
        return
    except json.JSONDecodeError:
        print(f"\n❌ ERROR: El archivo {JSON_DATOS} no es un JSON válido.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for contrac_name, datos_contrato in contratos.items():
        output_name = contrac_name + "_completado.pdf"
        output_file = os.path.join(OUTPUT_DIR, output_name)

        # 1. Crear el overlay en memoria
        overlay_buffer = crear_overlay(datos_contrato)
        
        # 2. Fusionar y guardar
        if fusionar_pdf(contrac_name, overlay_buffer, output_file):
            print(f"✅ Contrato PDF completado: {output_file}")
            
if __name__ == "__main__":
    generar_contratos()