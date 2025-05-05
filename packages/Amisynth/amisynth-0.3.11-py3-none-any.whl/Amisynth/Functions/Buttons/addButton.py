import xfox
import discord
from Amisynth.utils import buttons
import Amisynth.utils as utils

# Contador de fila global
row_counter = 0  

@xfox.addfunc(xfox.funcs)
async def addButton(new_row: str, button_id: str, label: str, style: str, disabled="false", emoji=None, message_id=None, *args, **kwargs):
    """Crea múltiples botones interactivos y devuelve una lista de objetos de botones creados."""
    context = utils.ContextAmisynth()
    
    global row_counter  # Para modificar el contador de fila

    # Estilos disponibles
    estilos = {
        "primary": discord.ButtonStyle.primary,
        "secondary": discord.ButtonStyle.secondary,
        "success": discord.ButtonStyle.success,
        "danger": discord.ButtonStyle.danger,
        "link": discord.ButtonStyle.link
    }
    
    button_style = estilos.get(style, discord.ButtonStyle.primary)

    # Validar el parámetro 'disabled'
    if disabled in ["true", "false"]:
        disabled = disabled == "true"
    else:
        raise ValueError("Error en el parámetro $addButton[]")

    # Validar si es un botón de tipo enlace
    custom_id = button_id if button_style != discord.ButtonStyle.link else None
    url = button_id if button_style == discord.ButtonStyle.link else None

    # Manejo de la fila (row)
    if new_row.lower() == "true":
        row_counter += 1
    elif new_row.lower() == "re":
        row_counter = 0  

    button = discord.ui.Button(
        label=label,
        custom_id=custom_id,
        style=button_style,
        emoji=emoji,
        disabled=disabled,
        url=url,
        row=row_counter
    )

    if message_id is None:
        buttons.append(button)  # Si no hay mensaje, guardar el botón en la lista
    else:

        message = await context.get_message_from_id(int(message_id))


        # Recuperar o crear una vista nueva
        view = discord.ui.View() if not message.components else discord.ui.View.from_message(message)
        view.add_item(button)  # Agregar el botón a la vista

        await message.edit(view=view)  # Editar el mensaje con la nueva vista

    return ""
