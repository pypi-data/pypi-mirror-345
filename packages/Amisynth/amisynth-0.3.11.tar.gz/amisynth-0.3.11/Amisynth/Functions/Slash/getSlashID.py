import xfox

@xfox.addfunc(xfox.funcs)
async def getSlashID(*args, **kwargs):
    return kwargs["ctx_slash_env"].id