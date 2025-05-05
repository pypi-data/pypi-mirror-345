import xfox

@xfox.addfunc(xfox.funcs)
async def getCreateSlash(*args, **kwargs):
    return kwargs["ctx_slash_env"].created_at