import xfox
from Amisynth.utils import json_storage
import ast

@xfox.addfunc(xfox.funcs)
async def jsonSet(*args, **kwargs):
    if len(args) < 2:
        raise ValueError("Debes establecer una clave y valor")
    
    *claves, valor = args
    data = json_storage
    
    try:
        for clave in claves[:-1]:
            if clave not in data or not isinstance(data[clave], dict):
                data[clave] = {}
            data = data[clave]
        
        data[claves[-1]] = valor
        return ""
    except (KeyError, TypeError):
       raise ValueError("Nose pudo establece en JSON Almacenado")