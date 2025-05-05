import xfox
import discord
import Amisynth.utils as utils
import asyncio
from typing import Any


@xfox.addfunc(xfox.funcs, "addBotReaction")
async def addBotReaction(*args, **kwargs) -> str:
    """
    Adds reactions to a message for each item in args (expected to be emojis).
    
    Args:
        *args: Any number of arguments (emojis) to add as reactions.
        **kwargs: Additional keyword arguments, if needed.
        
    Returns:
        str: An empty string to indicate the completion of the function or an error message.
    """
    if not 'message' in kwargs:

        return ""
    
    obj = kwargs['message']

    # Ensure args is not empty
    if not args:
        raise ValueError(":x: No emojis provided.")

    try:
        # Add each emoji reaction to the message
        for emoji in args:
            await obj.add_reaction(emoji)
    except Exception as e:
        raise ValueError(f"Error adding reactions: {str(e)}")
    print("[DEBUG ADDCMDREACTION] eactions added successfully ")
    return ""
