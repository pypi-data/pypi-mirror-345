import xfox
from Amisynth.Functions.storage import split_storage  # Importamos el almacenamiento global


@xfox.addfunc(xfox.funcs)
async def joinSplitText(separator: str, *args, **kwargs):
    global split_storage
    if "last_split" not in split_storage:
        raise ValueError("No text has been split yet")
    
    return separator.join(split_storage.get("last_split", []))