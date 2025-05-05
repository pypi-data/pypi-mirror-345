import xfox

@xfox.addfunc(xfox.funcs, name="multi")
async def multiply_numbers(first: str, *numbers: str, **kwargs):
    try:
        result = float(first)
    except ValueError:
        raise ValueError(f":x: Invalid number value: '{first}' en `$multi[]`")

    for n in numbers:
        try:
            result *= float(n)
        except ValueError:
            raise ValueError(f":x: Invalid number value: '{n}' en `$multi[]`")

    return str(int(result)) if result.is_integer() else str(result)
