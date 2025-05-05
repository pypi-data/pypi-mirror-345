import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def mentioned(numero: str = None, fallback_to_author: bool = False, *args, **kwargs):
    context = utils.ContextAmisynth()
    mentions = context.get_mentions()  # Obtiene la lista de IDs mencionados

    if not mentions:
        if fallback_to_author:
            return context.author_id
        return None  # No hay menciones y no se solicita fallback

    if numero is "-":
        return mentions  # Retorna todas las menciones si no se especifica un número

    numero = numero.strip()  # Elimina espacios innecesarios

    if numero == "<":
        return mentions[0]  # Primer mencionado
    elif numero == ">":
        return mentions[-1]  # Último mencionado
    elif numero.isdigit():
        index = int(numero) - 1  # Convertir a índice (1 -> 0, 2 -> 1, etc.)
        if 0 <= index < len(mentions):
            return mentions[index]
    
    return None  # Si el número es inválido o está fuera de rango
