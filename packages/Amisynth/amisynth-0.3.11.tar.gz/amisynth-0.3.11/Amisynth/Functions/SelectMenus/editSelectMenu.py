import xfox
import Amisynth.utils as utils
from Amisynth.utils import menu_options
import discord

@xfox.addfunc(xfox.funcs)
async def editSelectMenu(menu_id: str, min_values: int, max_values: int, placeholder: str = None, message_id: str = None, *args, **kwargs):
    from discord.ui import View, Select

    context = utils.ContextAmisynth()

    # Obtener opciones existentes o inicializar
    options = menu_options.get(menu_id, [])

    # Crear el nuevo menú
    select_menu = Select(
        placeholder=placeholder or "Seleccione una opción",
        min_values=int(min_values),
        max_values=int(max_values),
        options=options,
        custom_id=menu_id
    )

    # Si se proporcionó un mensaje, lo actualizamos
    if message_id:
        message = await context.get_message_from_id(int(message_id))
        view = View() if not message.components else View.from_message(message)

        # Eliminar cualquier menú existente con el mismo ID
        view.children = [child for child in view.children if not (isinstance(child, Select) and child.custom_id == menu_id)]

        view.add_item(select_menu)
        await message.edit(view=view)

    print(F"[DEBUG EDITSELECTMENU] Menú '{menu_id}' actualizado correctamente")
    return f""
