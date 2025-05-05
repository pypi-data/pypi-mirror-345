import xfox
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def message(index: str, *args, **kwargs):
    contexto = utils.ContextAmisynth()
    
    argumentos = contexto.arguments or []  # Asegurar que sea una lista


    try:
        index = int(index)  # Convertir una sola vez
    except ValueError:
        return ""  # Si no es un número, devolver vacío

    if index == -1:
        return " ".join(argumentos)  # Unir toda la lista en una cadena
    if 1 <= index <= len(argumentos):
        return argumentos[index - 1]  # Obtener el elemento ajustando índice
    return ""  # Si el índice está fuera de rango
