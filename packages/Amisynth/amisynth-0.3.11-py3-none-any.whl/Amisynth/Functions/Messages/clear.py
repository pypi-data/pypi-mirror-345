import xfox
import discord
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs, name="clear")
async def clear_func(amount: int, user_id: str = None, remove_pinned: bool = False, *args, **kwargs):
    context = utils.ContextAmisynth()
    channel = await context.get_channel(context.channel_id)

    def check(msg):
        if user_id and str(context.author_id) != user_id:
            return False
        if not remove_pinned and msg.pinned:
            return False
        return True
    
    await channel.purge(limit=amount, check=check)
    return ""
