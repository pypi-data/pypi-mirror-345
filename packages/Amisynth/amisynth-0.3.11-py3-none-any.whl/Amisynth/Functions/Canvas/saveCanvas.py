import os
from PIL import Image
import Amisynth.utils as utils
from Amisynth.utils import canvas_storage
import xfox

@xfox.addfunc(xfox.funcs)
async def saveCanvas(folder: str, canvas_id: str, *args, **kwargs):
    """
    Guarda el canvas en una carpeta específica con el ID dado.
    Si la carpeta no existe, la crea antes de guardar el archivo.
    """
    # Verifica si el canvas existe
    if canvas_id not in canvas_storage:
        return f"Error: no existe el canvas con id '{canvas_id}'."
    
    # Verifica si la carpeta existe, si no, la crea
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"[DEBUG SAVECANVAS] Carpeta creada: {folder}")
    
    # Guarda el canvas como PNG en la carpeta indicada
    path = os.path.join(folder, f"{canvas_id}.png")
    canvas_storage[canvas_id].save(path)
    print(f"[DEBUG SAVECANVAS] Resultado: {path}")
    return ""
