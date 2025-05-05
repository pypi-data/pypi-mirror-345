import xfox
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonArrayUnshift(*claves, value=None, **kwargs):
    if not claves:
        return ""  # Si no se pasan claves, devuelve vacío
    
    if value is None:
        return ""  # Si no se proporciona un valor, devuelve vacío

    data = json_storage

    try:
        for clave in claves[:-1]:
            if clave not in data or not isinstance(data[clave], dict):
                return ""  # Si alguna clave intermedia no existe, devuelve vacío
            data = data[clave]  # Avanza en la estructura del JSON
        
        last_key = claves[-1]
        
        if last_key not in data or not isinstance(data[last_key], list):
            data[last_key] = []  # Si la clave no existe o no es un array, la inicializa como lista
        
        data[last_key].insert(0, value)  # Agrega el valor al inicio del array
        return ""
    except Exception as e:
        raise ValueError(f"Error al hacer unshift en el array: {e}")
