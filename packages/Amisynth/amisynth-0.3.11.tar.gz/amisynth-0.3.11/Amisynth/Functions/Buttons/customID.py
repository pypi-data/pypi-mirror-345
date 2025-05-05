import xfox
import discord
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def customID(*args, **kwargs):
    n = utils.ContextAmisynth().custom_id
    return n
