import xfox
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def messageID(*args, **kwargs):
    contexto = utils.ContextAmisynth()
    return  contexto.message_id
