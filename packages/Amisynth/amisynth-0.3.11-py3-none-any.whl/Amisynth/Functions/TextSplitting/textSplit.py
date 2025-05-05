import xfox
from Amisynth.Functions.storage import split_storage  # Importamos el almacenamiento global

@xfox.addfunc(xfox.funcs)
async def textSplit(text: str, separator: str = None, *args, **kwargs):
    global split_storage

    if separator is None or separator == "":  
        split_storage["last_split"] = list(text)  # Guardar cada letra en la lista
    else:
        split_storage["last_split"] = text.split(separator)  # Separar por el delimitador

    return ""
