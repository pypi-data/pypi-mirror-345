import xfox

import time

@xfox.addfunc(xfox.funcs)
async def getTimestamp(opcion=None, *args, **kwargs):
    # Obtener el tiempo actual
    current_time = time.time()  # Esto devuelve el tiempo en segundos (float)

    if opcion: 
        if opcion.lower() == "s":
            return str(int(current_time))  # Devuelve el tiempo en segundos (s)
    
        elif opcion.lower() == "ms":
            return str(int(current_time * 1000))  # Convierte a milisegundos (ms)
    
        elif opcion.lower() == "ns":
             return str(int(current_time * 1e9))  # Convierte a nanosegundos (ns)
    
        else:
            raise ValueError(":x: Opción no válida en `$getTimestamp[]`. Usa `s`, `ms`, o `ns`.")
        
    elif opcion is None:
        return str(int(current_time))
