import xfox
from Amisynth.utils import ContextAmisynth
@xfox.addfunc(xfox.funcs)
async def isAdmin(user_id=None, *args, **kwargs):
    context = ContextAmisynth()
    guild = context.obj_guild
    if user_id is None or guild is None:
        return "false"
    
    member = await guild.fetch_member(int(user_id))
    return "true" if member.guild_permissions.administrator else "false"
