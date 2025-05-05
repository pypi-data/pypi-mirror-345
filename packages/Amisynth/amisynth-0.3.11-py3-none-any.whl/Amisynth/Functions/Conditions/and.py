import re
import xfox
@xfox.addfunc(xfox.funcs, name="and")
async def andCondition(*conditions: str, **kwargs):
    operadores_validos = ["!=", "==", ">=", "<=", ">", "<"]
    
    def evaluar_condicion(condition):
        patron = r'^(.*?)(!=|==|>=|<=|>|<)(.*?)$'
        coincidencia = re.match(patron, condition)
        
        if not coincidencia:
            return False  # Retorna False si la condición no es válida
        
        izquierda, operador, derecha = coincidencia.groups()
        izquierda, derecha = izquierda.strip(), derecha.strip()
        
        if (izquierda == "" and derecha != "") or (derecha == "" and izquierda != ""):
            return operador != "=="
        
        try:
            izquierda = float(izquierda) if izquierda.replace(".", "", 1).isdigit() else izquierda
            derecha = float(derecha) if derecha.replace(".", "", 1).isdigit() else derecha
            resultado = eval(f'"{izquierda}" {operador} "{derecha}"') if isinstance(izquierda, str) or isinstance(derecha, str) else eval(f'{izquierda} {operador} {derecha}')
            return resultado
        except Exception:
            return False
    
    return "True" if all(evaluar_condicion(cond) for cond in conditions) else "False"