import xfox
import urllib.parse

@xfox.addfunc(xfox.funcs)
async def url(modo: str, texto: str, *args, **kwargs):
    if modo.lower() == "encode":
        return urllib.parse.quote_plus(texto)
    elif modo.lower() == "decode":
        return urllib.parse.unquote_plus(texto)
    else:
        raise ValueError(f"Modo inválido: '{modo}'. Usa 'encode' o 'decode', en `$url[{modo};..]`")
