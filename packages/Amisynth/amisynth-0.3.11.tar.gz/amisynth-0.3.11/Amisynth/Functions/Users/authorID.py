import xfox
import discord
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def authorID(nombre: str = None, *args, **kwargs):
    context = utils.ContextAmisynth()
    if nombre is None:
        author_id  = context.author_id
    else:
        author_id = context.get_user_id_by_username(nombre)

    return author_id
