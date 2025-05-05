import xfox
from PIL import Image, ImageDraw
import os
import requests
from io import BytesIO
from Amisynth.utils import canvas_storage

@xfox.addfunc(xfox.funcs)
async def pasteCanvas(canvas_id: str, path: str, x: int, y: int, radio: int = 0, ancho: int = None, largo: int = None, *args, **kwargs):
    """
    Pega una imagen en el canvas con el ID proporcionado, redimensionándola según ancho y largo,
    y aplicando esquinas redondeadas con el radio especificado.

    Parámetros:
        canvas_id (str): El ID del canvas donde se pegará la imagen.
        path (str): URL o ruta local de la imagen a cargar.
        x (int): Coordenada X donde se pegará la imagen.
        y (int): Coordenada Y donde se pegará la imagen.
        radio (int): Radio para redondear las esquinas de la imagen.
        ancho (int, opcional): Ancho de la imagen a pegar.
        largo (int, opcional): Alto de la imagen a pegar.
    """
    try:
        # Cargar imagen desde URL o archivo local
        if path.startswith("http://") or path.startswith("https://"):
            response = requests.get(path)
            if response.status_code != 200:
                raise ValueError(f"Error al intentar acceder a la URL: {path}")
            img = Image.open(BytesIO(response.content)).convert("RGBA")
        else:
            if not os.path.exists(path):
                raise ValueError(f"El archivo no existe en la ruta proporcionada: {path}")
            img = Image.open(path).convert("RGBA")

        # Redimensionar si se especifican ancho y largo
        if ancho and largo:
            img = img.resize((ancho, largo), Image.Resampling.LANCZOS)


        # Aplicar esquinas redondeadas si radio > 0
        if radio > 0:
            mask = Image.new('L', img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), img.size], radius=radio, fill=255)
            img.putalpha(mask)

        # Obtener canvas
        canvas_image = canvas_storage.get(canvas_id)
        if canvas_image is None:
            raise ValueError(f"No se encontró un canvas con nombre '{canvas_id}'.")

        # Pegar imagen en canvas
        canvas_image.paste(img, (x, y), img)
        canvas_storage[canvas_id] = canvas_image

        print(f"[DEBUG PASTECANVAS] Imagen pegada en el canvas: {canvas_id}")
        return ""

    except Exception as e:
        return f"Error al pegar la imagen: {str(e)}"
