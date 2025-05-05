import xfox
from Amisynth.utils import embeds
import re  # Asegúrate de que 'embeds' sea la lista global que deseas modificar
URL_REGEX = re.compile(r"^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$", re.IGNORECASE)
@xfox.addfunc(xfox.funcs)
async def thumbnail(url: str, indice: int = 1, *args, **kwargs):
    """
    Guarda un thumbnail en la lista de embeds, con una URL de imagen específica y un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    """

    if url is None:
        print("[DEBUG THUMBNAIL] Esta vacia.")
        raise ValueError(f":x: URL Vacia en $thumbnail[]")
    
    elif not URL_REGEX.match(url):
        print("[DEBUG THUMBNAIL] URL inválida o None:", url)
        raise ValueError(f":x: URL no válida en $thumbnail[{url}]")
    
    embed = {
        "thumbnail_icon": url,  # URL de la imagen como thumbnail
        "index": indice    # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo el thumbnail
    found = False
    for i, item in enumerate(embeds):
        if item.get("index") == indice:
            # Mantener los otros atributos del embed y solo actualizar el thumbnail
            embeds[i]["thumbnail_icon"] = url
            found = True
            break
    if not found:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
