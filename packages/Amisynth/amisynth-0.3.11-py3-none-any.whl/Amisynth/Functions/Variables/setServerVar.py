import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def setServerVar(nombre=None, value=None, guild_id=None, *args, **kwargs):
    """Establece una variable para un servidor específico."""
    context = utils.ContextAmisynth()

    if nombre is None or value is None:
        raise ValueError(":x: Error, el nombre o el valor están vacíos en la función `$setServerVar[?;?]`.")
    
    if guild_id is None:
        guild_id = context.guild_id

    var = utils.VariableManager()
    
    # Establece el valor para el servidor especificado
    var.set_value("guild", key=nombre, value=value, guild_id=guild_id)
    return ""