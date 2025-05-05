import xfox

@xfox.addfunc(xfox.funcs, name="power")
async def power_of_number(base: str, exponent: str, **kwargs):
    try:
        base_num = float(base)
        exponent_num = float(exponent)
        return str(base_num ** exponent_num)
    except ValueError:
        return f":x: Invalid number value en `$power[]`"
