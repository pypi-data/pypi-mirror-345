import xfox
import discord
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def getUserVar(nombre:str=None, user_id:str=None, guild_id:str=None,  *args, **kwargs):
    context = utils.ContextAmisynth()
    if nombre is None:
        raise ValueError(":x: Error el nombre esta vacio de la `$setUserVar[?;..]`")
    
    if user_id is None:
        user_id = context.author_id

    if guild_id is None:
        guild_id = context.guild_id

    var = utils.VariableManager()

    value = var.get_value(level="user", key=str(nombre), guild_id=str(guild_id), user_id=str(user_id))
    return value