import xfox
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def typingUser(*args, **kwargs):
    context = kwargs["ctx_typing_env"][1]

    userTyping = context
    return userTyping
