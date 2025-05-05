import xfox

@xfox.addfunc(xfox.funcs, name="divide")
async def dividi_number(first: str, *numbers: str, **kwargs):
    try:
        first_num = float(first)
        for num in numbers:
            divisor = float(num)
            if divisor == 0:
                raise ValueError(":x: Division by zero error")
            first_num /= divisor
        return str(first_num)
    except ValueError:
        raise ValueError("Invalid number value")
