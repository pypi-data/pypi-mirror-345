import xfox
from Amisynth.utils import embeds  # Asumo que embeds es una lista global que estás usando

@xfox.addfunc(xfox.funcs)
async def authorURL(url: str=None, indice: int = 1, *args, **kwargs):
    """
    Guarda un autor con ícono en la lista de embeds, con la URL del ícono y un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    
    :param url: La URL del ícono que se quiere mostrar en el autor del embed.
    :param indice: El índice opcional del embed (posición en la lista).
    """
    if url is None:
        raise ValueError(":x: Error argumento primero de `$authorURL[?;..]` vacio.")
    # Crear el embed con el autor y el ícono
    embed = {
        "author_url": url,  # URL del ícono en el autor
        "index": indice     # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo el autor_url
    for i, item in enumerate(embeds):
        if item.get("index") == indice:
            # Mantener los otros atributos del embed y solo actualizar el author_url
            embeds[i]["author_url"] = url
            break
    else:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
