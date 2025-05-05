

import xfox
from Amisynth.utils import ContextAmisynth

@xfox.addfunc(xfox.funcs)
async def isNumber(value=None, *args, **kwargs):
    if value is None:
        raise ValueError(':x: Error en `$isNumber[?]` argumento vacio.')
    try:
        float(value)
        return "true"
    except:
        return "false"
