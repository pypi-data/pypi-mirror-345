import xfox
from Amisynth.utils import embeds  # Asumo que embeds es una lista global que estás usando

@xfox.addfunc(xfox.funcs)
async def footerIcon(url: str, indice: int = 1, *args, **kwargs):
    """
    Guarda un footer con ícono en la lista de embeds, con una URL de ícono y un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    
    :param url: La URL del ícono que se quiere mostrar en el footer.
    :param indice: El índice opcional del embed (posición en la lista).
    """
    # Crear el embed con el ícono en el footer
    embed = {
        "footer_icon": url,  # URL del ícono como footer_icon
        "index": indice      # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo el footer_icon
    for i, item in enumerate(embeds):
        if item.get("index") == indice:
            # Mantener los otros atributos del embed y solo actualizar el footer_icon
            embeds[i]["footer_icon"] = url
            break
    else:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
