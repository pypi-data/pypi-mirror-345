import xfox
import Amisynth.utils as utils
from Amisynth.utils import buttons, menu_options
import discord


@xfox.addfunc(xfox.funcs)
async def removeSelectMenus(message_id:int=None, *args, **kwargs):
    """
    Elimina todos los select menus del mensaje especificado.
    - Si no se proporciona message_id, usa el mensaje actual del contexto.
    - Conserva otros componentes (como botones).
    """

    context = utils.ContextAmisynth()

    # Obtener el mensaje
    if message_id is None:
        message_id = context.message_id
    
    message = await context.get_message_from_id(int(message_id))

    # Obtener vista actual
    view = discord.ui.View() if not message.components else discord.ui.View.from_message(message)

    # Filtrar todos los que NO sean select menus
    new_view = discord.ui.View()
    for item in view.children:
        if not isinstance(item, discord.ui.Select):
            new_view.add_item(item)

    await message.edit(view=new_view)
    return ""
