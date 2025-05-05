import xfox
import discord
import Amisynth.utils as utils
import traceback

@xfox.addfunc(xfox.funcs)
async def username(id: str = None, *args, **kwargs):
    context = utils.ContextAmisynth()
    

    if id is None:
            username = context.username
    else:
            username = context.get_username_by_id(int(id))  # Asegúrate de usar `await` si la función es asincrónica.

    if username is None:
            raise ValueError("Usuario no encontrado.")  # Lanza una excepción si el usuario no se encuentra


    return username

