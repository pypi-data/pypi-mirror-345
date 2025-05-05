import xfox
import re

@xfox.addfunc(xfox.funcs)
async def findNumbers(text: str, *args, **kwargs):
    # Busca todos los números en el texto
    numbers = re.findall(r"\d+", text)
    
    return ', '.join(numbers) if numbers else ""
