import re
import xfox

@xfox.addfunc(xfox.funcs)
async def checkCondition(condition: str, *args, **kwargs):
    operadores_validos = ["!=", "==", ">=", "<=", ">", "<"]
    
    # Expresión regular para capturar la condición
    patron = r'^(.*?)(!=|==|>=|<=|>|<)(.*?)$'
    coincidencia = re.match(patron, condition)
    
    if not coincidencia:
        return "False"  # Retorna False si la condición no es válida
    
    izquierda, operador, derecha = coincidencia.groups()
    izquierda, derecha = izquierda.strip(), derecha.strip()
    
    # Si alguno de los valores es vacío, se deja como cadena vacía
    izquierda = izquierda if izquierda else ""
    derecha = derecha if derecha else ""
    
    # Caso especial: Si un lado está vacío y el otro no, evitar evaluar "e==" como True
    if (izquierda == "" and derecha != "") or (derecha == "" and izquierda != ""):
        return "False" if operador == "==" else "True"
    
    try:
        # Intentar convertir a número si es posible, si no, dejar como string
        izquierda = float(izquierda) if izquierda.replace(".", "", 1).isdigit() else izquierda
        derecha = float(derecha) if derecha.replace(".", "", 1).isdigit() else derecha
        
        # Evaluar la condición
        resultado = eval(f'"{izquierda}" {operador} "{derecha}"') if isinstance(izquierda, str) or isinstance(derecha, str) else eval(f'{izquierda} {operador} {derecha}')
        
        return "True" if resultado else "False"
    except Exception:
        return "False"
