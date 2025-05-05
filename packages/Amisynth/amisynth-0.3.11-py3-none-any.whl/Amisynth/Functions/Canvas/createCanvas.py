from PIL import Image
import Amisynth.utils as utils
from Amisynth.utils import canvas_storage
import xfox
import re

# Diccionario global donde guardaremos los canvas abiertos o creados

@xfox.addfunc(xfox.funcs)
async def createCanvas(canvas_id: str, width: int, height: int, color: str = "#000000", *args, **kwargs):
    """
    Crea un canvas con un ID, ancho y alto específicos y un color de fondo dado (HEX o RGB).
    Si no se proporciona color, el fondo será negro.
    """
    # Verifica si los parámetros obligatorios están presentes
    if not canvas_id:
        raise ValueError("El parámetro 'canvas_id' es obligatorio.")
    if not isinstance(width, int) or width <= 0:
        raise ValueError("El parámetro 'width' debe ser un entero positivo.")
    if not isinstance(height, int) or height <= 0:
        raise ValueError("El parámetro 'height' debe ser un entero positivo.")

    # Función para convertir HEX a RGB
    def hex_to_rgb(hex_color: str):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Validar el color
    if not isinstance(color, str):
        raise ValueError("El parámetro 'color' debe ser una cadena de texto.")
    
    # Si el color es en formato HEX, lo convertimos a RGB
    if re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
        color = hex_to_rgb(color)
    # Si el color es en formato RGB (tupla), aseguramos que esté en el formato correcto
    elif isinstance(color, str) and color.startswith('rgb(') and color.endswith(')'):
        try:
            color = tuple(map(int, color[4:-1].split(',')))
            if len(color) != 3 or not all(0 <= c <= 255 for c in color):
                raise ValueError("El valor de 'color' en formato RGB debe tener tres valores entre 0 y 255.")
        except ValueError:
            raise ValueError("El valor de 'color' en formato RGB no es válido.")

    # Crea un canvas con el color de fondo especificado
    canvas_storage[canvas_id] = Image.new("RGBA", (width, height), color)
    print(f"[DEBUG CREATECANVAS] Canvas creado con color: {color}")
    return ""
