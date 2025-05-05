import xfox
from Amisynth.utils import embeds  # Asumo que embeds es una lista global que estás usando

@xfox.addfunc(xfox.funcs)
async def titleURL(url: str, indice: int = 1, *args, **kwargs):
    """
    Guarda una URL en el título del embed, con un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    
    :param url: La URL que se quiere asociar al título del embed.
    :param indice: El índice opcional del embed (posición en la lista).
    """

    if url is None:
        print("[DEBUG TITLE] La funciom $titleURL[?;..] esta vicia")
        raise ValueError(":x: Error en `$titleURL[?;..]` esta vacio")
    # Crear el embed con la URL en el título
    embed = {
        "title_url": url,  # URL asociada al título
        "index": indice    # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo la URL
    for i, item in enumerate(embeds):
        if item.get("index") == indice:
            # Mantener los otros atributos del embed y solo actualizar la URL
            embeds[i]["title_url"] = url
            break
    else:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
