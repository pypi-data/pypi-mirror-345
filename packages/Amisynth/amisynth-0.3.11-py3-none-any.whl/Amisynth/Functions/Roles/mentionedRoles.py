import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs, name="mentionedRoles")
async def mentioned_roles(numero: str = None, *args, **kwargs):
    context = utils.ContextAmisynth()
    roles = context.get_role_mentions()  # Obtener menciones de roles

    if not roles:  # Verificar si hay menciones de roles
        print("[DEBUG MENTIONED_ROLES]: No se encontraron menciones de roles")
        return ""

    # Si no se proporciona un índice o selector, devolver el primer rol mencionado
    if numero is None:
        return str(roles[0])  # Retorna la mención del primer rol

    # Si el argumento es un número, obtener la mención en ese índice
    if numero.isdigit():
        indice = int(numero) - 1  # Convertir a índice basado en 1
        if 0 <= indice < len(roles):
            return str(roles[indice])  # Retorna la mención del rol en ese índice
        else:
            print("[DEBUG MENTIONED_ROLES]: No hay suficiente cantidad de roles mencionados.")
            return ""

    # Mayor y menor ID de rol
    if numero == ">":
        return str(max(roles, key=lambda role: role.id))  # Mayor ID
    
    if numero == "<":
        return str(min(roles, key=lambda role: role.id))  # Menor ID
    
    print(f"[DEBUG MENTIONED_ROLES]: Parámetro no válido: {numero}")
    raise ValueError(f":x: No pusiste el parámetro adecuado: `{numero}`, en `$mentionedRoles[{numero}]`")
