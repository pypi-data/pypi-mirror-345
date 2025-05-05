import json
import Amisynth.utils as utils
import xfox

@xfox.addfunc(xfox.funcs)
async def httpResult(parametro: str, *args, **kwargs):
    """Devuelve el valor de un parámetro específico dentro del JSON almacenado en utils.http_response.
       Si se pasa '-1', devuelve todo el JSON."""

    # Verificación de la existencia de http_response en utils
    if not hasattr(utils, 'http_response') or utils.http_response is None:
        print("[DEBUG HTTPRESULT] Error: No se ha realizado una solicitud GET previamente.")
        return "Error: No se ha realizado una solicitud GET previamente."

    try:
        # Si la respuesta es una cadena, intentar cargarla como JSON
        if isinstance(utils.http_response, str):
            data = json.loads(utils.http_response)  # Convertimos la cadena a un diccionario
        else:
            data = utils.http_response  # Asumimos que ya es un diccionario

        # Si el parámetro es '-1', devolver todo el JSON de forma legible
        if parametro == "-1":
            return json.dumps(data, indent=2)

        # Devolver el valor correspondiente a la clave solicitada
        if parametro in data:
            return data[parametro]
        else:
            print(f"[DEBUG HTTPRESULT] Error: La clave '{parametro}' no existe en la respuesta.")
            return f"Error: La clave '{parametro}' no se encuentra en la respuesta."

    except json.JSONDecodeError:
        print("[DEBUG HTTPRESULT] Error: No se pudo procesar el JSON.")
        raise ValueError(":x: Error: No se pudo procesar la respuesta JSON.")
    except Exception as e:
        # Manejo de otros posibles errores
        print(f"[DEBUG HTTPRESULT] Error desconocido: {str(e)}")
        raise ValueError(f":x: Error desconocido: {str(e)}")
