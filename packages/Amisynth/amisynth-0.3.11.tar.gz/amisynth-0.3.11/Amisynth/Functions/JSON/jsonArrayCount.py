import xfox
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonArrayCount(*claves, **kwargs):
    if not claves:
        raise ValueError("Error: Debes proporcionar al menos una clave en $jsonArrayCount[]")
    
    data = json_storage
    
    try:
        for clave in claves:
            if clave not in data:
                return "-1"
            data = data[clave]  # Avanza en la estructura del JSON
        
        return str(len(data)) if isinstance(data, list) else "-1"
    except Exception as e:
        raise ValueError(f"Error al contar elementos en el array: {e}")
