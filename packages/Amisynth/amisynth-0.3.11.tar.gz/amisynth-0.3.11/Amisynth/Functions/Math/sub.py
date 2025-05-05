
import xfox

@xfox.addfunc(xfox.funcs, name="sub")
async def subtract_numbers(first: str, *numbers: str, **kwargs):
    try:
        result = float(first)
    except ValueError:
        raise ValueError(f":x: Invalid number value: '{first}' en `$sub[]`")

    for n in numbers:
        try:
            result -= float(n)
        except ValueError:
            raise ValueError(f":x: Invalid number value: '{n}' en `$sub[]`")

    return str(int(result)) if result.is_integer() else str(result)
