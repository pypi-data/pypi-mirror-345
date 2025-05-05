import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def userRoles(separator: str = None, option: str = "names", user_id: int = None, *args, **kwargs):
    contexto = utils.ContextAmisynth()

    # Asigna el user_id si no se proporciona
    resolved_user_id = user_id if user_id is not None else contexto.author_id

    # Obtiene el miembro del guild
    member = await contexto.obj_guild.fetch_member(resolved_user_id)

    # Establece un separador por defecto si no se proporciona
    if separator is None:
        separator = "\n"

    # Filtra los roles, excluyendo @everyone
    roles = [rol for rol in member.roles if rol.name != "@everyone"]

    # Devuelve los datos según el tipo de opción
    if option == "names":
        return separator.join(rol.name for rol in roles)
    elif option == "ids":
        return separator.join(str(rol.id) for rol in roles)
    else:
        raise ValueError(f"Opción inválida: '{option}'. Usa 'names' o 'ids'.")
