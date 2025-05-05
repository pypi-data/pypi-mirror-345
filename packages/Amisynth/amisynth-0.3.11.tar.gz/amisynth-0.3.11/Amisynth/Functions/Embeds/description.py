import xfox
from Amisynth.utils import embeds

@xfox.addfunc(xfox.funcs)
async def description(texto: str=None, indice: int = 1, *args, **kwargs):
    """
    Guarda una descripción en la lista de embeds, con un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    
    :param texto: El texto de la descripción.
    :param indice: El índice opcional del embed (posición en la lista).
    """
    if texto is None:
        print("[DEBUG DESCRIPTION] La funciom $description esta vicia")
        raise ValueError(":x: Error en $description esta vacio")
    # Crear un embed con el texto de la descripción
    embed = {
        "description": texto,
        "index": indice  # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo la descripción
    for i, item in enumerate(embeds):
        if item.get("index") == indice:
            # Mantener los otros atributos del embed y solo actualizar la descripción
            embeds[i]["description"] = texto
            break
    else:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
