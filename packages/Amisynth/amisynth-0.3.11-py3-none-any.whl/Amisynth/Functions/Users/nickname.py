import xfox
import discord
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def nickname(id: str = None, *args, **kwargs):
    context = utils.ContextAmisynth()
    if id is None:
        username  = context.display_name
    else:
        username = context.get_nickname_by_id(int(id))

    return username
