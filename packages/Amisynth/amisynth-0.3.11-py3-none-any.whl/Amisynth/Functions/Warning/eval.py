import xfox
import discord
import Amisynth.utils as utils
from Amisynth.utils import utils as utils_func
from Amisynth.utils import buttons as but, embeds as emb

@xfox.addfunc(xfox.funcs, name="eval")
async def eval_command(code=None, *args, **kwargs):
    # ✅ Verificación para evitar que 'code' sea None
    if code is None:
        return ""

    context = utils.ContextAmisynth()
    channel = context.obj_channel

    try:
        code = await xfox.parse(code, del_empty_lines=True)

    except ValueError as e:
        return f"{e}"


    texto = code

    botones, embeds, files = await utils_func()

    view = discord.ui.View()
    if botones:
        for boton in botones:
            view.add_item(boton)
    print(f"[DEBUG EVAL - CHANNEL] Canal ejeciutado: {channel.name}")
    await channel.send(
        content=texto if texto else "",
        view=view,
        embeds=embeds if embeds else [],
        files=files
    )
    from Amisynth.utils import clear_data
    await clear_data()

    return ""

