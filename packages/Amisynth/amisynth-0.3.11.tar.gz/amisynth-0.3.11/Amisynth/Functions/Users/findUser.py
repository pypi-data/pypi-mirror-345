import xfox
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def findUser(query: str, fallback_to_author: bool = False, *args, **kwargs):
    context = utils.ContextAmisynth()
    guild = context.obj_guild

    if guild is None:
        print("[DEBUG FINDUSER] No se puede buscar fuera de un servidor.")
        raise ValueError(":x: No se puede buscar fuera de un servidor.")

    # Buscar por ID directo
    if query.isdigit():
        member = guild.get_member(int(query))
        if member:
            print(f"[DEBUG FINDUSER] Encontrado por ID: {member}")
            return str(member.id)

    query_lower = query.lower()
    for member in guild.members:
        if (
            member.name.lower() == query_lower or
            member.display_name.lower() == query_lower
        ):
            print(f"[DEBUG FINDUSER] Encontrado por nombre/display_name: {member}")
            return str(member.id)

    if fallback_to_author:
        print("[DEBUG FINDUSER] No se encontró, devolviendo author.id por fallback.")
        return str(context.message.author.id)

    print("[DEBUG FINDUSER] Usuario no encontrado")
    return ""
