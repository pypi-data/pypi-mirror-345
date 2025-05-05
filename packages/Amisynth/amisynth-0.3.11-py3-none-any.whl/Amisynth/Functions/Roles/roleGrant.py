import xfox
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs, name="roleGrant")
async def role_grant(user_id: int, *roles: str, **kwargs):
    ctx = utils.ContextAmisynth()
    
    for role_data in roles:
        action = role_data[0]  # '+' o '-'
        role_id = int(role_data[1:])  # ID del rol sin el prefijo
        
        if action == '+':
            await ctx.modificar_rol(user_id, role_id, "+")
        elif action == '-':
            await ctx.modificar_rol(user_id, role_id, "-")
    
    return ""
