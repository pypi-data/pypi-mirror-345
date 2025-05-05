from PIL import Image
import Amisynth.utils as utils
from Amisynth.utils import canvas_storage
import xfox
import os
import requests
from io import BytesIO

@xfox.addfunc(xfox.funcs)
async def loadCanvas(canvas_id: str, path: str, *args, **kwargs):
    """
    Carga una imagen desde una ruta local o URL y la guarda en el canvas con el ID proporcionado.
    """
    try:
        # Verifica si la ruta es una URL
        if path.startswith("http://") or path.startswith("https://"):
            # Intentamos cargar la imagen desde una URL
            response = requests.get(path)
            if response.status_code != 200:
                raise ValueError(f"Error al intentar acceder a la URL: {path}")
            img = Image.open(BytesIO(response.content)).convert("RGBA")
        else:
            # Verifica si el archivo existe en la ruta local
            if not os.path.exists(path):
                raise ValueError(f"El archivo no existe en la ruta proporcionada: {path}")
            img = Image.open(path).convert("RGBA")

        # Guarda la imagen en el canvas con el ID proporcionado
        canvas_storage[canvas_id] = img
        print(f"[DEBUG LOADCANVAS] Imagen cargada con éxito en el canvas: {canvas_id}")
        return ""
    
    except Exception as e:
        # Captura cualquier error y lo devuelve
        return f"Error al cargar la imagen: {str(e)}"
