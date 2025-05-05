import xfox
import math
from PIL import ImageDraw
from Amisynth.utils import canvas_storage

@xfox.addfunc(xfox.funcs)
async def addPolygonCanvas(
    canvas_id: str,
    x: int,
    y: int,
    lados: int,
    radio: int,
    borde_color: str = "#FFFFFF",
    relleno_color: str = None,
    grosor: int = 1,
    rotacion: float = 0,
    *args, **kwargs
):
    """
    Dibuja un polígono regular en el canvas.

    Parámetros:
        canvas_id (str): ID del canvas donde se dibujará.
        x (int): Coordenada X del centro del polígono.
        y (int): Coordenada Y del centro del polígono.
        lados (int): Número de lados del polígono (mínimo 3).
        radio (int): Distancia del centro a los vértices.
        borde_color (str): Color del borde (contorno) del polígono.
        relleno_color (str | None): Color de relleno del polígono (si es None, sin relleno).
        grosor (int): Grosor del borde.
        rotacion (float): Rotación en grados del polígono.
    """
    try:
        if lados < 3:
            raise ValueError("El número de lados debe ser al menos 3.")

        canvas = canvas_storage.get(canvas_id)
        if canvas is None:
            raise ValueError(f"No se encontró un canvas con nombre '{canvas_id}'.")

        draw = ImageDraw.Draw(canvas)

        # Convertir rotación a radianes
        angulo_rot = math.radians(rotacion)

        # Calcular los vértices del polígono
        puntos = [
            (
                x + radio * math.cos(2 * math.pi * i / lados + angulo_rot - math.pi / 2),
                y + radio * math.sin(2 * math.pi * i / lados + angulo_rot - math.pi / 2)
            )
            for i in range(lados)
        ]

        # Dibujar el relleno si se especifica
        if relleno_color:
            draw.polygon(puntos, fill=relleno_color)

        # Dibujar el contorno
        draw.line(puntos + [puntos[0]], fill=borde_color, width=grosor)

        # Guardar el canvas actualizado
        canvas_storage[canvas_id] = canvas
        print(f"[DEBUG POLYGON] Polígono de {lados} lados añadido al canvas.")
        return ""

    except Exception as e:
        return f"Error al dibujar polígono: {str(e)}"
