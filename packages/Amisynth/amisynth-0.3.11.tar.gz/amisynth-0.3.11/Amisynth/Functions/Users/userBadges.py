import xfox
import discord
import Amisynth.utils as utils

@xfox.addfunc(xfox.funcs)
async def userBadges(user_id: int = None, separator: str = "\n", *args, **kwargs):
    contexto = utils.ContextAmisynth()

    resolved_user_id = user_id if user_id is not None else contexto.author_id

    # Intenta buscar al miembro primero
    member = contexto.obj_guild.get_member(resolved_user_id)
    if member is None:
        member = await contexto.obj_guild.fetch_member(resolved_user_id)

    # Accede al objeto User (para obtener public_flags)
    user = member._user if hasattr(member, "_user") else member

    # Lista de posibles flags (badges)
    flags = user.public_flags

    badge_map = {
        "staff": "Discord Staff",
        "partner": "Partner",
        "hypesquad": "HypeSquad Events",
        "bug_hunter": "Bug Hunter",
        "bug_hunter_level_2": "Bug Hunter Level 2",
        "hypesquad_bravery": "Bravery",
        "hypesquad_brilliance": "Brilliance",
        "hypesquad_balance": "Balance",
        "early_supporter": "Early Supporter",
        "verified_bot_developer": "Verified Bot Dev",
        "active_developer": "Active Developer",
        "discord_certified_moderator": "Certified Moderator",
        "premium_promo_dismissed": "Promo Dismissed",
    }

    badges = [name for attr, name in badge_map.items() if getattr(flags, attr, False)]

    return separator.join(badges) if badges else "Este usuario no tiene badges públicas."
