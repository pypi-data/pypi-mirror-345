import xfox
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonExists(*claves, **kwargs):
    if not claves:
        raise ValueError("Error: Debes proporcionar al menos una clave en $jsonExists[]")
    
    data = json_storage
    
    try:
        for clave in claves:
            if clave not in data:
                return "false"
            data = data[clave]  # Avanza en la estructura del JSON
        
        return "true"
    except (KeyError, TypeError):
        return "false"
