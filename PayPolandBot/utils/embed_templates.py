import discord
from datetime import datetime

def base_embed(title, description, color=0x0099ff):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    embed.set_footer(text=f"PayPoland © 2026 • All rights reserved • {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    return embed

async def add_banner_to_message(coro):
    """
    Użycie: await add_banner_to_message(channel.send(embed=embed))
    """
    from main import bot  # aby uniknąć cyklicznych importów
    message = await coro
    # Tu można dodać banner jako attachment, ale wymaga to dostępu do pliku.
    # W tej wersji zakładamy, że banner jest dołączany automatycznie przez funkcję wysyłającą.
    # W praktyce w każdej komendzie trzeba jawnie dodać file=discord.File(bot.config['banner_path'])
    return message
