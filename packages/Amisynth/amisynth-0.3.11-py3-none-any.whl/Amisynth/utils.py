import discord
import re
from discord import app_commands
from discord.ext import commands
import json

# Lista global de embeds
embeds = []  # Esta lista se puede actualizar desde otros archivos, como 'image.py' o 'thumbnail.py'

buttons = []  # Si también necesitas manejar botones, puedes añadir la lógica aquí

modales = []

modals_activate = False

ephemeral = False

options_slash = []

canvas_storage = {}

json_storage = {}

files = []

menu_options = {}

message_id = None

async def set_message_bot(msg):
    message_id = msg

bot_inst = None


# utils.py

# Variable global para almacenar las cabeceras y los datos JSON
http_data = {
    "headers": {},
    "json": {}
}

# Variable para almacenar la respuesta HTTP
http_response = ""

http_status = None

async def utils():
    nuevos_embeds = []  # Usamos una lista nueva para los embeds procesados

    # Iterar sobre cada item en la lista de embeds

    for item in embeds:
        embed = discord.Embed()  # Crear el embed sin título y descripción por defecto

        if "color" in item and item["color"]:
            embed.color = item["color"]

        # Verificar si el título está presente y agregarlo
        if 'title' in item and item['title']:
            embed.title = item['title']

        if "title_url" in item and item["title_url"]:
            embed.url = ensure_double_slash(item["title_url"] or "")

        # Verificar si la descripción está presente y agregarla
        if 'description' in item and item['description']:
            embed.description = item['description']

        # Verificar si hay imagen y añadirla, asegurando que la URL esté bien formada
        if "image" in item and item["image"]:
            n = ensure_double_slash(item["image"])
            embed.set_image(url=n)

        if "thumbnail_icon" in item and item["thumbnail_icon"]:
            n = ensure_double_slash(item["thumbnail_icon"])
            embed.set_thumbnail(url=n)

        if "footer" in item and item["footer"]:
            icon = item["footer_icon"] if "footer_icon" in item and item["footer_icon"] else None
            embed.set_footer(text=item["footer"], icon_url=icon)

        if "timestamp" in item and item["timestamp"]:
            from datetime import datetime
            embed.timestamp = datetime.utcnow()
        

        author_name = item.get("author")
        author_icon = ensure_double_slash(item.get("author_icon", ""))
        author_url = ensure_double_slash(item.get("author_url", ""))

        if author_name or author_icon or author_url:
            embed.set_author(name=author_name or "", icon_url=author_icon, url=author_url)
        # Agregar el embed procesado a la lista

        if "fields" in item and isinstance(item["fields"], list):
            for field in item["fields"]:
                embed.add_field(
                    name=field.get("name"),
                    value=field.get("value"),
                    inline=field.get("inline"))


        nuevos_embeds.append(embed)

    # Retornar los nuevos embeds procesados y los botones
    return buttons, nuevos_embeds, files



def ensure_double_slash(text: str) -> str:
    return re.sub(r"https:(?!//)", "https://", text)



from discord import Interaction, Message, Member, TextChannel, RawReactionActionEvent
from discord.ext import commands
from discord.utils import get


