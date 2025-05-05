import xfox


@xfox.addfunc(xfox.funcs, name="round")
async def round_number(number: str, decimals: str, **kwargs):
    try:
        num = float(number)
        dec = int(decimals)
        return str(round(num, dec))
    except ValueError:
        return ":x: Invalid number value en `$round[]`"
