
import xfox
from Amisynth.utils import options_slash

@xfox.addfunc(xfox.funcs, name="addSlashOption")
async def addSlashOption(nombre: str=None, description:str="..", tipo: str="Texto", requerido=False, retornar: bool = False, *args, **kwargs):
    """
    Agrega una opción para un slash command.

    - Evita nombres duplicados.
    - Si 'retornar' es True, retorna el nombre.

    Uso:
        $add_option[mensaje;Texto;true]
    """
    if nombre is None:
        raise ValueError(":x: Error en `$addSlashOption[?;..] esta vacio el primer argumento.`")

    # Verificar duplicado

    options_slash.append({
        "name_option": nombre,
        "type": tipo,
        "description": description,
        "required": requerido,
        "choices": []
    })

    if retornar:
        return nombre
    else: 
        return ""