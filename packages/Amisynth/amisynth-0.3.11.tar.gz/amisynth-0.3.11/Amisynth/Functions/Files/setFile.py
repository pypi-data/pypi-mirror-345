import xfox
import discord
import io
import requests
from PIL import Image
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def setFile(direccion, *args, **kwargs):
    # Aseguramos que utils.files sea una lista
    if not isinstance(utils.files, list):
        utils.files = []

    # Creamos el objeto para el archivo binario de la imagen o el .txt
    file_binary = io.BytesIO()

    # Manejo de imagen o archivo de texto
    if direccion.endswith(".txt"):
        # Si es un archivo .txt
        if direccion.startswith("http://") or direccion.startswith("https://"):
            # Descargar el archivo de texto desde internet
            response = requests.get(direccion)
            response.raise_for_status()  # Por si da error de descarga
            file_binary.write(response.content)
        else:
            # Cargar desde un archivo local
            with open(direccion, "rb") as f:
                file_binary.write(f.read())

        file_binary.seek(0)
        # Crear el discord.File para el archivo .txt
        nombre_archivo = direccion.split("/")[-1].split("?")[0]  # Limpiar nombre si tiene parámetros
        file = discord.File(fp=file_binary, filename=nombre_archivo)
    
    elif direccion.startswith("http://") or direccion.startswith("https://") or direccion.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        # Si es una imagen
        image_binary = io.BytesIO()
        if direccion.startswith("http://") or direccion.startswith("https://"):
            # Descargar la imagen de internet
            response = requests.get(direccion)
            response.raise_for_status()  # Por si da error de descarga
            image_binary.write(response.content)
        else:
            # Cargar desde un archivo local
            with open(direccion, "rb") as f:
                image_binary.write(f.read())

        image_binary.seek(0)

        # Validar que sea una imagen válida usando PIL
        try:
            img = Image.open(image_binary)
            img.verify()  # Solo verificar que es una imagen, no reescribir
        except Exception as e:
            raise Exception(f"Archivo de imagen inválido: {e}")

        # Reiniciamos puntero para el File
        image_binary.seek(0)

        # Crear el discord.File para la imagen
        nombre_archivo = direccion.split("/")[-1].split("?")[0]  # Limpiar nombre si tiene parámetros
        file = discord.File(fp=image_binary, filename=nombre_archivo)
    
    else:
        raise Exception("El archivo no es ni una imagen ni un archivo .txt válido.")

    # Añadimos el archivo a la lista
    utils.files.append(file)

    return ""
