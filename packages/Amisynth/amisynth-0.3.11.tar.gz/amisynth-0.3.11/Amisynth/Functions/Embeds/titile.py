import xfox
from Amisynth.utils import embeds  # Asumo que embeds es una lista global que estás usando

@xfox.addfunc(xfox.funcs)
async def title(texto_title: str=None, indice: int = 1, *args, **kwargs):
    """
    Guarda un título en la lista de embeds, con un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    
    :param texto_title: El texto que se quiere mostrar como título en el embed.
    :param indice: El índice opcional del embed (posición en la lista).
    """
    if texto_title is None:
        print("[DEBUG TITLE] La funciom $title esta vicia")
        raise ValueError(":x: Error en $title esta vacio")
    # Crear un embed con el texto de la descripción
    # Crear el embed con el título
    embed = {
        "title": texto_title,
        "index": indice  # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo el título
    for i, item in enumerate(embeds):
        if item["index"] == indice:
            # Mantener los otros atributos del embed y solo actualizar el título
            embeds[i]["title"] = texto_title
            break
    else:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
