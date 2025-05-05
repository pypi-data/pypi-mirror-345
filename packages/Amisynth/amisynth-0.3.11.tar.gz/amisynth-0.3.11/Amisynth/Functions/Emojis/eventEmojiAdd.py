import xfox
import discord
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs, "eventEmojiAdd")
async def emoji_addd(*args, **kwargs):
    
    context = utils.ContextAmisynth()
    emoji = context.emoji_name


    return emoji