import discord
from Amisynth.utils import menu_options
# Diccionario para almacenar las opciones de cada menú por su ID
import xfox

@xfox.addfunc(xfox.funcs)
async def addSelectMenuOption(menu_id: str, label: str, value: str, description: str, *args, **kwargs):
    """Agrega una opción al menú de selección, almacenándola en una lista por ID."""
    option = discord.SelectOption(label=label, value=value, description=description)
    
    # Si no existe una lista de opciones para este ID, la crea
    if menu_id not in menu_options:
        menu_options[menu_id] = []
    
    # Agregar la opción al menú correspondiente
    menu_options[menu_id].append(option)
    return ""
