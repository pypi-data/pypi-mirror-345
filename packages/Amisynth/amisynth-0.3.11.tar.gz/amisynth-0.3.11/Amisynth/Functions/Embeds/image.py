import xfox
from Amisynth.utils import embeds  # Asegúrate de que 'embeds' sea la lista global que deseas modificar

@xfox.addfunc(xfox.funcs)
async def image(url_imagen: str=None, indice: int = 1, *args, **kwargs):
    """
    Guarda una imagen en la lista de embeds, con una URL de imagen específica y un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    """
    if url_imagen is None:
        raise ValueError(":x: Error argumento primero de `$image[?;..]` vacio")
    embed = {
        "image": url_imagen,  # Solo la URL de la imagen
        "index": indice       # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo la imagen
    found = False
    for i, item in enumerate(embeds):
        if item.get("index") == indice:
            # Mantener los otros atributos del embed y solo actualizar la imagen
            embeds[i]["image"] = url_imagen
            found = True
            break
    if not found:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
