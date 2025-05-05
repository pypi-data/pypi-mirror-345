import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def setChannelVar(nombre=None, value=None, guild_id=None, channel_id=None, *args, **kwargs):
    """Establece una variable para un canal específico."""
    context = utils.ContextAmisynth()
    
    if nombre is None or value is None:
        raise ValueError(":x: Error, el nombre o el valor están vacíos en la función `$setChannelVar[?;?]`.")
    
    if guild_id is None:
        guild_id = context.guild_id

    if channel_id is None:
        channel_id = context.channel_id

    var = utils.VariableManager()
    
    # Establece el valor para el canal especificado
    var.set_value("channel", key=nombre, value=value, guild_id=guild_id, channel_id=channel_id)
    print("[DEBUG SETCHANNELVAR]white_check_mark: Variable `{nombre}` establecida con éxito para el canal.")
    return f""