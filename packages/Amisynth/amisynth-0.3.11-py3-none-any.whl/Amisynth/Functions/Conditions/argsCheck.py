import re
import xfox
import Amisynth.utils as utils
@xfox.addfunc(xfox.funcs)
async def argsCheck(check, error_msg, *args, **kwargs):
    """
    Verifica si el número de argumentos proporcionados cumple con la condición especificada.
    Si no se cumple la condición, se lanza un ValueError con un mensaje de error personalizado.

    :param check: Condición para la validación como '>n', '<n', o 'n' (donde n es un número).
    :param error_msg: El mensaje de error que se lanza si la condición no se cumple.
    :param args: Los argumentos proporcionados por el usuario en la lista.
    """
    
    # Obtener los argumentos proporcionados por el usuario

    context = utils.ContextAmisynth()
    user_arguments = context.arguments

    # Extraer la operación y el número del check (ejemplo: '>3', '<5', '3')
    operator = check[0]  # El operador (> o < o =)
    number = int(check[1:])  # El número después del operador

    # Verificar la condición y lanzar el error si no se cumple
    if operator == ">":
        if len(user_arguments) <= number:
            raise ValueError(error_msg)
    elif operator == "<":
        if len(user_arguments) >= number:
            raise ValueError(error_msg)
    elif operator == "=":
        if len(user_arguments) != number:
            raise ValueError(error_msg)
    else:
        raise ValueError(f"Condición no válida en $argsCheck[{check};..]. Usa '>n', '<n' o 'n'.")
    
    return ""  # Retornar vacío si no hubo error
