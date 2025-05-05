# Amisynth

Amisynth es un paquete para integrar funciones personalizadas en Discord.

![PyPI](https://img.shields.io/pypi/v/amisynth)
[![PyPI Downloads](https://static.pepy.tech/badge/amisynth)](https://pepy.tech/projects/amisynth)
![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
[![Docs](https://img.shields.io/badge/docs-passing-brightgreen)](https://amisynth.github.io/AmisynthDocs/)
[![Únete a nuestro Discord](https://img.shields.io/badge/Discord-Support-blue?logo=discord)](https://discord.gg/5xSjPnxRTa)

## Instalación

Para instalar este paquete, usa `pip`:

```bash
pip install Amisynth
```

## Codigo Basico

```python

from Amisynth.client import AmiClient

bot = AmiClient(prefix="!")

bot.new_command(name="test",
                 type="text",
                 code="Hi everyone!")

bot.run("""TOKEN BOT""")
```

##  Codigo con Cogs

```python
AmiClient(prefix="!", cogs="carpeta de cogs")
```

##  Eventos


```python
from Amisynth.client import AmiClient

bot = AmiClient(prefix="!")

bot.new_event(name="$onMessage",
                 code="Hi everyone!")

bot.run("""TOKEN BOT""")
```

##  Cog Exmaple

```python
# cog/test.py
def setup(bot):
    bot.new_command(name="test",
                 type="text",
                 code="Hi everyone!")
``` 