import xfox

@xfox.addfunc(xfox.funcs)
async def replaceText(text, sample, new, amount=-1, *args, **kwargs):
    """
    Reemplaza todas las ocurrencias de 'sample' por 'new' en el texto, limitando los reemplazos a la cantidad especificada.

    :param text: El texto original en el que se realizarán los reemplazos.
    :param sample: El texto que será reemplazado.
    :param new: El texto que reemplazará a 'sample'.
    :param amount: La cantidad máxima de reemplazos. Por defecto es -1, lo que significa que se reemplazarán todas las ocurrencias.
    :return: El texto con los reemplazos realizados.
    """
    
    # Asegurarnos de que 'amount' sea un número entero
    try:
        amount = int(amount)  # Convertir a entero
    except ValueError:
        raise ValueError(f"Invalid amount value: {amount}. It must be an integer.")

    # Reemplazar las ocurrencias del texto
    if amount == -1:
        # Reemplazar todas las ocurrencias
        return text.replace(sample, new)
    else:
        # Limitar la cantidad de reemplazos
        count = 0
        result = []
        for part in text.split(sample):
            result.append(part)
            if count < amount:
                result.append(new)
                count += 1
        return ''.join(result)
