import xfox
import Amisynth.utils as utils
import re

@xfox.addfunc(xfox.funcs)
async def findChannel(query: str, *args, **kwargs):
    context = utils.ContextAmisynth()
    guild = context.obj_guild

    if guild is None:
        print("[DEBUG FINDCHANNEL] No se puede buscar fuera de un servidor.")
        raise ValueError(":x: No se puede buscar fuera de un servidor.")

    query = query.strip()

    # 🟦 Si es mención de canal: <#123456789012345678>
    mention_match = re.match(r"<#(\d+)>", query)
    if mention_match:
        channel_id = int(mention_match.group(1))
        channel = guild.get_channel(channel_id)
        if channel:
            print(f"[DEBUG FINDCHANNEL] Encontrado por mención: {channel}")
            return str(channel.id)

    # 🟩 Si es ID
    if query.isdigit():
        channel = guild.get_channel(int(query))
        if channel:
            print(f"[DEBUG FINDCHANNEL] Encontrado por ID: {channel}")
            return str(channel.id)

    # 🟨 Si es nombre de canal
    query_lower = query.lower()
    for channel in guild.channels:
        if channel.name.lower() == query_lower:
            print(f"[DEBUG FINDCHANNEL] Encontrado por nombre: {channel}")
            return str(channel.id)

    print("[DEBUG FINDCHANNEL] Canal no encontrado")
    return ""
