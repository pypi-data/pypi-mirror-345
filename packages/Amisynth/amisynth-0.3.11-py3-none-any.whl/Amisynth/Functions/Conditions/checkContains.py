import xfox

@xfox.addfunc(xfox.funcs)
async def checkContains(text, *phrases, **kwargs):
    """
    Verifica si el texto contiene alguna de las frases proporcionadas.
    Devuelve True si alguna frase está contenida en el texto, y False si no.

    :param text: El texto en el que buscar las frases.
    :param phrases: Las frases que se buscarán dentro del texto.
    :return: True si alguna frase está contenida en el texto, False si no.
    """
    
    # Verificar si alguna de las frases está en el texto
    for phrase in phrases:
        if phrase.lower() in text.lower():
            return True
    
    return False  # Si ninguna frase fue encontrada en el texto
