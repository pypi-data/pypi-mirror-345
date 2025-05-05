import xfox
from Amisynth.utils import ContextAmisynth

@xfox.addfunc(xfox.funcs)
async def isBanned(user_id=None, *args, **kwargs):
    context = ContextAmisynth()
    guild = context.obj_guild
    if user_id is None or guild is None:
        return "false"
    
    try:
        bans = await guild.bans()
        return "true" if any(str(ban.user.id) == str(user_id) for ban in bans) else "false"
    except:
        return "false"
