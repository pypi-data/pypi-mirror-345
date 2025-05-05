import xfox
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def typingTime(*args, **kwargs):
    context = kwargs["ctx_typing_env"][2]
    return context
