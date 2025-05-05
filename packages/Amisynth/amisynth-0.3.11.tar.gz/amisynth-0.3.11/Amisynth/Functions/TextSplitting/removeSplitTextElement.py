import xfox
from Amisynth.Functions.storage import split_storage  # Importamos el almacenamiento global


@xfox.addfunc(xfox.funcs)
async def removeSplitTextElement(index: str, *args, **kwargs):
    global split_storage
    if "last_split" not in split_storage:
        raise ValueError("No text has been split yet")
    
    try:
        index = int(index) - 1  # Ajustar para que empiece desde 1
        if 0 <= index < len(split_storage["last_split"]):
            del split_storage["last_split"][index]
        else:
            raise ValueError("Index out of range")
    except ValueError:
        raise ValueError("Invalid index: must be an integer")
    
    return ""
