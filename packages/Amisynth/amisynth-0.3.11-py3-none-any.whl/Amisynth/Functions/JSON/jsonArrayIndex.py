import xfox
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonArrayIndex(*args, **kwargs):
    if len(args) < 2:
        return ""  # Si no se pasan suficientes argumentos, devuelve vacío

    *claves, valor = args  # Extrae claves y el valor a buscar
    data = json_storage

    try:
        for clave in claves:
            if clave not in data:
                return "-1"
            data = data[clave]  # Avanza en la estructura del JSON
        
        if isinstance(data, list):
            return str(data.index(valor)) if valor in data else "-1"
        return "-1"
    except Exception as e:
        raise ValueError(f"Error al buscar el índice en el array: {e}")
