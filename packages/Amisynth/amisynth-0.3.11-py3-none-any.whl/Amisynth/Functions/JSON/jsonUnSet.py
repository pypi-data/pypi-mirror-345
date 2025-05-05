import xfox
from Amisynth.utils import json_storage


@xfox.addfunc(xfox.funcs)
async def jsonUnSet(*claves, **kwargs):
    if not claves:
        raise ValueError("Error: Debes proporcionar al menos una clave en $jsonUnSet[]")
    
    data = json_storage
    
    try:
        for clave in claves[:-1]:
            if clave not in data or not isinstance(data[clave], dict):
                return ""
            data = data[clave]
        
        del data[claves[-1]]
        return ""
    except (KeyError, TypeError):
        raise ValueError("Error: No se pudo eliminar la clave en el JSON almacenado")