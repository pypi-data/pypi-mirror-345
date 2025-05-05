import xfox

@xfox.addfunc(xfox.funcs, name="abs")
async def absolute_value(*args, **kwargs):
    if not args:
       raise ValueError(":x: Falta un número en `$abs[]`")

    try:
        num = float(args[0])
        return str(abs(num))
    except ValueError:
        return ":x: Valor no numérico en `$abs[]`"
