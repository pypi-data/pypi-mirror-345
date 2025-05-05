import xfox
import re

@xfox.addfunc(xfox.funcs)
async def findEmails(text: str, *args, **kwargs):
    # Expresión regular para detectar emails
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    
    return ', '.join(emails) if emails else ""
