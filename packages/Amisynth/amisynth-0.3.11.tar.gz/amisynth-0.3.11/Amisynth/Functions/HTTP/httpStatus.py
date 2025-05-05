import aiohttp
import xfox
import Amisynth.utils as utils
import ast

# Función para HTTP POST
@xfox.addfunc(xfox.funcs, name="httpStatus")
async def http_status(*args, **kwargs):
    return utils.http_status