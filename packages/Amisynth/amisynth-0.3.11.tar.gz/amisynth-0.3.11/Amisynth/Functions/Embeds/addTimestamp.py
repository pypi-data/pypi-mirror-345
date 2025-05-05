import xfox
from Amisynth.utils import embeds  # Asumo que embeds es una lista global que estás usando
from datetime import datetime
@xfox.addfunc(xfox.funcs)
async def addTimestamp(indice=None, *args, **kwargs):
    """
    Agrega un timestamp en la lista de embeds con un índice opcional.
    Si no se especifica el índice, se agrega en la posición 1.
    
    :param args: Argumentos opcionales, el primer argumento será el índice.
    """
    if indice is None:
        indice = 1
    # Verificar si hay un argumento de índice, si no, asignar el valor predeterminado de 1
    
    embed = {
        "timestamp": "true",  # Aquí puedes definir lo que quieras almacenar en el embed
        "index": int(indice)           # El índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizarlo
    for i, item in enumerate(embeds):
        if item.get("index") == int(indice):
            # Actualizamos el embed solo si el índice coincide
            embeds[i]["timestamp"] = "true"  # Aquí puedes poner lo que quieras actualizar
            break
    else:
        # Si no se encontró, agregamos un nuevo embed con ese índice
        embeds.append(embed)

    return ""
