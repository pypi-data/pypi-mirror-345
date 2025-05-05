import xfox

@xfox.addfunc(xfox.funcs)
async def editMessageBefore(*args, **kwargs):
    if "ctx_message_edit_env" in kwargs:
        before = kwargs["ctx_message_edit_env"][0]
        return before.content
    return ""