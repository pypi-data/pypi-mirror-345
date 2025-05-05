import xfox
from Amisynth.Functions.storage import split_storage  # Importamos el almacenamiento global

@xfox.addfunc(xfox.funcs)
async def getTextSplitIndex(value: str, *args, **kwargs):
    global split_storage
    if "last_split" not in split_storage:
        raise ValueError("No text has been split yet")
    try:
        index = split_storage["last_split"].index(value) + 1  # Ajustar para que empiece desde 1
        return str(index)
    except ValueError:
        return "-1"  # Si no se encuentra, devuelve 0
