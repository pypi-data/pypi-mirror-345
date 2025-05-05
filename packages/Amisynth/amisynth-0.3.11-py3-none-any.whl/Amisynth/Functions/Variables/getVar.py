import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def getVar(nombre:str=None, user_id:str=None, *args, **kwargs):
    """Obtiene una variable, ya sea global de usuario o general, según si se proporciona un user_id."""
    context = utils.ContextAmisynth()
    
    if nombre is None:
        raise ValueError(f":x: Error, el nombre está vacío en la función `$getVar[?]`.")
    
    var = utils.VariableManager()

    if user_id is not None:
        # Si se proporciona un user_id, la variable es global de usuario
        value = var.get_value("global_user", key=nombre, user_id=user_id)
        
        if value is None:
            raise ValueError(f":x: No se encontró la variable `{nombre}` para el usuario especificado.")
        return value

    # Si no se proporciona un user_id, la variable es global
    value = var.get_value("global", key=nombre)
    
    if value is None:
        raise ValueError(f":x: No se encontró la variable `{nombre}` de forma global.")
    
    return value