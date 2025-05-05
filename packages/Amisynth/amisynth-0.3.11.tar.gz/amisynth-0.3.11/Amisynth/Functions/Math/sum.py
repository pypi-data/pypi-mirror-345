import xfox

@xfox.addfunc(xfox.funcs, name="sum")
async def sum_number(first: str, *numbers: str, **kwargs):
    try:
        total = sum(map(float, (first,) + numbers))
        return str(int(total))
    except ValueError:
        return "Invalid number value"
