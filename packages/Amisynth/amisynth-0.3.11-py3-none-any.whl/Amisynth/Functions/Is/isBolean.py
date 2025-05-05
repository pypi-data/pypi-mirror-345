import xfox

@xfox.addfunc(xfox.funcs)
async def isBoolean(value=None, *args, **kwargs):
    if value is None:
        return "false"

    value_str = str(value).strip().lower()
    
    positive = ["true", "yes", "on", "enable"]
    negative = ["false", "no", "off", "disable"]
    
    return "true" if value_str in positive + negative else "false"
