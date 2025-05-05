import xfox
import discord
import Amisynth.utils as utils


@xfox.addfunc(xfox.funcs)
async def ban(user_id: int, reason="Sin razón específica", *args, **kwargs):
    contexto = utils.ContextAmisynth()

    try:
        # Validación del ID
        if not isinstance(user_id, int):
            raise ValueError("El ID debe ser un número entero válido.")

        # Buscar al miembro
        member = await contexto.obj_guild.fetch_member(user_id)

        if member is None:
            raise discord.NotFound("No se encontró al usuario en el servidor.")

        # Banear al miembro
        await member.ban(reason=reason)

        return f"✅ Usuario `{member}` ha sido baneado. Razón: `{reason}`"

    except ValueError as ve:
        return f"❌ Error de valor: {ve}"

    except discord.NotFound:
        return "❌ No se encontró al usuario en este servidor."

    except discord.Forbidden:
        return "❌ No tengo permisos suficientes para banear al usuario."

    except discord.HTTPException as e:
        return f"❌ Error de red al banear: {e}"

    except Exception as e:
        return f"❌ Ocurrió un error inesperado: {e}"
