import xfox
import discord
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def categoryIDs(separator:str, guild_id=None, *args, **kwargs):
    contexto = utils.ContextAmisynth()

    # Si no se proporciona guild_id, usamos el del contexto
    if guild_id is None:
        guild_id = contexto.guild_id

    # Obtenemos los nombres de los canales
    nombres = contexto.get_categorys_ids(guild_id=int(guild_id))
    # Validamos si hay canales
    if not nombres:
        return ""

    # Unimos los nombres con el separador
    return separator.join(nombre for nombre in nombres)
