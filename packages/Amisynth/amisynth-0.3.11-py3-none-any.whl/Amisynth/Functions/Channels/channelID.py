import xfox
import discord
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def channelID(nombre: str = None, *args, **kwargs):
    context = utils.ContextAmisynth()
    if nombre is None:
        channel  = context.channel_id
    else:
        channel = context.obj_guild.fetch_channel(int(nombre))

    return channel
