import discord
from discord.ext import commands
import json
import logging
import os
from utils.data_manager import DataManager

# Konfiguracja logowania
logging.basicConfig(
    filename='logs/paypoland.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Wczytaj config
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# Globalne obiekty
bot.config = config
bot.data_manager = DataManager()

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user} (ID: {bot.user.id})')
    print('------')
    # Ładowanie cogów
    await bot.load_extension('cogs.admin')
    await bot.load_extension('cogs.exchange')
    await bot.load_extension('cogs.tickets')
    await bot.load_extension('cogs.stats')
    await bot.load_extension('cogs.automod')
    print('Wszystkie cogi załadowane.')

    # Ustawienie Persistent Views
    from cogs.tickets import TicketPanelView
    from cogs.exchange import ExchangePanelView
    bot.add_view(TicketPanelView())
    bot.add_view(ExchangePanelView())
    print('Persistent Views dodane.')

if __name__ == '__main__':
    bot.run(config['token'])
