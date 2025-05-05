import xfox
from PIL import ImageDraw, ImageFont
from Amisynth.utils import canvas_storage

@xfox.addfunc(xfox.funcs)
async def addTextCanvas(
    canvas_id: str,
    text: str = "Hola!",
    x: int = 150,
    y: int = 180,
    fill: str = "green",
    font_size: int = 20,
    font_path: str = None,
    *args,
    **kwargs
):
    """
    Dibuja texto en un canvas con opciones personalizadas.

    Parámetros:
        canvas_id (str): ID del canvas.
        text (str): Texto a dibujar.
        x (int): Posición horizontal.
        y (int): Posición vertical.
        fill (str): Color del texto.
        font_size (int): Tamaño de la fuente.
        font_path (str, opcional): Ruta a la fuente TrueType.
    """
    canvas = canvas_storage.get(canvas_id)
    if canvas is None:
        raise ValueError(f"No se encontró un canvas con ID '{canvas_id}'.")

    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except Exception as e:
        raise ValueError(f"No se pudo cargar la fuente: {e}")

    draw.text((x, y), text, fill=fill, font=font)
    return ""
