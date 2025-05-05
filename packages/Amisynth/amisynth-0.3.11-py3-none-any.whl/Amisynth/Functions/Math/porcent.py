import xfox

@xfox.addfunc(xfox.funcs, name="percent")
async def percentage_of_number(number: str, percent: str, **kwargs):
    try:
        num = float(number)
        percent_value = float(percent)
        return str((num * percent_value) / 100)
    except ValueError:
        return ":x: Invalid number value en `$percent[]`"
