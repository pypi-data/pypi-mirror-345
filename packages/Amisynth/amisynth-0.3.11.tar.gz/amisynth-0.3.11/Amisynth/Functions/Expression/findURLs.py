import xfox
import re

@xfox.addfunc(xfox.funcs)
async def findURLs(text: str, *args, **kwargs):
    # Expresión regular para detectar URLs
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    urls = re.findall(url_pattern, text)
    
    return ', '.join(urls) if urls else ""