class ContextAmisynth:
    _instances = {}  
    _last_ctx = None  

    def __new__(cls, ctx=None):
        
        if ctx:
            cls._last_ctx = ctx  
            ctx_type = type(ctx).__name__
            if ctx_type not in cls._instances:
                
                cls._instances[ctx_type] = super().__new__(cls)
            return cls._instances[ctx_type]
        
        return cls._instances.get(type(cls._last_ctx).__name__, super().__new__(cls))  

    def __init__(self, ctx=None):
        
        if ctx:
            self.set_context(ctx)

    def set_context(self, ctx):
        """Establece o cambia el contexto actual."""
        
        self.ctx = ctx
        ContextAmisynth._last_ctx = ctx 
        ContextAmisynth._instances[type(ctx).__name__] = self 


        if isinstance(ctx, commands.Context):
            self.author_id = ctx.author.id
            self.guild_id = ctx.guild.id if ctx.guild else None
            self.channel_id = ctx.channel.id
            self.message_id = ctx.message.id
            self.username = ctx.author.name
            self.arguments = ctx.message.content.split()[1:]
            self.user_roles = [role.id for role in ctx.author.roles if role.name != "@everyone"]
            self.message_content = ctx.message.content[1:]
            self.display_name = ctx.author.display_name

            self.obj_channel = ctx.channel
            self.obj_guild = ctx.guild
            self.obj_message = ctx.message
 
        elif isinstance(ctx, discord.Interaction):
            self.author_id = ctx.user.id
            self.guild_id = ctx.guild.id if ctx.guild else None
            self.channel_id = ctx.channel.id if ctx.channel else None
            self.message_id = ctx.message.id if ctx.message else None
            self.username = ctx.user.name
            self.custom_id = ctx.data.get("custom_id")
            self.slash_options = ctx.data.get("options")
            self.user_roles = [role.id for role in ctx.user.roles if role.name != "@everyone"]
            self.display_name = ctx.user.display_name
            
            self.obj_channel = ctx.channel
            self.obj_member = ctx.user

        elif isinstance(ctx, Message):
            self.author_id = ctx.author.id
            self.guild_id = ctx.guild.id if ctx.guild else None
            self.channel_id = ctx.channel.id
            self.message_id = ctx.id
            self.username = ctx.author.name
            self.arguments = ctx.content.split()
            self.user_roles = [role.id for role in ctx.author.roles if role.name != "@everyone"]
            self.message_content = ctx.content
            self.display_name = ctx.author.display_name
            self.obj_channel = ctx.channel
            self.obj_channel = ctx.author

        elif isinstance(ctx, Member):
            self.author_id = ctx.id  # ID del usuario
            self.guild_id = ctx.guild.id if ctx.guild else None  # ID del servidor (si está en uno)
            self.username = ctx.name  # Nombre de usuario
            self.display_name = ctx.display_name  # Nombre mostrado en el servidor
            self.obj_member = ctx

        elif isinstance(ctx, discord.TextChannel):
            self.channel_id = ctx.id
            self.guild_id = ctx.guild.id if ctx.guild else None
            self.channel_name = ctx.name
            self.obj_channel = ctx

            
        elif isinstance(ctx, RawReactionActionEvent):
            self.author_id = ctx.user_id
            self.username = self.get_username_by_id(ctx.user_id)
            self.guild_id = ctx.guild_id  
            self.channel_id = ctx.channel_id  
            self.message_id = ctx.message_id




            self.emoji_name = ctx.emoji.name  # Nombre del emoji
            self.emoji_id = ctx.emoji.id  # ID del emoji, si es un emoji personalizado
            self.is_custom = ctx.emoji.is_custom_emoji()  # Verificar si es un emoji personalizado

            


        elif isinstance(ctx, discord.Thread):
   
            self.obj_guild = ctx.guild
    
 
            self.channel_id = ctx.parent.id
            self.obj_channel = ctx.parent

    
            self.thread_id = ctx.id
            self.thread_name = ctx.name
            self.thread_owner = ctx.owner.id if ctx.owner else ctx.owner_id  # fallback
            self.guild_id = ctx.guild.id

  
            self.archived = ctx.archived
            self.locked = ctx.locked
            self.invitable = ctx.invitable  # Solo relevante en hilos privados
            self.auto_archive_duration = ctx.auto_archive_duration
            self.created_at = ctx.created_at
            self.archived_at = ctx.archive_timestamp
            self.slowmode_delay = ctx.slowmode_delay
            self.message_count = ctx.message_count
            self.member_count = ctx.member_count
            self.last_message_id = ctx.last_message_id


            self.thread_type = ctx.type.name

   
            self.bot_member_info = ctx.me  #
    
   
            self.parent_name = ctx.parent.name


        else:
            self.author_id = None
            self.guild_id = None
            self.channel_id = None
            self.message_id = None
    
    def get_user_id_by_username(self, username: str):
        """Obtiene el ID de un usuario a partir de su nombre de usuario dentro del contexto."""


        guild = bot_inst.get_guild(self.guild_id)

        if guild:
            member = get(guild.members, name=username)  # Buscar por nombre de usuario
            if member:
                return member.id

        return None  # No se encontró el usuario
    

    def get_username_by_id(self, user_id: int):
        """Obtiene el nombre de usuario de un usuario a partir de su ID en todos los servidores."""
        for guild in bot_inst.guilds:  # Iterar sobre todos los servidores en los que el bot está
            member = guild.get_member(user_id)  # Buscar por ID de usuario en el servidor actual
            if member:
                return member.name  # Retornar el nombre de usuario si se encuentra

        return None  # No se encontró el usuario en ninguno de los servidores
    



    def get_channel_id_by_name(self, channel_name: str):
        """Obtiene el ID de un canal a partir de su nombre dentro del contexto."""
        guild = bot_inst.get_guild(self.guild_id)

        if guild:
            channel = get(guild.channels, name=channel_name)  # Buscar por nombre del canal
            if channel:
                return channel.id  # Retorna el ID del canal encontrado

        return None  # No se encontró el canal

    
    def get_nickname_by_id(self, user_id: int):
        """Obtiene el nombre de usuario a partir de un ID dentro del contexto del servidor."""

        guild = bot_inst.get_guild(self.guild_id)
        if guild:
            member = get(guild.members, id=user_id)  # Buscar por ID de usuario
            if member:
                return member.display_name  # Retorna el nombre de usuario
    
        return None  # Usuario no encontrado
    

    
    def get_mentions(self):
        """Devuelve una lista de IDs de usuarios mencionados en el mensaje actual del contexto."""
        if isinstance(self.ctx, commands.Context):
            return [user.id for user in self.ctx.message.mentions]  # Extrae IDs de menciones

        elif isinstance(self.ctx, Interaction) and self.ctx.message:
            return [user.id for user in self.ctx.message.mentions]  # Si Interaction tiene un mensaje

        elif isinstance(self.ctx, Message):
            return [user.id for user in self.ctx.mentions]  # Extrae menciones en mensajes directos

        return []
    
    def get_role_mentions(self):
        """Devuelve una lista de IDs de roles mencionados en el mensaje actual del contexto."""
        if isinstance(self.ctx, commands.Context):
            return [role.id for role in self.ctx.message.role_mentions]  # Extrae IDs de roles mencionados

        elif isinstance(self.ctx, Interaction) and self.ctx.message:
            return [role.id for role in self.ctx.message.role_mentions]  # Si Interaction tiene un mensaje

        elif isinstance(self.ctx, Message):
            return [role.id for role in self.ctx.role_mentions]  # Extrae menciones de roles en mensajes directos

        return []
    
    def get_channel_mentions(self):
        """Devuelve una lista de IDs de canales mencionados en el mensaje actual del contexto."""
        if isinstance(self.ctx, commands.Context):
            return [channel.id for channel in self.ctx.message.channel_mentions]  # Extrae IDs de canales mencionados

        elif isinstance(self.ctx, Interaction) and self.ctx.message:
            return [channel.id for channel in self.ctx.message.channel_mentions]  # Si Interaction tiene un mensaje

        elif isinstance(self.ctx, Message):
            return [channel.id for channel in self.ctx.channel_mentions]  # Extrae menciones de canales en mensajes directos

        return []
    

    def get_text_channels_name(self, guild_id: int):
        """Devuelve una lista de nombres de los canales de texto de un servidor, excluyendo las categorías."""
        guild = self.ctx.guild  # Obtiene el servidor desde el contexto
        if not guild or guild.id != guild_id:
             return []  # Si el servidor no coincide, devuelve una lista vacía

        return [channel.name for channel in guild.channels if not isinstance(channel, discord.CategoryChannel)]
    


    def get_text_channels_ids(self, guild_id: int):
        """Devuelve una lista de nombres de los canales de un servidor, excluyendo las categorías."""
        guild = self.ctx.guild  # Obtiene el servidor desde el contexto
        if not guild or guild.id != guild_id:
            return []  # Si el servidor no coincide, devuelve una lista vacía

        return [str(channel.id) for channel in guild.channels if not isinstance(channel, discord.CategoryChannel)]
    

    def get_categorys_names(self, guild_id: int):
        """Devuelve una lista de nombres de las categorías de un servidor."""
        guild = self.ctx.guild  # Obtiene el servidor desde el contexto
        if not guild or guild.id != guild_id:
            return []  # Si el servidor no coincide, devuelve una lista vacía

        return [category.name for category in guild.channels if isinstance(category, discord.CategoryChannel)]

    def get_categorys_ids(self, guild_id: int):
        """Devuelve una lista de IDs de las categorías de un servidor."""
        guild = self.ctx.guild  # Obtiene el servidor desde el contexto
        if not guild or guild.id != guild_id:
            return []  # Si el servidor no coincide, devuelve una lista vacía

        return [str(category.id) for category in guild.channels if isinstance(category, discord.CategoryChannel)]


    
    async def get_message_from_id(self, message_id: int):
        """Busca un mensaje en cualquier canal del servidor actual."""
    
        if not hasattr(self, "ctx") or not self.ctx.guild:
            return None  # Asegurarse de que haya contexto y sea un servidor válido
    
        for channel in self.ctx.guild.text_channels:  # Iterar sobre los canales de texto
            try:
                message = await channel.fetch_message(message_id)  # Intentar obtener el mensaje
                return message  # Si se encuentra, retornarlo
            except discord.NotFound:
                continue  # Si no se encuentra, seguir con el siguiente canal
            except discord.Forbidden:
                print(f"No tengo permisos para leer {channel.name}")  # Diagnóstico de permisos
                continue
            except discord.HTTPException as e:
                print(f"Error HTTP en {channel.name}: {e}")
                continue

        return None  # Si no se encuentra en ningún canal, devolver None


    
    async def get_channel(self, channel_id:int=None):
        """Obtiene el objeto del canal dado un ID o el canal almacenado en el contexto."""
        if not hasattr(self, "ctx"):
            return None  # No hay contexto disponible

        client = self.ctx._state._get_client()  # Obtiene el cliente (bot)
        channel_id = channel_id or getattr(self, "channel_id", None)  # Usa el ID dado o el almacenado en el contexto

        if channel_id:
            return client.get_channel(channel_id)  # Retorna el objeto del canal si está en caché

        return None  # Retorna None si no se encuentra el canal
    
    async def modificar_rol(self, user_id: int, role_id: int, action: str):
        """
        Modifica el rol de un usuario en el servidor.

        :param user_id: ID del usuario.
        :param role_id: ID del rol.
        :param action: '+' para añadir el rol, '-' para quitarlo.
        """
        if not self.ctx:
            return
    
        guild = self.guild_id  # Asegúrate de que guild_id es el ID del servidor
        obj_guild = bot_inst.get_guild(guild)  # Cambié get_server() por get_guild()

        if not obj_guild:
            await self.ctx.send("❌ Servidor no encontrado.")
            return

        member = obj_guild.get_member(user_id)  # Obtener el miembro desde el servidor
        if not member:
            await self.ctx.send("❌ Usuario no encontrado.")
            return

        role = obj_guild.get_role(role_id)  # Obtener el rol desde el servidor
        if not role:
            await self.ctx.send("❌ Rol no encontrado.")
            return

        if action == "+":
            await member.add_roles(role)
        elif action == "-":
            await member.remove_roles(role)
        else:
            raise ValueError("❌ Acción no válida. Usa '+' para agregar o '-' para quitar el rol en $roleGrant[].")


    def get_user_avatar_by_id(self, user_id: int):
        """Obtiene el avatar de un usuario a partir de su ID dentro del contexto."""


        guild = bot_inst.get_guild(self.guild_id)

        if guild:
            member = guild.get_member(user_id)  # Buscar por ID de usuario
            if member:
                return member.avatar.url if member.avatar else member.default_avatar.url

        return None  # No se encontró el usuario o no tiene avatar personalizado




