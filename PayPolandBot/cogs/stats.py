import discord
from discord.ext import commands
from utils.embed_templates import base_embed, add_banner_to_message
from utils.data_manager import get_user_stats, get_leaderboard

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='stats', description='Wyświetla statystyki użytkownika')
    async def stats(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        stats = get_user_stats(self.bot, user.id)
        embed = base_embed(
            title=f":bar_chart: **STATYSTYKI UŻYTKOWNIKA** :bar_chart:",
            description=f"**Użytkownik:** {user.mention}\n"
                        f"**Wykonane wymiany:** {stats['exchanges']}\n"
                        f"**Łączna kwota:** {stats['total_eur']} EUR\n"
                        f"**Dołączył:** <t:{int(stats['joined_at'].timestamp())}:R>",
            color=self.bot.config['colors']['gold']
        )
        await add_banner_to_message(ctx.respond(embed=embed))

    @commands.slash_command(name='leaderboard', description='Top 10 najaktywniejszych użytkowników')
    async def leaderboard(self, ctx):
        leaderboard_data = get_leaderboard(self.bot)
        description = ""
        for i, (user_id, stats) in enumerate(leaderboard_data[:10], 1):
            user = self.bot.get_user(int(user_id))
            if user:
                description += f"**{i}.** {user.mention} – {stats['exchanges']} wymian (łącznie {stats['total_eur']} EUR)\n"
            else:
                description += f"**{i}.** Nieznany użytkownik – {stats['exchanges']} wymian\n"

        # Dodaj pozycję wywołującego
        user_stats = get_user_stats(self.bot, ctx.author.id)
        position = next((i for i, (uid, _) in enumerate(leaderboard_data) if uid == str(ctx.author.id)), None)
        if position is not None:
            description += f"\n**Twoja pozycja:** #{position+1} (wykonano {user_stats['exchanges']} wymian)"

        embed = base_embed(
            title=f":trophy: **TOP 10 NAJAKTYWNIEJSZYCH** :trophy:",
            description=description,
            color=self.bot.config['colors']['gold']
        )
        await add_banner_to_message(ctx.respond(embed=embed))

    @commands.slash_command(name='vouch', description='Ręczne dodanie voucha (staff)')
    @commands.has_any_role('Staff', 'Admin')
    async def vouch(self, ctx, user: discord.Member, kwota: float):
        update_user_stats(self.bot, user.id, kwota)
        await ctx.respond(f"✅ Dodano vouch dla {user.mention} na kwotę {kwota} EUR.", ephemeral=True)

def setup(bot):
    bot.add_cog(Stats(bot))
