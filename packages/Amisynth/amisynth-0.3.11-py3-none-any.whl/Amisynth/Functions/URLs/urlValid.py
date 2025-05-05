import xfox
import urllib.parse

@xfox.addfunc(xfox.funcs)
async def urlValid(texto: str, *args, **kwargs):
    try:
        parsed = urllib.parse.urlparse(texto)
        if all([parsed.scheme, parsed.netloc]):
            return "True"
        else:
            return "False"
    except Exception:
        return "False"