import os
import json  # Asegúrate de importar el módulo json

class VariableManager:
    _instances = {}  # Diccionario para manejar instancias por archivo JSON

    def __new__(cls, path="data.json"):
        if path not in cls._instances:
            cls._instances[path] = super(VariableManager, cls).__new__(cls)
            cls._instances[path]._initialize(path)
        return cls._instances[path]

    def _initialize(self, path):
        """Carga datos desde el archivo JSON si existe, de lo contrario, inicializa una estructura vacía."""
        self._file_path = path  # Guardar la ruta del archivo JSON
        if os.path.exists(self._file_path):
            with open(self._file_path, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        else:
            self.data = {
                "guilds": {},
                "channels": {},
                "users": {},
                "global": {},
                "global_users": {}
            }

    def _save_to_file(self):
        """Guarda los datos en el archivo JSON."""
        with open(self._file_path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def set_value(self, level, key, value, guild_id=None, user_id=None, channel_id=None):
        """Establece un valor en el nivel indicado y lo guarda en el JSON."""

        if level == "guild":
            if guild_id is None:
                raise ValueError("guild_id es requerido para valores de servidor.")
            # Asegurar que no se sobrescribe, solo se añade o actualiza
            self.data["guilds"].setdefault(guild_id, {})[key] = value

        elif level == "channel":
            if guild_id is None or channel_id is None:
                raise ValueError("guild_id y channel_id son requeridos para valores de canal.")
            self.data["channels"].setdefault(guild_id, {}).setdefault(channel_id, {})[key] = value

        elif level == "user":
            if guild_id is None or user_id is None:
                raise ValueError("guild_id y user_id son requeridos para valores de usuario en un servidor.")
        # Aquí es clave: asegurar niveles sin sobrescribir
            self.data["users"].setdefault(guild_id, {}).setdefault(user_id, {})[key] = value

        elif level == "global":
            self.data["global"][key] = value

        elif level == "global_user":
            if user_id is None:
                raise ValueError("user_id es requerido para valores globales de usuario.")
            self.data["global_users"].setdefault(user_id, {})[key] = value

        else:
            raise ValueError("Nivel no válido. Usa: 'guild', 'channel', 'user', 'global', 'global_user'.")

        self._save_to_file()


    def get_value(self, level, key, guild_id=None, user_id=None, channel_id=None):
        """Obtiene un valor almacenado en el nivel indicado."""
        if level == "guild":
            return self.data["guilds"].get(guild_id, {}).get(key, None)
        
        elif level == "channel":
            return self.data["channels"].get(guild_id, {}).get(channel_id, {}).get(key, None)
        
        elif level == "user":
            return self.data["users"].get(guild_id, {}).get(user_id, {}).get(key, None)
        
        elif level == "global":
            return self.data["global"].get(key, None)
        
        elif level == "global_user":
            return self.data["global_users"].get(user_id, {}).get(key, None)

        else:
            raise ValueError("Nivel no válido.")

    def to_json(self):
        """Devuelve la estructura en formato JSON."""
        return json.dumps(self.data, indent=4, ensure_ascii=False)






async def clear_data():
        # Limpiar las listas de botones, embeds y menús
    embeds.clear()
    buttons.clear()
    menu_options.clear()
    options_slash.clear()
    modales.clear()
    modals_activate = False
    ephemeral = False
    files.clear()
    canvas_storage.clear()

