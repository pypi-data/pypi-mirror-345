import xfox
from PIL import ImageDraw
from Amisynth.utils import canvas_storage

@xfox.addfunc(xfox.funcs)
async def addCircleCanvas(canvas_id: str, x: int, y: int, radio: int, color: str = "#FFFFFF", *args, **kwargs):
    """
    Dibuja un círculo en el canvas con el color y radio especificado.

    Parámetros:
        canvas_id (str): ID del canvas destino.
        x (int): Coordenada X del centro del círculo.
        y (int): Coordenada Y del centro del círculo.
        radio (int): Radio del círculo.
        color (str): Color del círculo en formato hexadecimal (por defecto blanco).
    """
    try:
        # Obtener canvas
        canvas = canvas_storage.get(canvas_id)
        if canvas is None:
            raise ValueError(f"No se encontró un canvas con nombre '{canvas_id}'.")

        # Crear objeto de dibujo
        draw = ImageDraw.Draw(canvas)

        # Coordenadas del círculo
        left_up = (x - radio, y - radio)
        right_down = (x + radio, y + radio)

        # Dibujar círculo relleno
        draw.ellipse([left_up, right_down], fill=color)

        # Guardar canvas actualizado
        canvas_storage[canvas_id] = canvas

        print(f"[DEBUG CIRCLECANVAS] Círculo agregado al canvas: {canvas_id}")
        return ""

    except Exception as e:
        raise ValueError(f"Error al dibujar círculo: {str(e)}")
