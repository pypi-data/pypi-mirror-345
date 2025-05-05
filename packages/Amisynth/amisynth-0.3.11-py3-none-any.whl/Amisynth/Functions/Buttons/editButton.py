import xfox
import discord
import Amisynth.utils as utils


@xfox.addfunc(xfox.funcs)
async def editButton(button_id: str, label: str, style: str, disabled="false", emoji=None, message_id=None, *args, **kwargs):
    """Edita o añade un botón en un mensaje ya enviado."""



    context = utils.ContextAmisynth()

    if message_id is None:
        message_id = int(context.message_id)
    
    estilos = {
        "primary": discord.ButtonStyle.primary,
        "secondary": discord.ButtonStyle.secondary,
        "success": discord.ButtonStyle.success,
        "danger": discord.ButtonStyle.danger,
        "link": discord.ButtonStyle.link
    }

    button_style = estilos.get(style, discord.ButtonStyle.primary)

    if disabled in ["true", "false"]:
        disabled = disabled == "true"
    else:
        raise ValueError("Parámetro 'disabled' no válido en $editButton[]")

    custom_id = button_id if button_style != discord.ButtonStyle.link else None
    url = button_id if button_style == discord.ButtonStyle.link else None

    message = await context.get_message_from_id(int(message_id))

    # Obtener vista actual
    view = discord.ui.View() if not message.components else discord.ui.View.from_message(message)

    # Buscar si el botón ya existe (por custom_id o URL)
    for item in view.children:
        if isinstance(item, discord.ui.Button):
            if (item.custom_id == custom_id and custom_id is not None) or (item.url == url and url is not None):
                # Editar propiedades del botón existente
                item.label = label
                item.style = button_style
                item.disabled = disabled
                item.emoji = emoji
                await message.edit(view=view)
                return ""

    # Si no se encontró el botón, agregar uno nuevo
    new_button = discord.ui.Button(
        label=label,
        custom_id=custom_id,
        style=button_style,
        disabled=disabled,
        emoji=emoji,
        url=url
    )
    view.add_item(new_button)

    await message.edit(view=view)
    return ""
