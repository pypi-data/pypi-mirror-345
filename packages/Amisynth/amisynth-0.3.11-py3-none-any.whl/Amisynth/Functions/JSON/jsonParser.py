import xfox
from Amisynth.utils import json_storage
import ast

@xfox.addfunc(xfox.funcs)
async def jsonParse(entrada: str, *args, **kwargs):
    try:
        nuevo_json = ast.literal_eval(entrada)  # Evalúa la cadena como un diccionario
        if not isinstance(nuevo_json, dict):
            raise ValueError("El JSON evaluado no es un diccionario válido.")

        
        json_storage.clear()  # Limpia el diccionario original
        json_storage.update(nuevo_json)  # Copia los nuevos valores en él
        
  
        return ""
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"Error en Evaluación del JSON: {str(e)}")
