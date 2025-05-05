import xfox
from Amisynth.utils import json_storage


@xfox.addfunc(xfox.funcs)
async def jsonSetString(*args, **kwargs):
    if len(args) < 2:
        raise ValueError("Error: Debes proporcionar al menos una clave y un valor")
    
    *claves, valor = args
    data = json_storage
    
    try:
        for clave in claves[:-1]:
            if clave not in data or not isinstance(data[clave], dict):
                data[clave] = {}
            data = data[clave]
        
        data[claves[-1]] = str(valor)  # Asegura que el valor se almacene como string
        return ""
    except (KeyError, TypeError):
        raise ValueError("Error: No se pudo establecer el valor en el JSON almacenado")
