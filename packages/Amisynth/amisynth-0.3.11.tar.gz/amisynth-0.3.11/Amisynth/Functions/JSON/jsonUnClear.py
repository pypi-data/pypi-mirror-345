import xfox
from Amisynth.utils import json_storage


@xfox.addfunc(xfox.funcs)
async def jsonUnClear(*args, **kwargs):
    json_storage.clear()
    return ""