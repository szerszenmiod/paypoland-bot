import json
import os
from threading import Timer
from datetime import datetime
import discord

def admin_only():
    def predicate(ctx):
        admin_role = discord.utils.get(ctx.guild.roles, name=ctx.bot.config['role_names']['admin'])
        return admin_role in ctx.author.roles
    return commands.check(predicate)

class DataManager:
    def __init__(self):
        self.user_stats = {}
        self.open_tickets = {}
        self.ticket_data = {}
        self.load_data()
        self.start_auto_save()

    def load_data(self):
        if os.path.exists('data/user_stats.json'):
            with open('data/user_stats.json', 'r') as f:
                self.user_stats = json.load(f)
        if os.path.exists('data/open_tickets.json'):
            with open('data/open_tickets.json', 'r') as f:
                self.open_tickets = json.load(f)
        if os.path.exists('data/ticket_data.json'):
            with open('data/ticket_data.json', 'r') as f:
                self.ticket_data = json.load(f)

    def save_data(self):
        with open('data/user_stats.json', 'w') as f:
            json.dump(self.user_stats, f, indent=4)
        with open('data/open_tickets.json', 'w') as f:
            json.dump(self.open_tickets, f, indent=4)
        with open('data/ticket_data.json', 'w') as f:
            json.dump(self.ticket_data, f, indent=4)

    def start_auto_save(self):
        Timer(300, self.save_data).start()

# Funkcje pomocnicze
def get_user_stats(bot, user_id):
    user_id = str(user_id)
    if user_id not in bot.data_manager.user_stats:
        bot.data_manager.user_stats[user_id] = {
            "exchanges": 0,
            "total_eur": 0.0,
            "joined_at": datetime.now().isoformat()
        }
    return bot.data_manager.user_stats[user_id]

def update_user_stats(bot, user_id, amount):
    user_id = str(user_id)
    stats = get_user_stats(bot, user_id)
    stats['exchanges'] += 1
    stats['total_eur'] += amount
    bot.data_manager.save_data()

def get_leaderboard(bot):
    # Zwraca listę (user_id, stats) posortowaną malejąco według exchanges
    sorted_stats = sorted(bot.data_manager.user_stats.items(), key=lambda x: x[1]['exchanges'], reverse=True)
    return sorted_stats
