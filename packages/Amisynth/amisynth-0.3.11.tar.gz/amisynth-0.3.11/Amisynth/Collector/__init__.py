import os
import importlib.util


def load_functions():
    """Carga automáticamente todas las funciones de la carpeta 'Functions'."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  
    folder = os.path.join(base_path, "Functions")  # Accede a `Amisynth/Functions`

    if not os.path.exists(folder):
        print(f"⚠️ No se encontró la carpeta 'Functions' en {folder}")
        return  

    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".py"):
                module_name = filename[:-3]  # Nombre del módulo sin `.py`
                module_path = os.path.join(root, filename)  # Ruta completa del archivo

                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)

                try:
                    spec.loader.exec_module(module)  # Carga y ejecuta el módulo sin almacenarlo
                    # print(f"✅ Módulo cargado: {module_name}")
                    
                except Exception as e:
                    print(f"❌ Error al cargar {module_name}: {e}")

