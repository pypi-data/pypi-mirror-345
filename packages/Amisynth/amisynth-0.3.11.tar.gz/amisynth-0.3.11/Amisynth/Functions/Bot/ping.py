import xfox

@xfox.addfunc(xfox.funcs)
async def ping(*args, **kwargs):
    from Amisynth.utils import bot_inst
    bot = bot_inst
    if not bot:
        raise ValueError(":x: Error: el objeto `bot` no está disponible en `$ping[]`.")
    
    latency_ms = round(bot.latency * 1000)
    return f"{latency_ms}"
