import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def getLeaderboardValue(var_type=None, var_name=None, sort_type="desc", position=1, return_type=None, *args, **kwargs):
    """Obtiene el valor ordenado de una variable numérica en el leaderboard."""

    if var_type not in ["guilds", "channels", "users", "global", "global_users"]:
        raise ValueError(":x: Error, el `Variable type` debe ser uno de: `guilds, channels, users, global, global_users`.")

    if var_name is None:
        raise ValueError(":x: Error, el `Variable name` está vacío en `$getLeaderboardValue[?;?]`.")

    position = int(position) - 1  # Ajustamos la posición (1-based a 0-based)

    var = utils.VariableManager()
    data = var.data.get(var_type, {})

    leaderboard = []

    # Extraer valores numéricos según el tipo de variable
    if var_type in ["guilds", "channels", "global"]:
        # Datos directos (sin niveles adicionales)
        for key, values in data.items():
            value = values.get(var_name)
            if value is not None and str(value).isdigit():
                leaderboard.append((key, int(value)))

    elif var_type in ["users", "global_users"]:
        # Datos anidados (requieren recorrer niveles)
        for guild_id, users in data.items():
            for user_id, values in users.items():
                value = values.get(var_name)
                if value is not None and str(value).isdigit():
                    leaderboard.append((user_id, int(value)))

    # Verificar si hay datos numéricos
    if not leaderboard:
        return f":x: No hay valores numéricos para `{var_name}` en `{var_type}`."

    # Ordenar el leaderboard
    leaderboard.sort(key=lambda x: x[1], reverse=(sort_type.lower() == "desc"))

    # Verificar que la posición solicitada exista
    if position < 0 or position >= len(leaderboard):
        return f":x: No hay suficientes datos para la posición `{position+1}`."

    # Obtener el resultado en la posición indicada
    key, value = leaderboard[position]

    # Si return_type es None o está vacío, devolvemos "id - valor"
    if return_type is None or return_type == "":
        return f"{key} - {value}"

    # Si el return_type es 'value', devolvemos solo el valor
    elif return_type.lower() == "value":
        return value
    # Si el return_type es 'id', devolvemos solo el id
    elif return_type.lower() == "id":
        return key
    else:
        raise ValueError(f":x: `Return type` inválido. Usa `value` o `id`.")
