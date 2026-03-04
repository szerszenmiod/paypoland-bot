import discord
from discord.ext import commands
import re

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_pattern = re.compile(r'(discord\.(gg|com\/invite|app\.com\/invite)\/\S+)', re.IGNORECASE)
        self.url_pattern = re.compile(r'(https?://\S+|www\.\S+)', re.IGNORECASE)
        self.spam_count = {}  # user_id -> [licznik, ostatni czas]
        self.warnings = {}    # user_id -> liczba ostrzeżeń

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Ignorowane kanały
        if message.channel.name in self.bot.config['automod']['ignored_channels']:
            return

        # Blokada zaproszeń
        if self.bot.config['automod']['block_invites']:
            if self.invite_pattern.search(message.content):
                await message.delete()
                await self.warn_user(message.author, "Wysłanie zaproszenia na inny serwer")
                return

        # Blokada linków
        if self.bot.config['automod']['block_all_links']:
            if self.url_pattern.search(message.content):
                await message.delete()
                await self.warn_user(message.author, "Wysłanie linku")
                return

        # Anty-spam
        now = discord.utils.utcnow().timestamp()
        user_id = str(message.author.id)
        if user_id not in self.spam_count:
            self.spam_count[user_id] = [1, now]
        else:
            count, last_time = self.spam_count[user_id]
            if now - last_time < self.bot.config['automod']['spam_timeframe']:
                if count >= self.bot.config['automod']['spam_limit']:
                    await self.warn_user(message.author, "Spamowanie")
                    # Mute po 3 ostrzeżeniach
                    if self.warnings.get(user_id, 0) >= 3:
                        await self.mute_user(message.author)
                else:
                    self.spam_count[user_id][0] += 1
            else:
                self.spam_count[user_id] = [1, now]

        # Cenzura przekleństw (uproszczona, można rozbudować)
        if self.bot.config['automod']['censor_swears']:
            bad_words = ["kurwa", "chuj", "pierdol", "dupa"]  # przykładowa lista
            if any(word in message.content.lower() for word in bad_words):
                await message.delete()
                await self.warn_user(message.author, "Użycie niedozwolonego słowa")

    async def warn_user(self, user, reason):
        user_id = str(user.id)
        self.warnings[user_id] = self.warnings.get(user_id, 0) + 1
        try:
            await user.send(f"⚠️ Ostrzeżenie: {reason}. Liczba ostrzeżeń: {self.warnings[user_id]}/3")
        except:
            pass

    async def mute_user(self, user):
        muted_role = discord.utils.get(user.guild.roles, name=self.bot.config['role_names']['muted'])
        if muted_role:
            await user.add_roles(muted_role)
            # Usuń mute po czasie
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(minutes=self.bot.config['automod']['mute_duration']))
            await user.remove_roles(muted_role)

def setup(bot):
    bot.add_cog(Automod(bot))
