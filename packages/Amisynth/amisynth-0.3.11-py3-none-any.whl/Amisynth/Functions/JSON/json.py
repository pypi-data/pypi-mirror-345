import xfox
from Amisynth.utils import json_storage
import asyncio
@xfox.addfunc(xfox.funcs)
async def json(*args, **kwargs):
    try:
        data = json_storage  # Inicia con el JSON base

        for clave in args:
            if isinstance(data, dict) and clave in data:
                data = data[clave]  # Acceder a clave en diccionario
            elif isinstance(data, list):
                try:
                    index = int(clave)  # Convertir clave a entero si es índice
                    data = data[index]  # Acceder a índice en lista
                except ValueError:
                    return f""
                    
                except IndexError:
                    return f""
            else:
                return f""
        
        return data  # Devuelve el resultado final
    except Exception as e:
        raise ValueError(f"Error inesperado: {str(e)}")

