import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def getLeaderboardPosition(var_type=None, var_name=None, sort_type="desc", user_id=None, *args, **kwargs):
    """Devuelve la posición de un usuario en el leaderboard basado en una variable numérica."""

    if var_type not in ["guilds", "channels", "users", "global", "global_users"]:
        raise ValueError(":x: Error, el `Variable type` debe ser uno de: `guilds, channels, users, global, global_users`.")

    if var_name is None:
        raise ValueError(":x: Error, el `Variable name` está vacío en `$getLeaderboardPosition[?;?]`.")

    if user_id is None:
        context = utils.ContextAmisynth()
        user_id = context.author_id  # Usa la ID del usuario actual si no se proporciona una

    var = utils.VariableManager()
    data = var.data.get(var_type, {})

    leaderboard = []

    # Extraer valores numéricos según el tipo de variable
    if var_type in ["guilds", "channels", "global"]:
        for key, values in data.items():
            value = values.get(var_name)
            if value is not None and str(value).isdigit():
                leaderboard.append((key, int(value)))

    elif var_type in ["users", "global_users"]:
        for guild_id, users in data.items():
            for u_id, values in users.items():
                value = values.get(var_name)
                if value is not None and str(value).isdigit():
                    leaderboard.append((u_id, int(value)))

    # Verificar si hay datos numéricos
    if not leaderboard:

        raise ValueError(f":x: No hay valores numéricos para `{var_name}` en `{var_type}`.")

    # Ordenar el leaderboard
    leaderboard.sort(key=lambda x: x[1], reverse=(sort_type.lower() == "desc"))

    # Buscar la posición del usuario
    for index, (key, _) in enumerate(leaderboard, start=1):
        if str(key) == str(user_id):
            return index  # Retorna la posición 1-based

    raise ValueError(f":x: El usuario `{user_id}` no tiene un valor registrado para `{var_name}` en `{var_type}`.")
