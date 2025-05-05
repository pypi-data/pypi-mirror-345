import xfox
import Amisynth.utils as utils
import re

@xfox.addfunc(xfox.funcs)
async def channelPosition(channel_id: str = None, *args, **kwargs):
    context = utils.ContextAmisynth()
    guild = context.obj_guild
    current_channel = context.obj_channel

    if guild is None:
        print("[DEBUG CHANNELPOSITION] No se puede usar fuera de un servidor.")
        raise ValueError(":x: No se puede usar fuera de un servidor.")

    # Si no se proporciona canal, usar el actual
    if channel_id is None:
        channel = current_channel
    else:
        channel_id = channel_id.strip()
        
        # Detectar mención tipo <#1234567890>
        mention_match = re.match(r"<#(\d+)>", channel_id)
        if mention_match:
            channel_id = mention_match.group(1)

        if not channel_id.isdigit():
            print("[DEBUG CHANNELPOSITION] ID inválido.")
            return ""

        channel = guild.get_channel(int(channel_id))

    if channel:
        print(f"[DEBUG CHANNELPOSITION] Canal encontrado: {channel.name} con posición {channel.position}")
        return str(channel.position)
    
    print("[DEBUG CHANNELPOSITION] Canal no encontrado")
    return ""
