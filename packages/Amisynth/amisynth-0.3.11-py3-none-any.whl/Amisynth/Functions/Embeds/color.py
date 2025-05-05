import xfox
from Amisynth.utils import embeds  # Asumo que embeds es una lista global que estás usando

@xfox.addfunc(xfox.funcs)
async def color(color: str=None, indice: int = 1, *args, **kwargs):
    """
    Guarda un color en la lista de embeds, con un color específico y un índice opcional.
    Si se especifica el índice, se inserta o actualiza en esa posición. Si no, se agrega en la posición 1.
    
    :param color: El color en formato hexadecimal (con o sin '#').
    :param indice: El índice opcional del embed (posición en la lista).
    """

    if color is None:
        raise ValueError(":x: Error argumento color vacio. `$color[?;..]`")
    # Asegurarse de que el color tiene el formato adecuado
    if color.startswith('#'):
        color = color[1:]  # Eliminar el '#' si está presente
    if len(color) == 6:  # Asegurarse de que el código hexadecimal sea válido
        try:
            int(color, 16)  # Comprobar si el color es un número hexadecimal
        except ValueError:
            raise ValueError(f"Error: El color proporcionado no es un código hexadecimal válido: $color[{color}]")
    else:
        raise ValueError(f"Error El color debe ser un código hexadecimal de 6 caracteres.")

    # Crear el embed con solo el color
    embed = {
        "color": int(color, 16),  # Convertir el código hexadecimal a entero
        "index": indice           # Añadir el índice para identificar la posición
    }

    # Buscar si ya existe un embed con ese índice y actualizar solo el color
    for i, item in enumerate(embeds):
        if item.get("index") == indice:
            # Mantener los otros atributos del embed y solo actualizar el color
            embeds[i]["color"] = int(color, 16)
            break
    else:
        # Si no se encontró, agregar uno nuevo
        embeds.append(embed)

    return ""
