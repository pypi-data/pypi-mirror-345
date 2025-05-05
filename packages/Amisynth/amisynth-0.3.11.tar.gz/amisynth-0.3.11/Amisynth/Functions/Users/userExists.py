import xfox
import discord
import Amisynth.utils as utils


@xfox.addfunc(xfox.funcs)
async def userExists(user_id: int, *args, **kwargs):
    contexto = utils.ContextAmisynth()  # Suponiendo que tienes una forma de obtener el contexto de la guild
    try:
        # Intenta obtener al miembro por su ID
        member = await contexto.obj_guild.fetch_member(user_id)
        return "True"  # Si el miembro existe, devuelve True
    except discord.NotFound:
        return "False"  # Si el miembro no es encontrado, devuelve False
    except discord.HTTPException as e:
        raise ValueError(f":x: Error al buscar usuario: {str(e)}")
