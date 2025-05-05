import xfox
import json
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonStringify(*args, **kwargs):
    try:
        return json.dumps(json_storage, ensure_ascii=False, separators=(',', ':'))
    except Exception as e:
        raise ValueError(f"Error al convertir JSON a string: {e}")
