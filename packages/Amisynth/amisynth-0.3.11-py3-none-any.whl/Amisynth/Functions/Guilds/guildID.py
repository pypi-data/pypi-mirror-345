import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def guildID(nombre: str = None, *args, **kwargs):
    context = utils.ContextAmisynth()

    if nombre is None:
        return context.guild_id
    else:
        # Buscar el servidor por nombre
        guild = discord.utils.get(utils.bot_inst.guilds, name=nombre)
        if guild is None:
            return None  # O puedes lanzar un error si prefieres
        return guild.id
