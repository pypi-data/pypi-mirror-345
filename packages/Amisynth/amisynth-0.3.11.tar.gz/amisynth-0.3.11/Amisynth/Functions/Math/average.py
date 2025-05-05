import xfox

@xfox.addfunc(xfox.funcs, name="average")
async def average_of_numbers(first: str, *numbers: str, **kwargs):
    try:
        numbers = [float(first)] + [float(n) for n in numbers]
        return str(sum(numbers) / len(numbers))
    except ValueError:
        return ":x: Invalid number value en `$average[]`"
