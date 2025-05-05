import xfox
import json
from Amisynth.utils import json_storage

@xfox.addfunc(xfox.funcs)
async def jsonPretty(indent: str = "4", **kwargs):
    try:
        indent = int(indent)  # Convierte el valor de indent a entero
        return json.dumps(json_storage, ensure_ascii=False, indent=indent)
    except ValueError:
        raise ValueError("Error: El valor de indent debe ser un número entero válido.")
    except Exception as e:
        raise ValueError(f"Error al convertir JSON a string: {e}")
