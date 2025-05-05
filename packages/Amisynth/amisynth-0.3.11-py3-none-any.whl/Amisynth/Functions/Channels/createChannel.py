import xfox
import discord
import Amisynth.utils as utils


@xfox.addfunc(xfox.funcs, name="createChannel")
async def create_channel(name: str, type: str, category_id: int = None, retornar:bool=False, *args, **kwargs):
    contexto = utils.ContextAmisynth()
    guild = contexto.obj_guild  # Obtiene el servidor (guild)

    # Validar el tipo de canal
    valid_types = ["category", "text", "voice", "stage", "forum"]
    if type not in valid_types:
        return f"❌ Tipo de canal inválido. Usa uno de los siguientes: {', '.join(valid_types)}."

    # Buscar la categoría si se proporcionó un ID
    category = None
    if category_id:
        category = discord.utils.get(guild.categories, id=category_id)
        if not category:
            return f"❌ No se encontró la categoría con ID {category_id}."

    try:
        # Crear el canal según el tipo proporcionado
        if type == "text":
            channel = await guild.create_text_channel(name, category=category)
        elif type == "voice":
            channel = await guild.create_voice_channel(name, category=category)
        elif type == "category":
            channel = await guild.create_category_channel(name)
        elif type == "stage":
            channel = await guild.create_stage_channel(name, category=category)
        elif type == "forum":
            channel = await guild.create_forum_channel(name, category=category)

        if retornar is True or retornar is "true" or retornar is "yes":
            return channel.id
        else:
            return ""

    except discord.Forbidden:
        return "❌ No tengo permisos suficientes para crear un canal."

    except discord.HTTPException as e:
        return f"❌ Ocurrió un error al crear el canal: {e}"

    except Exception as e:
        return f"❌ Error inesperado: {e}"
