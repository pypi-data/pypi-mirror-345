import xfox
import discord
import Amisynth.utils as utils


@xfox.addfunc(xfox.funcs)
async def removeButtons(message_id:int=None, *args, **kwargs):
    """
    Elimina todos los botones del mensaje especificado.
    - Si no se proporciona message_id, usa el mensaje actual del contexto.
    - Conserva otros componentes (como select menus).
    """

    context = utils.ContextAmisynth()

    # Obtener el mensaje
    if message_id is None:
        message_id = context.message_id

        
    message  = await context.get_message_from_id(int(message_id))

    # Obtener vista actual
    view = discord.ui.View() if not message.components else discord.ui.View.from_message(message)

    # Filtrar todos los que NO sean botones
    new_view = discord.ui.View()
    for item in view.children:
        if not isinstance(item, discord.ui.Button):
            new_view.add_item(item)

    await message.edit(view=new_view)
    return ""
