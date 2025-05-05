
import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def getChannelVar(nombre:str=None, guild_id:str=None, channel_id:str=None, *args, **kwargs):
    """Obtiene una variable para un canal específico."""
    context = utils.ContextAmisynth()
    
    if nombre is None:
        raise ValueError(":x: Error, el nombre está vacío en la función `$getChannelVar[?]`.")
    
    if guild_id is None:
        guild_id = context.guild_id

    if channel_id is None:
        channel_id = context.channel_id

    var = utils.VariableManager()

    # Obtiene el valor para el canal especificado
    value = var.get_value("channel", key=nombre, guild_id=guild_id, channel_id=channel_id)
    
    if value is None:
        return f":x: No se encontró la variable `{nombre}` para el canal especificado."
    
    return value