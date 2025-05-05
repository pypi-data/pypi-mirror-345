from PIL import Image

import xfox
import discord
import io
from Amisynth.utils import canvas_storage
@xfox.addfunc(xfox.funcs)
async def getCanvas(canvas_id: str=None, *args, **kwargs):
    if canvas_id is  None:
        raise ValueError(":x: Error en `$getCanvas[?]` argumento vacio.")
    if canvas_id in canvas_storage:
        return f"attachment://{canvas_id}.png"
    else:
        raise ValueError(":x: Error en `$getCanvas[]` ID propocionado no encontrado.")
