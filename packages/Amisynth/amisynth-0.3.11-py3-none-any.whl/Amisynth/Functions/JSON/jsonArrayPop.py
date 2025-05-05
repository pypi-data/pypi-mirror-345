import xfox
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonArrayPop(*claves, **kwargs):
    if not claves:
        return ""  # Si no se pasan claves, devuelve vacío
    
    data = json_storage

    try:
        for clave in claves:
            if clave not in data:
                return ""  # Si la clave no existe, devuelve vacío
            data = data[clave]  # Avanza en la estructura del JSON
        
        if isinstance(data, list) and data:
            return str(data.pop())  # Elimina y devuelve el último elemento
        return ""  # Si no es un array o está vacío, devuelve vacío
    except Exception as e:
        raise ValueError(f"Error al hacer pop en el array: {e}")
