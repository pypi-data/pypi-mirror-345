import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def unban(user_id: int, *args, **kwargs):
    contexto = utils.ContextAmisynth()

    try:
        # Validación del ID
        if not isinstance(user_id, int):
            raise ValueError("El ID debe ser un número entero válido.")

        # Intentar obtener el usuario (por ID) en la lista de baneos
        banned_users = await contexto.obj_guild.bans()
        member_to_unban = discord.utils.get(banned_users, user__id=user_id)

        if member_to_unban is None:
            raise discord.NotFound("No se encontró al usuario en la lista de baneos.")

        # Unbanear al usuario
        await contexto.obj_guild.unban(member_to_unban.user)

        return f"✅ Usuario `{member_to_unban.user}` ha sido desbaneado."

    except ValueError as ve:
        return f"❌ Error de valor: {ve}"

    except discord.NotFound:
        return "❌ El usuario no está baneado en este servidor."

    except discord.Forbidden:
        return "❌ No tengo permisos suficientes para desbanear al usuario."

    except discord.HTTPException as e:
        return f"❌ Error de red al desbanear: {e}"

    except Exception as e:
        return f"❌ Ocurrió un error inesperado: {e}"
