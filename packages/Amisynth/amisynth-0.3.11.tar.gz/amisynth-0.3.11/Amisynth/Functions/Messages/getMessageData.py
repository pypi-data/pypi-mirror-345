import xfox
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def getMessageData(message_id=None, data_type="message", prop="content", embed_index=1, *args, **kwargs):
    context = utils.ContextAmisynth()

    if message_id is None:
        raise ValueError(":x: El argumento `message_id` está vacío en `$getMessageData[]`.")

    message = await context.get_message_from_id(message_id=message_id)
    if message is None:
        raise ValueError(":x: No se encontró ningún mensaje con el ID proporcionado.")

    if data_type.lower() == "message":
        if prop == "content":
            return message.content
        elif prop == "authorID":
            return str(message.author.id)
        elif prop == "username":
            return message.author.name
        elif prop == "avatar":
            return message.author.avatar.url if message.author.avatar else None
        else:
            raise ValueError(f":x: Propiedad de mensaje no válida: `{prop}`")
        
    elif data_type.lower() == "embed":
        # Ajustar el índice para comenzar desde 1
        if int(embed_index) < 1:
            raise ValueError(":x: El índice de embed debe ser mayor o igual a 1.")

        embeds = message.embeds
        if len(embeds) < int(embed_index):
            raise ValueError(":x: Índice de embed inválido o no hay suficientes embeds en el mensaje, error en `$getMessageData[]`.")

        embed = embeds[int(embed_index) - 1]  # Convertir el índice de 1 a 0

        if prop == "title":
            return embed.title
        elif prop == "description":
            return embed.description
        elif prop == "footer":
            return embed.footer.text if embed.footer else None
        elif prop == "color":
            return str(embed.color)
        elif prop == "timestamp":
            return str(embed.timestamp)
        elif prop == "image":
            return embed.image.url if embed.image else None
        else:
            raise ValueError(f":x: Propiedad de embed no válida: `{prop}` en `$getMessageData[{prop};..]`!")
    
    else:
        raise ValueError(f":x: Tipo de dato no válido: `{data_type}` en `$getMessageData[..;{data_type};..]`. Usa `message` o `embed`.")
