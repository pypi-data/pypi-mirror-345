import discord
import xfox
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def sendMessage(texto, retornar_id="false", canal_id=None, *args, **kwargs): 
    n = utils.ContextAmisynth()
    # Si no se pasa un canal_id, intenta obtenerlo desde el contexto
    if canal_id is None:
        canal = await n.get_channel(int(n.channel_id))  # Obtener el canal desde el contexto
       
    else:
        canal = await n.get_channel(int(canal_id))  # Obtener el canal desde el ID pasado
    
    if canal is None:
        raise ValueError(":x: Error en obtener el canal ID, Contacte con Soporte.")

    # Verificar si el canal es válido antes de enviar el mensaje
    if isinstance(canal, discord.TextChannel):
        mensaje = await canal.send(texto)
        if str(retornar_id).lower() == "true":
            return mensaje.id  # Retorna el ID del mensaje si se solicita
        
        return ""  # Retorna una cadena vacía si no se necesita el ID

    print(f"No se encontró un canal válido para enviar el mensaje. Canal ID: {canal_id}")
    return None  # Indicar que falló el envío
