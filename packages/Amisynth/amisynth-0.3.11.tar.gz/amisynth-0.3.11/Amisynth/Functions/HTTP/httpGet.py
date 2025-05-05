import aiohttp
import json
import Amisynth.utils as utils  # Importamos el archivo utils donde está http_data
import xfox

# Función para hacer la solicitud GET
@xfox.addfunc(xfox.funcs)
async def httpGet(url: str, *args, **kwargs):
    """Hace una solicitud HTTP GET con las cabeceras personalizadas y almacena el contenido en una variable global."""
    global utils  # Usamos el diccionario http_data de utils
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=utils.http_data["headers"]) as response:
                response.raise_for_status()
                utils.http_response = await response.text()  # Almacena la respuesta
                utils.http_status = await response.status
                print("[DEBUG HTTPGET] Respuesta GET almacenada.")
                return ""
    except Exception as e:
        return f"Error en $httpGet: {str(e)}"
