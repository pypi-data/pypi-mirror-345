import xfox
import Amisynth.utils as utils
import re

@xfox.addfunc(xfox.funcs)
async def findRole(query: str, *args, **kwargs):
    context = utils.ContextAmisynth()
    guild = context.obj_guild

    if guild is None:
        print("[DEBUG FINDROLE] No se puede buscar fuera de un servidor.")
        raise ValueError(":x: No se puede buscar fuera de un servidor.")

    query = query.strip()

    # 🟦 Buscar por mención de rol <@&123456789012345678>
    mention_match = re.match(r"<@&(\d+)>", query)
    if mention_match:
        role_id = int(mention_match.group(1))
        role = guild.get_role(role_id)
        if role:
            print(f"[DEBUG FINDROLE] Encontrado por mención: {role}")
            return str(role.id)

    # 🟩 Buscar por ID
    if query.isdigit():
        role = guild.get_role(int(query))
        if role:
            print(f"[DEBUG FINDROLE] Encontrado por ID: {role}")
            return str(role.id)

    # 🟨 Buscar por nombre
    query_lower = query.lower()
    for role in guild.roles:
        if role.name.lower() == query_lower:
            print(f"[DEBUG FINDROLE] Encontrado por nombre: {role}")
            return str(role.id)

    print("[DEBUG FINDROLE] Rol no encontrado")
    return ""
