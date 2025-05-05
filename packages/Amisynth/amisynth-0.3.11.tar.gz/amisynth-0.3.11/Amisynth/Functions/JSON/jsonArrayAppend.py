import xfox
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonArrayAppend(*args, **kwargs):
    if len(args) < 2:
        return ""  # Si no se pasan suficientes argumentos, devuelve vacío

    *claves, valor = args  # Extrae claves y el valor a agregar
    data = json_storage

    try:
        for clave in claves:
            if clave not in data:
                data[clave] = {}  # Si la clave no existe, crea un diccionario
            data = data[clave]  # Avanza en la estructura del JSON
        
        if isinstance(data, list):
            data.append(valor)  # Agrega el valor al array
        else:
            data[claves[-1]] = [valor]  # Si no es un array, lo convierte en uno con el valor

        return ""
    except Exception as e:
        raise ValueError(f"Error al agregar el valor al array: {e}")
