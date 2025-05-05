

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select

import traceback

import asyncio
import xfox
import Amisynth.Handler
import Amisynth.utils as utils
from typing import List, Dict, Optional, Any
import os
import importlib.util


from Amisynth.utils import options_slash
from Amisynth.utils import clear_data

# Registrar todas las funciones automáticamente
Amisynth.Handler.register_all()

class AmiClient(commands.Bot):
    def __init__(self, prefix, cogs=None, variables_json=False, case_insensitive:bool=False):
        super().__init__(command_prefix=prefix, intents=discord.Intents.all(), case_insensitive=case_insensitive)
        
        self.prefix = prefix
        self.servicios_prefijos = {}  # Diccionario para guardar los prefijos por servidor
        self._cogs = cogs or []
        self.comandos_personalizados = {}
        self.eventos_personalizados = {
            "$onMessage": [],
            "$onReady": [],
            "$onReactionAdd": [],
            "$onReactionRemove": [],
            "$onInteraction": [],
            "$onMessageEdit": [],
            "$onMessageDelete": [],
            "$onJoinMember": [],
            "$onLeaveMember": [],
            "$onMessagesPurged": [],
            "$onMessageTyping": [],
            "$onChannelCreate": [],
            "$onChannelDelete": [],
            "$onChannelEdit": [],
            "$onThreadCreate": [],
            "$onThreadRemove": [],
            "$onThreadJoin": [],
            "$onThreadDelete": [],
            "$onThreadUpdate": [],
            "$onThreadJoinMember": [],
            "$onThreadRemoveMember": []
        }

        if variables_json == True:
            utils.VariableManager()

        utils.bot_inst = self

    async def get_prefix(self, msg):
        """Obtiene el prefijo de acuerdo con el servidor o usa el prefijo general."""
        if msg.guild:
            # Si el servidor tiene un prefijo personalizado, lo devuelve
            return self.servicios_prefijos.get(msg.guild.id, self.prefix)
        return self.prefix  # Usa el prefijo general si no es un servidor
    
    def set_prefijo_servidor(self, servidor_id, nuevo_prefijo):
        """Permite cambiar el prefijo para un servidor específico."""
        self.servicios_prefijos[servidor_id] = nuevo_prefijo


    async def setup_hook(self):
        """Cargar todos los cogs de forma asincrónica."""
        if self._cogs:  # Verificar si se pasó una carpeta de cogs
            await self.load_cogs(self._cogs)

    async def load_cogs(self, carpeta):
        """Cargar cogs de forma asincrónica."""
        for filename in os.listdir(carpeta):
            if filename.endswith(".py"):
                cog_path = os.path.join(carpeta, filename)

                # Cargar módulo dinámicamente
                spec = importlib.util.spec_from_file_location(filename[:-3], cog_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Si el cog tiene una función setup(bot), la ejecutamos
                if hasattr(module, "setup"):
                    await module.setup(self)  # Ejecutar setup(bot) si es async


    def new_command(self, name, type, code):
        async def custom_command(ctx_command):
            utils.ContextAmisynth(ctx=ctx_command)

            try:
              
                result = await xfox.parse(code, del_empty_lines=True)
             
            except ValueError as e:
                result = e
        
            texto = result
            botones, embeds, files = await utils.utils()
            view = discord.ui.View()
            botones_en_fila = 0
            # Construir el View si hay botones
            for boton in botones:
                if botones_en_fila < 5:
                    view.add_item(boton)
                    botones_en_fila += 1
                else:
            # Si hay más de 5 botones, empieza una nueva fila
                    view.add_item(boton)
                    botones_en_fila = 1
            

            # Enviar mensaje con el tipo adecuado
            try:
                message = await ctx_command.send(
                content=texto if texto else None,  # Si hay texto, se agrega
                view=view if botones else None,    # Si hay botones, se agrega el View
                embeds=embeds if embeds else None,  # Si hay embeds, se agregan
                files=files if files else []
                )
                kwargs = {'message': message}
                await clear_data()
                await xfox.parse(code, **kwargs)
                await clear_data()

            except ValueError as e:
                print(f"[ERROR COMMAND]: {e}")
            except xfox.Empty as e:
                await ctx_command.send(f":x: {e}")
            except Exception as e:
                print("Error en API:", e)
                traceback.print_exc()


            except discord.HTTPException as e:
                print(f"[ERROR] {e}")

       




        self.comandos_personalizados[name] = {"type": type, "code": code}
        self.add_command(commands.Command(custom_command, name=name))
    
    
    def new_slash(
        self,
        name: str,
        description: str,
        code: str = "",
    ):
        parameters = ["interaction: discord.Interaction"]
        choices_kwargs = {}

        
        options = options_slash
        options = asyncio.run(xfox.parse(code))
        print("[DEBUG NEWSLASH] PARSE COMPLETED")
        options = options_slash
        print("[DEBUG NEWSLASH] OPTIONS:", options_slash)

        def remp(valor):
            if valor.lower() == "texto":
                return "str"  # Devuelve el tipo de texto (string)
            elif valor.lower() == "integer":
                return "int"  # Devuelve el tipo entero
            elif valor.lower() == "archivo":
                return "discord.Attachment"  # Devuelve el tipo de archivo adjunto
            elif valor.lower() == "canal":
                return "discord.TextChannel"  # Devuelve el tipo de canal de texto
            elif valor.lower() == "mencionable":
                return "discord.Member" # Devuelve el tipo de miembro mencionable (puede ser un usuario o rol)
            elif valor.lower() == "rol":
                return "discord.Role"  # Devuelve el tipo de rol
            elif valor.lower() == "numero":
               return "float"  # Devuelve el tipo de número (puede ser entero o flotante)
            else:
               raise ValueError("[DEBUG SLASH] OPCION DE SLASH INVALIDA")
            
        describe_kwargs = {}
        
        if options:
            for option in options:
                option_name = option.get("name_option")
                param_name = option_name.replace(" ", "_")
                option_type = remp(valor=option["type"])
                option_required = option.get("required", False)
                
                if option_required:
                    parameters.append(f"{param_name}: {option_type}")
                else:
                    parameters.append(f"{param_name}: {option_type} = None")

                if "description" in option:
                    describe_kwargs[param_name] = option["description"]

                if "choices" in option and isinstance(option["choices"], list):
                    choices_kwargs[param_name] = [
                        app_commands.Choice(name=choice["name_choice"], value=choice["value_choice"])
                        for choice in option["choices"]
                    ]

        params_str = ", ".join(parameters)

        func_code = f"""async def slash_command({params_str}):
        kwargs = {{"ctx_slash_env": interaction}}
        utils.ContextAmisynth(interaction)

        result = await xfox.parse({repr(code)}, del_empty_lines=True, **kwargs)
        botones, embeds = await utils.utils()
           
        view = discord.ui.View()
        if botones:
            for boton in botones: 
                view.add_item(boton)

        await interaction.response.send_message(
            content=result if result else None,
            view=view,
            embeds=embeds if embeds else [],
            ephemeral=False



        )
        await clear_data()

        
        """
        
        exec(func_code, globals(), locals())
        command_func = locals()["slash_command"]
        # 🔸 Registrar el comando con @self.tree.command(...)

        if describe_kwargs:
            decorated_func = app_commands.describe(**describe_kwargs)(command_func)
        else:
            decorated_func = command_func
        decorated_func = self.tree.command(name=name, description=description)(decorated_func)

        
        for key, choices in choices_kwargs.items():
            decorated_func = app_commands.choices(**{key: choices})(decorated_func)
        
        self.comandos_personalizados[name] = {"type": "slash", "code": code}

        





    def new_event(self, 
                  tipo, 
                  codigo, 
                  overwrite=False):
        
        if tipo not in self.eventos_personalizados or overwrite:
            self.eventos_personalizados[tipo] = []  # Reiniciar si se sobrescribe
        self.eventos_personalizados[tipo].append(codigo)

    async def ejecutar_eventos(self, tipo, 
                               ctx_message_env=None, 
                               ctx_reaction_env=None, 
                               ctx_reaction_remove_env=None, 
                               ctx_interaction_env=None, 
                               ctx_message_edit_env=None, 
                               ctx_message_delete_env=None,
                               ctx_join_member_env=None,
                               ctx_remove_member_env=None,
                               ctx_bulk_message_delete_env=None,
                               ctx_typing_env=None,
                               ctx_guild_channel_create=None,
                               ctx_guild_channel_delete=None,
                               ctx_guild_channel_edit=None,
                               ctx_thread_create_env=None,
                               ctx_thread_remove_env=None,
                               ctx_thread_join_env=None,
                               ctx_thread_delete_env=None,
                               ctx_thread_update_env=None,
                               ctx_thread_member_join_env=None,
                               ctx_thread_member_remove_env=None
                               
                               ):
        

        if tipo in self.eventos_personalizados:
            for codigo in self.eventos_personalizados[tipo]:
                kwargs = {
                    "ctx_message_env": ctx_message_env,
                    "ctx_reaction_env": ctx_reaction_env,
                    "ctx_reaction_remove_env": ctx_reaction_remove_env,
                    "ctx_interaction_env": ctx_interaction_env,  # 👈 Agregado aquí
                    "ctx_message_edit_env": ctx_message_edit_env,
                    "ctx_message_delete_env": ctx_message_delete_env,
                    "ctx_join_member_env": ctx_join_member_env,
                    "ctx_remove_member_env": ctx_remove_member_env,
                    "ctx_bulk_message_delete_env": ctx_bulk_message_delete_env,
                    "ctx_typing_env": ctx_typing_env,
                    "ctx_guild_channel_create": ctx_guild_channel_create,
                    "ctx_guild_channel_delete": ctx_guild_channel_delete,
                    "ctx_guild_channel_edit": ctx_guild_channel_edit,
                    "ctx_thread_create_env": ctx_thread_create_env,
                    "ctx_thread_remove_env": ctx_thread_remove_env,
                    "ctx_thread_join_env": ctx_thread_join_env,
                    "ctx_thread_delete_env": ctx_thread_delete_env,
                    "ctx_thread_update_env": ctx_thread_update_env,
                    "ctx_thread_member_join_env": ctx_thread_member_join_env,
                    "ctx_thread_member_remove_env": ctx_thread_member_remove_env
                  
                }
                try:
                    result = await xfox.parse(codigo, del_empty_lines=True, **kwargs)
                except ValueError as e:
                    result = e

                botones, embeds = await utils.utils()
                view = discord.ui.View()
                if botones:
                    
                    # Crear un View para los botones
                    for boton in botones:
                        view.add_item(boton)  # Agregar los botones al View
                
                try:
                    if ctx_message_env:
                        await ctx_message_env.channel.send(result, 
                                                        view=view if view else None,  
                                                        embeds=embeds if embeds else [])

                    elif ctx_reaction_env:
                        channel = self.get_channel(ctx_reaction_env.channel_id, )
                        if channel:
                            await channel.send(result, 
                                            view=view if view else None,
                                            embeds=embeds if embeds else [])


                    elif ctx_reaction_remove_env:
                        channel = self.get_channel(ctx_reaction_remove_env.channel_id)
                        if channel:
                            await channel.send(result, 
                                            view=view,
                                            embeds=embeds if embeds else [])

                    elif ctx_interaction_env:
                        try:
                            mensaje_original = await ctx_interaction_env.channel.fetch_message(ctx_interaction_env.message.id)
                            view_original = discord.ui.View.from_message(mensaje_original)

       
                            for item in view_original.children:
                                view.add_item(item)
                        except Exception as e:
                                print(f"[DEBUG ONINTERACTION] Error al combinar views: {e}")
                        
           
                        await ctx_interaction_env.response.edit_message(
                                                            content=result,
                                                            view=view,
                                                            embeds=embeds
                                                                    )
   
                        

                    elif ctx_message_edit_env:
                        before, after = ctx_message_edit_env
                        await before.channel.send(content=result, 
                                              view=view, 
                                              embeds=embeds)

                    elif ctx_message_delete_env:
                        await ctx_message_delete_env.channel.send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                    
                    elif ctx_bulk_message_delete_env:
                        
                        await ctx_bulk_message_delete_env.channel.send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                        
                    elif ctx_typing_env:
                        
                        await ctx_typing_env[0].send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                    elif ctx_guild_channel_create:
                        
                        await ctx_guild_channel_create.send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                    elif ctx_guild_channel_edit:
                        
                        await ctx_guild_channel_edit[0].send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                        
                    elif ctx_thread_create_env:
                        
                        await ctx_thread_create_env.send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                        
                    elif ctx_thread_member_join_env:
                        
                        await ctx_thread_member_join_env.thread.send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                        
                    elif ctx_thread_member_remove_env:
                        
                        await ctx_thread_member_remove_env.thread.send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                        
                    elif ctx_thread_update_env:
                        
                        await ctx_thread_update_env[1].send(content=result, 
                                                                    view=view,
                                                                    embeds=embeds)
                    
                    
                    await clear_data()
                except Exception as e:
                    print(f"[DEBUG ERRORCLIENT]: {e}")
    


    async def on_message(self, ctx_message_env):
        if ctx_message_env.author.bot:
            return
        
        utils.ContextAmisynth(ctx_message_env)

        await self.ejecutar_eventos("$onMessage", ctx_message_env)
        await self.process_commands(ctx_message_env)  # Permite que otros comandos de discord.py sigan funcionando




    async def on_ready(self):
        print(f"[DEBUG CLIENT] USER:{self.user}")
        utils.bot_id = self.user.id
        await self.ejecutar_eventos("$onReady")
        try:
            synced = await self.tree.sync()
            
        except Exception as e:
            print(f"Error al sincronizar slash commands: {e}")



    async def on_member_join(self, member: discord.Member):
        utils.ContextAmisynth(member)
        await self.ejecutar_eventos("$onJoinMember", ctx_join_member_env=member)
    
    async def on_member_remove(self, member: discord.Member):
        utils.ContextAmisynth(member)
        await self.ejecutar_eventos("$onLeaveMember", ctx_remove_member_env=member)


        
    async def on_raw_reaction_add(self, ctx_reaction_env: discord.RawReactionActionEvent):
        utils.ContextAmisynth(ctx_reaction_env)
        """Maneja cuando un usuario añade una reacción."""
        await self.ejecutar_eventos("$onReactionAdd", ctx_reaction_env=ctx_reaction_env)



    async def on_raw_reaction_remove(self, ctx_reaction_remove_env: discord.RawReactionActionEvent):
        """Maneja cuando un usuario remueve una reacción."""
        utils.ContextAmisynth(ctx_reaction_remove_env)
        await self.ejecutar_eventos("$onReactionRemove", ctx_reaction_remove_env=ctx_reaction_remove_env)



    async def on_interaction(self, ctx_interaction_env: discord.Interaction):
        """Maneja interacciones como botones y menús."""
        if ctx_interaction_env.user.bot:
            return
        utils.ContextAmisynth(ctx_interaction_env)
        await self.ejecutar_eventos("$onInteraction", ctx_interaction_env=ctx_interaction_env)



    async def on_message_edit(self, before, after):
        utils.ContextAmisynth(before)
        if before.author.bot:  # Evita que el bot procese sus propios mensajes
            return
        await self.ejecutar_eventos("$onMessageEdit", ctx_message_edit_env=(before, after))
        

    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        utils.ContextAmisynth(message)
        await self.ejecutar_eventos("$onMessageDelete", ctx_message_delete_env=message)



    async def on_bulk_message_delete(self, ctx_bulk_message_delete_env: discord.Message):
        utils.ContextAmisynth(ctx_bulk_message_delete_env)
        await self.ejecutar_eventos("$onMessagesPurged", ctx_bulk_message_delete_env=ctx_bulk_message_delete_env[0])

    async def on_typing(self, channel, user, when):
        utils.ContextAmisynth(channel)
        await self.ejecutar_eventos("$onMessageTyping", ctx_typing_env=(channel, user, when))

    async def on_guild_channel_create(self, channel: discord.TextChannel):
        utils.ContextAmisynth(channel)
        await self.ejecutar_eventos("$onChannelCreate", ctx_guild_channel_delete=channel)


    async def on_guild_channel_delete(self, channel: discord.TextChannel):
        utils.ContextAmisynth(channel)
        await self.ejecutar_eventos("$onChannelDelete", ctx_guild_channel_delete=channel)

    async def on_guild_channel_update(self, before, after):
        utils.ContextAmisynth(before)
        await self.ejecutar_eventos("$onChannelEdit", ctx_guild_channel_edit=(before, after))


    async def on_thread_create(self, thread):
        utils.ContextAmisynth(thread)
        await self.ejecutar_eventos("$onThreadCreate", ctx_thread_create_env=thread)

    
    async def on_thread_remove(self, thread):
        utils.ContextAmisynth(thread)
        await self.ejecutar_eventos("$onThreadRemove", ctx_thread_remove_env=thread)

    
    async def on_thread_join(self, thread):
        utils.ContextAmisynth(thread)
        await self.ejecutar_eventos("$onThreadJoin", ctx_thread_join_env=thread)


    async def on_thread_delete(self, thread):
        utils.ContextAmisynth(thread)
        await self.ejecutar_eventos("$onThreadDelete", ctx_thread_delete_env=thread)


    async def on_thread_update(self, before, after):
        utils.ContextAmisynth(before)
        await self.ejecutar_eventos("$onThreadUpdate", ctx_thread_update_env=(before, after))

    
    async def on_thread_member_join(self, thread_member):
        utils.ContextAmisynth(thread_member)
        await self.ejecutar_eventos("$onThreadJoinMember", ctx_thread_member_join_env=thread_member)

    async def on_thread_member_remove(self, thread_member):
        utils.ContextAmisynth(thread_member)
        await self.ejecutar_eventos("$onThreadRemoveMember", ctx_thread_member_remove_env=thread_member)
