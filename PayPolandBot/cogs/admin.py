import discord
from discord.ext import commands
from utils.embed_templates import base_embed, add_banner_to_message
from utils.data_manager import admin_only

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='buduj', description='Buduje strukturę serwera (tylko admin)')
    @admin_only()
    async def buduj(self, ctx):
        # Tutaj kod budowania kategorii, kanałów, ról i wysyłania paneli
        # Ze względu na objętość, przedstawiam szkielet. Pełna implementacja wymaga szczegółowego tworzenia kanałów i uprawnień.
        await ctx.respond('Komenda w trakcie implementacji.', ephemeral=True)

    @commands.slash_command(name='wiadomosc', description='Wysyła wiadomość embed na kanał')
    @admin_only()
    async def wiadomosc(self, ctx, kanal: discord.TextChannel, tytul: str, opis: str, kolor: str = None):
        color = int(kolor.lstrip('#'), 16) if kolor else self.bot.config['colors']['info']
        embed = base_embed(title=tytul, description=opis, color=color)
        await add_banner_to_message(kanal.send(embed=embed))

    @commands.slash_command(name='clear', description='Czyści wiadomości na kanale')
    @admin_only()
    async def clear(self, ctx, liczba: int, kanal: discord.TextChannel = None):
        if kanal is None:
            kanal = ctx.channel
        await kanal.purge(limit=liczba)
        await ctx.respond(f'Usunięto {liczba} wiadomości na {kanal.mention}', ephemeral=True)

    @commands.slash_command(name='role', description='Zarządza rolami użytkownika')
    @admin_only()
    async def role(self, ctx, user: discord.Member, rola: discord.Role, nadaj: bool):
        if nadaj:
            await user.add_roles(rola)
            await ctx.respond(f'Nadano rolę {rola.name} użytkownikowi {user.mention}', ephemeral=True)
        else:
            await user.remove_roles(rola)
            await ctx.respond(f'Odebrano rolę {rola.name} użytkownikowi {user.mention}', ephemeral=True)

def setup(bot):
    bot.add_cog(Admin(bot))
