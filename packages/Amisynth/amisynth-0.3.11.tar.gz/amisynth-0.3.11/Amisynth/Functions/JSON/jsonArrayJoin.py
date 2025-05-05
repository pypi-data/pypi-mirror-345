import xfox
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonJoinArray(*claves_y_separador, **kwargs):
    if len(claves_y_separador) < 2:
        return ""  # Si no hay suficientes parámetros, devuelve vacío
    
    *claves, separador = claves_y_separador  # Extrae claves y separador
    data = json_storage

    try:
        for clave in claves:
            if clave not in data or not isinstance(data[clave], (dict, list)):
                return ""  # Si alguna clave no existe o no es válida, devuelve vacío
            data = data[clave]  # Avanza en la estructura del JSON

        if not isinstance(data, list):
            return ""  # Si el resultado no es una lista, devuelve vacío

        return separador.join(map(str, data))  # Une los elementos con el separador
    except Exception as e:
        raise ValueError(f"Error en $jsonJoinArray: {e}")
