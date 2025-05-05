import xfox
from Amisynth.utils import embeds  # Asumo que embeds es una lista global que estás usando

@xfox.addfunc(xfox.funcs)
async def author(texto: str=None, indice: int = 1, *args, **kwargs):
    """
    Guarda un autor en la lista de embeds, con el texto del autor y un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    
    :param texto: El texto que se quiere mostrar como autor en el embed.
    :param indice: El índice opcional del embed (posición en la lista).
    """
    if texto is None:
        raise ValueError(f":x: Error el texto de author esta vacio")
    # Crear el embed con el texto del autor
    embed = {
        "author": texto,  # Solo el texto del autor
        "index": indice   # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo el texto del autor
    for i, item in enumerate(embeds):
        if item.get("index") == indice:
            # Mantener los otros atributos del embed y solo actualizar el texto del autor
            embeds[i]["author"] = texto
            break
    else:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
