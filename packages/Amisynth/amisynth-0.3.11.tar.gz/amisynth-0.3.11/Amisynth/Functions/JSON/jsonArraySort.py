import xfox
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonArraySort(*claves, **kwargs):
    if not claves:
        return ""  # Si no se pasan claves, devuelve vacío
    
    data = json_storage

    try:
        for clave in claves[:-1]:
            if clave not in data or not isinstance(data[clave], dict):
                return ""  # Si alguna clave intermedia no existe, devuelve vacío
            data = data[clave]  # Avanza en la estructura del JSON
        
        last_key = claves[-1]

        if last_key not in data or not isinstance(data[last_key], list):
            return ""  # Si la clave final no existe o no es un array, devuelve vacío

        data[last_key].sort()  # Ordena el array en orden ascendente
        return ""
    except Exception as e:
        raise ValueError(f"Error al ordenar el array: {e}")
