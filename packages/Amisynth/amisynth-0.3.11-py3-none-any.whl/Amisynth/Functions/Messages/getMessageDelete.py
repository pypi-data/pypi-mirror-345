import xfox

@xfox.addfunc(xfox.funcs)
async def getMessageDelete(*args, **kwargs):

    if "ctx_message_delete_env" in kwargs:
        message = kwargs["ctx_message_delete_env"]
        return message.content
    return ""