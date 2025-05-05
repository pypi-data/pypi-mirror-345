import xfox
from Amisynth.utils import ContextAmisynth

@xfox.addfunc(xfox.funcs)
async def isHoisted(user_id=None, *args, **kwargs):
    context = ContextAmisynth()
    guild = context.obj_guild
    if user_id is None:
        return "false"
    
    member = await guild.fetch_member(int(user_id))
    for role in member.roles:
        if role.hoist:
            return "true"
    return "false"
