import xfox
import discord
import datetime
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs, name="sendEmbedMessage")
async def etc(channel_id=None, 
              content="",
              title=None, 
              title_url=None, 
              description=None,
              color=None,
              author=None, 
              author_icon=None, 
              author_url=None,
              footer=None, 
              footer_icon=None,
              image=None,
              thumbnail=None,
              timestamp=None,
              retorna_id=None,
              *args, **kwargs):
    
    context = utils.ContextAmisynth()

    # Obtener el canal de envío
    if channel_id is None:
        if not hasattr(context, "channel_id") or context.channel_id is None:
            raise ValueError(":x: No se encontró un canal válido en el contexto.")
        channel = await context.get_channel(int(context.channel_id))
    else:
        channel = await context.get_channel(int(channel_id))

    # Crear embed si hay contenido
    embed = None if all(v is None for v in [title, description, color, author, author_icon, author_url, footer, footer_icon, image, thumbnail, timestamp]) else discord.Embed()

    if embed:
        if title:
            embed.title = title
        if title_url:
            embed.url = title_url
        if description:
            embed.description = description
        if color:
            try:
                color = color.lstrip("#")  # Elimina el '#' si existe
                embed.color = int(color, 16)
            except ValueError:
                print(f"[DEBUG COLOR ERROR] El color '{color}' no es un valor hexadecimal válido.")
        if author:
            embed.set_author(name=author, url=author_url or "", icon_url=author_icon or "")
        if footer:
            embed.set_footer(text=footer, icon_url=footer_icon or "")
        if image:
            embed.set_image(url=image)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if timestamp:
            if timestamp == "true":
                embed.timestamp = datetime.datetime.utcnow()
            elif timestamp != "false":
                print(f"[DEBUG TIMESTAMP ERROR] Argumento no válido: `{timestamp}` en `$sendEmbedMessage[]`, usa true/false.")
                raise ValueError(f":x: Argumento no válido: `{timestamp}` en `$sendEmbedMessage[]`, usa true/false.")

    # Agregar fields desde *args
    args_list = list(args)
    for i in range(0, len(args_list), 3):
        try:
            name = args_list[i]
            value = args_list[i + 1]
            inline = args_list[i + 2] if i + 2 < len(args_list) else "true"
            inline = inline.lower() == "true"
            embed.add_field(name=name, value=value, inline=inline)
        except IndexError:
            missing_parts = ["nombre", "valor", "inline"][len(args_list) % 3:]
            print(f"[DEBUG FIELD ERROR] Faltan: {', '.join(missing_parts)} en `$sendEmbedMessage`.")
            raise ValueError(f":x: Faltan valores en un field: {', '.join(missing_parts)}.")

    # Enviar el mensaje
    message = await channel.send(content, embed=embed)

    # Retornar ID si se requiere
    if retorna_id:
        if retorna_id == "true":
            return message.id
        elif retorna_id != "false":
            print(f"[DEBUG RETORNAR_ID ERROR] Argumento no válido: `{retorna_id}` en `$sendEmbedMessage[]`, usa true/false.")
            raise ValueError(f":x: Argumento no válido: `{retorna_id}` en `$sendEmbedMessage[]`, usa true/false.")

    print("[DEBUG AMYSINTH ERROR] Contacta con Soporte: https://discord.gg/NyGuP3e5")
    return ""
