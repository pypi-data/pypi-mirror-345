import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs, name="mentionedChannels")
async def mentioned_channels(numero: str = None, fallback_to_current=False, *args, **kwargs):
    context = utils.ContextAmisynth()
    channels = context.get_channel_mentions()  # Obtener menciones de canales

    if not channels:
        if fallback_to_current or fallback_to_current is "true":
            print("[DEBUG MENTIONEDCHANNELS]: No se encontraron menciones, devolviendo canal actual.")
            return str(context.channel_id)
        print("[DEBUG MENTIONEDCHANNELS]: No se encontraron menciones de canales.")
        return ""

    if numero is None:
        return str(channels[0])

    if numero.isdigit():
        indice = int(numero) - 1
        if 0 <= indice < len(channels):
            return str(channels[indice])
        else:
            print("[DEBUG MENTIONED_CHANNELS]: No hay suficiente cantidad de canales mencionados.")
            return ""

    if numero == ">":
        return str(max(channels, key=lambda channel: channel.id))
    
    if numero == "<":
        return str(min(channels, key=lambda channel: channel.id))
    
    print(f"[DEBUG MENTIONED_CHANNELS]: Parámetro no válido: {numero}")
    raise ValueError(f":x: No pusiste el parámetro adecuado: `{numero}`, en `$mentionedChannels[{numero}]`")
