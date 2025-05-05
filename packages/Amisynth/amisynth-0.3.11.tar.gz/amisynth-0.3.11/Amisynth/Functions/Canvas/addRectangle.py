import xfox
from PIL import ImageDraw
from Amisynth.utils import canvas_storage

@xfox.addfunc(xfox.funcs)
async def addRectangleCanvas(canvas_id: str, x: int, y: int, ancho: int, alto: int, color: str = "#FFFFFF", *args, **kwargs):
    """
    Dibuja un rectángulo relleno en el canvas especificado.

    Parámetros:
        canvas_id (str): ID del canvas donde se dibujará.
        x (int): Coordenada X inicial (esquina superior izquierda).
        y (int): Coordenada Y inicial (esquina superior izquierda).
        ancho (int): Ancho del rectángulo.
        alto (int): Alto del rectángulo.
        color (str): Color del rectángulo en formato hexadecimal (por defecto blanco).
    """
    try:
        # Obtener el canvas
        canvas = canvas_storage.get(canvas_id)
        if canvas is None:
            raise ValueError(f"No se encontró un canvas con nombre '{canvas_id}'.")

        # Crear objeto de dibujo
        draw = ImageDraw.Draw(canvas)

        # Coordenadas del rectángulo
        rect_coords = [(x, y), (x + ancho, y + alto)]

        # Dibujar rectángulo relleno
        draw.rectangle(rect_coords, fill=color)

        # Guardar canvas actualizado
        canvas_storage[canvas_id] = canvas

        print(f"[DEBUG RECTCANVAS] Rectángulo agregado al canvas: {canvas_id}")
        return ""

    except Exception as e:
        return f"Error al dibujar rectángulo: {str(e)}"
