import xfox
import discord
from Amisynth.utils import ContextAmisynth
@xfox.addfunc(xfox.funcs)
async def channelSystem(*args, **kwargs):
    ctx = ContextAmisynth()
    n = ctx.obj_guild.system_channel.id
    return n

