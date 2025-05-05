import xfox
from Amisynth.Functions.storage import split_storage  # Importamos el almacenamiento global

@xfox.addfunc(xfox.funcs)
async def splitText(index: str, *args, **kwargs):
    global split_storage
    try:
        index = int(index) - 1  # Ajustar para que comience desde 1
        return split_storage.get("last_split", [""])[index]  # Obtener el índice solicitado
    except (ValueError, IndexError):
        return ""  # Si el índice no existe, devolver vacío
