import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def setVar(nombre=None, value=None, user_id=None, *args, **kwargs):
    """Establece una variable, ya sea global de usuario o general, según si se proporciona un user_id."""
    context = utils.ContextAmisynth()

    if nombre is None or value is None:
        raise ValueError(":x: Error, el nombre o el valor están vacíos en la función `$setVar[?;?]`.")
    
    var = utils.VariableManager()

    if user_id is not None:
        # Si se proporciona un user_id, la variable es global de usuario
        var.set_value("global_user", key=nombre, value=value, user_id=user_id)
        print("[DEBUG SETVAR] Variable `{nombre}` establecida con éxito como global de usuario.")
        return ""

    # Si no se proporciona un user_id, la variable es general
    var.set_value("global", key=nombre, value=value)
    print("[DEBUG SETVAR] Variable `{nombre}` establecida con éxito como global.")
    return ""