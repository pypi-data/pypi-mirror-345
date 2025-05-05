import math
import xfox

@xfox.addfunc(xfox.funcs, name="sqrt")
async def square_root(number: str, *args, **kwargs):
    try:
        num = float(number)
        if num < 0:
            raise ValueError(":x: No se puede calcular la raíz cuadrada de un número negativo.")
        return str(math.sqrt(num))
    except ValueError:
        return f":x: Invalid number value: '{number}' en `$sqrt[]`"
