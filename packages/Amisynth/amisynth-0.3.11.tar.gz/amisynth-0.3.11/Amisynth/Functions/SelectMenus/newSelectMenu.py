import xfox
import discord
from Amisynth.utils import buttons, menu_options
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def newSelectMenu(menu_id: str, min_val: int, max_val: int, placeholder: str, message_id=None, *args, **kwargs):
    
    context = utils.ContextAmisynth()
    # Obtener las opciones del menú por su ID desde menu_options
    options = menu_options.get(menu_id, [])

    # Crear el menú de selección
    select_menu = discord.ui.Select(
        placeholder=placeholder if placeholder else "Seleccione una opción",
        min_values=min_val,
        max_values=max_val,
        options=options,
        custom_id=menu_id
    )

    if message_id is None:
        buttons.append(select_menu)  # Si no hay mensaje, guardar el botón en la lista
    else:

        message = await context.get_message_from_id(int(message_id))


        # Recuperar o crear una vista nueva
        view = discord.ui.View() if not message.components else discord.ui.View.from_message(message)
        view.add_item(select_menu)  # Agregar el botón a la vista

        await message.edit(view=view)  # Editar el mensaje con la nueva vista
    
    return ""
