import xfox
import Amisynth.utils as utils
from Amisynth.utils import buttons, menu_options
import discord

@xfox.addfunc(xfox.funcs)
async def editSelectMenuOption(
    menu_id: str, 
    label: str, 
    value: str, 
    description: str, 
    default: str = "False", 
    emoji: str = None, 
    message_id: str = None, 
    *args, **kwargs
):
    from discord import SelectOption
    context = utils.ContextAmisynth()

    default = default.lower() == "true"  # Convertir a booleano
    options = menu_options.get(menu_id, [])

    # Buscar opción por 'value'
    updated = False
    for i, option in enumerate(options):
        if option.value == value:
            options[i] = SelectOption(
                label=label,
                value=value,
                description=description,
                default=default,
                emoji=emoji
            )
            updated = True
            break

    if not updated:
        # Si no existe, agregar la nueva opción
        options.append(SelectOption(
            label=label,
            value=value,
            description=description,
            default=default,
            emoji=emoji
        ))

    # Actualizar el menú guardado
    menu_options[menu_id] = options

    if message_id:
        message = await context.get_message_from_id(int(message_id))

        view = discord.ui.View() if not message.components else discord.ui.View.from_message(message)
        
        # Eliminar cualquier menú con el mismo ID
        view.children = [child for child in view.children if not (isinstance(child, discord.ui.Select) and child.custom_id == menu_id)]

        # Crear nuevo menú actualizado
        select_menu = discord.ui.Select(
            placeholder="Seleccione una opción",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=menu_id
        )
        view.add_item(select_menu)

        await message.edit(view=view)

    return ""
