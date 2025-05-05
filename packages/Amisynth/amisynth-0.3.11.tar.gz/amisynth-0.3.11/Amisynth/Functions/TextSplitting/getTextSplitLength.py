import xfox
from Amisynth.Functions.storage import split_storage  # Importamos el almacenamiento global

@xfox.addfunc(xfox.funcs)
async def getTextSplitLength(*args, **kwargs):
    global split_storage
    return str(len(split_storage.get("last_split", [])))  # Devuelve la cantidad de elementos
