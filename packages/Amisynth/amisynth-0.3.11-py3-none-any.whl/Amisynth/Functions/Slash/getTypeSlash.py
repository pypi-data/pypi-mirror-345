import xfox

@xfox.addfunc(xfox.funcs)
async def getTypeSlash(*args, **kwargs):
    return kwargs["ctx_slash_env"].type