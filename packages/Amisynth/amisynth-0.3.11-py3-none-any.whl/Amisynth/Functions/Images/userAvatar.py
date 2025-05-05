import xfox
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def userAvatar(id=None, *args, **kwargs):
    context = utils.ContextAmisynth()

    if id is None:
        n = int(context.author_id)

    else:
        n = int(id)
        
        
    avatar = context.get_user_avatar_by_id(n)

    return avatar
    

