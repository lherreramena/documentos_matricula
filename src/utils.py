# Convertimos mm a píxeles. Usaremos una resolución de 300 DPI (puntos por pulgada)
DPI = 300
MM_POR_PULGADA = 25.4

def mm_a_pixeles(mm):
    return int((mm / MM_POR_PULGADA) * DPI)
