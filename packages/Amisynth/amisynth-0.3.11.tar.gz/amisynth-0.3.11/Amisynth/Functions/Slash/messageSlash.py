from typing import List, Dict, Optional
import xfox
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def messageSlash(nombre: str, *args, **kwargs):
    context = utils.ContextAmisynth()
    datos = context.slash_options
    
    if datos is None:
        return ""

    for item in datos:
        if item.get("name") == nombre:
            return item.get("value")  # Retorna el valor si encuentra coincidencia
    return ""
