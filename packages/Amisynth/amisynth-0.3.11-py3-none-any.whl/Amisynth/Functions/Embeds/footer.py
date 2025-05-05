import xfox
from Amisynth.utils import embeds  # Asumo que embeds es una lista global que estás usando

@xfox.addfunc(xfox.funcs)
async def footer(texto_footer: str=None, indice: int = 1, *args, **kwargs):
    """
    Guarda un footer en la lista de embeds, con un texto de footer específico y un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    
    :param texto_footer: El texto que se quiere mostrar en el footer del embed.
    :param indice: El índice opcional del embed (posición en la lista).
    """
    if texto_footer is None:
        raise ValueError(":x: Error argumento primero de `$footer[?;..]` vacio")
    # Crear el embed con el footer
    embed = {
        "footer": texto_footer,
        "index": indice  # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo el footer
    for i, item in enumerate(embeds):
        if item["index"] == indice:
            # Mantener los otros atributos del embed y solo actualizar el footer
            embeds[i]["footer"] = texto_footer
            break
    else:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
