import discord
from Amisynth.utils import menu_options
# Diccionario para almacenar las opciones de cada menú por su ID
import xfox

@xfox.addfunc(xfox.funcs)
async def getSelectMenuID(*args, **kwargs):
    """Agrega una opción al menú de selección, almacenándola en una lista por ID."""
    if "ctx_interaction_env" in kwargs:
        interaction = kwargs["ctx_interaction_env"]
        menu_id = interaction.data['custom_id']
        return menu_id
    return ""
