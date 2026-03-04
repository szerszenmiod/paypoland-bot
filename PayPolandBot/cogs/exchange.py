import discord
from discord.ext import commands
from utils.validators import validate_crypto_address
from utils.embed_templates import base_embed, add_banner_to_message
from utils.data_manager import update_user_stats, get_user_stats
import re

class ExchangeModal(discord.ui.Modal):
    def __init__(self, crypto_type, bot):
        super().__init__(title=f"💱 Wymiana PayPal → {crypto_type}")
        self.crypto_type = crypto_type
        self.bot = bot

        self.add_item(discord.ui.InputText(
            label="💰 Kwota w EURO",
            placeholder="np. 50.00 (min. 10, max. 1000)",
            required=True
        ))
        self.add_item(discord.ui.InputText(
            label=f"💎 Adres portfela {crypto_type}",
            placeholder="Wprowadź adres...",
            required=True
        ))
        self.add_item(discord.ui.InputText(
            label="📋 Kod transakcji PayPal (opcjonalnie)",
            placeholder="ID transakcji z PayPal",
            required=False
        ))

    async def callback(self, interaction: discord.Interaction):
        # Walidacja kwoty
        try:
            amount = float(self.children[0].value)
            if amount < self.bot.config['min_exchange_amount'] or amount > self.bot.config['max_exchange_amount']:
                raise ValueError("Kwota poza zakresem")
        except:
            await interaction.response.send_message("❌ Nieprawidłowa kwota.", ephemeral=True)
            return

        address = self.children[1].value.strip()
        if not validate_crypto_address(self.crypto_type, address):
            await interaction.response.send_message("❌ Nieprawidłowy adres kryptowaluty.", ephemeral=True)
            return

        paypal_code = self.children[2].value.strip() if self.children[2].value else None

        # Sprawdź czy użytkownik nie ma już otwartego ticketa
        if str(interaction.user.id) in self.bot.data_manager.open_tickets:
            channel_id = self.bot.data_manager.open_tickets[str(interaction.user.id)]
            await interaction.response.send_message(f"Masz już otwarty ticket: <#{channel_id}>", ephemeral=True)
            return

        # Utwórz ticket
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=self.bot.config['category_names']['tickets'])
        if not category:
            await interaction.response.send_message("❌ Kategoria ticketów nie istnieje. Uruchom /buduj.", ephemeral=True)
            return

        channel_name = f"ticket-{self.crypto_type.lower()}-{interaction.user.name}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        staff_role = discord.utils.get(guild.roles, name=self.bot.config['role_names']['staff'])
        admin_role = discord.utils.get(guild.roles, name=self.bot.config['role_names']['admin'])
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        # Zapisz dane ticketa
        self.bot.data_manager.open_tickets[str(interaction.user.id)] = channel.id
        self.bot.data_manager.ticket_data[str(channel.id)] = {
            "user_id": interaction.user.id,
            "crypto": self.crypto_type,
            "amount": amount,
            "address": address,
            "paypal_code": paypal_code,
            "created_at": discord.utils.utcnow().isoformat(),
            "status": "open"
        }
        self.bot.data_manager.save_data()

        # Wyślij embed powitalny
        embed = base_embed(
            title=f":ticket: **NOWY TICKET WYMIANY** :ticket:",
            description=f"**Użytkownik:** {interaction.user.mention}\n"
                        f"**Kryptowaluta:** {self.crypto_type}\n"
                        f"**Kwota:** {amount} EUR\n"
                        f"**Adres:** {address}\n"
                        f"**Kod PayPal:** {paypal_code or 'Brak'}",
            color=self.bot.config['colors']['ticket']
        )
        await channel.send(embed=embed)

        # Wyślij profil użytkownika
        stats = get_user_stats(self.bot, interaction.user.id)
        profile_embed = base_embed(
            title=f":bust_in_silhouette: **TWOJ PROFIL** :bust_in_silhouette:",
            description=f"**Wykonane wymiany:** {stats['exchanges']}\n"
                        f"**Łączna kwota:** {stats['total_eur']} EUR",
            color=self.bot.config['colors']['info']
        )
        await channel.send(embed=profile_embed)

        # Ping do staff
        await channel.send(f"{staff_role.mention if staff_role else '@Staff'} Nowy ticket wymiany do weryfikacji!")

        await interaction.response.send_message(f"✅ Utworzono ticket: {channel.mention}", ephemeral=True)

class ExchangePanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Litecoin (LTC)", style=discord.ButtonStyle.secondary, custom_id="paypoland:exchange:ltc", emoji="💚")
    async def ltc_button(self, button, interaction):
        await interaction.response.send_modal(ExchangeModal("LTC", interaction.client))

    @discord.ui.button(label="Bitcoin (BTC)", style=discord.ButtonStyle.secondary, custom_id="paypoland:exchange:btc", emoji="💛")
    async def btc_button(self, button, interaction):
        await interaction.response.send_modal(ExchangeModal("BTC", interaction.client))

    @discord.ui.button(label="Ethereum (ETH)", style=discord.ButtonStyle.secondary, custom_id="paypoland:exchange:eth", emoji="💜")
    async def eth_button(self, button, interaction):
        await interaction.response.send_modal(ExchangeModal("ETH", interaction.client))

class StaffConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Potwierdź wymianę", style=discord.ButtonStyle.success, custom_id="paypoland:staff:confirm")
    async def confirm_button(self, button, interaction):
        # Sprawdź uprawnienia
        if not any(role.name in [interaction.client.config['role_names']['staff'], interaction.client.config['role_names']['admin']] for role in interaction.user.roles):
            await interaction.response.send_message("❌ Brak uprawnień!", ephemeral=True)
            return

        channel = interaction.channel
        ticket = interaction.client.data_manager.ticket_data.get(str(channel.id))
        if not ticket or ticket['status'] != 'open':
            await interaction.response.send_message("❌ Ticket nie jest otwarty lub nie istnieje.", ephemeral=True)
            return

        user = channel.guild.get_member(ticket['user_id'])
        if not user:
            await interaction.response.send_message("❌ Użytkownik nie znajduje się na serwerze.", ephemeral=True)
            return

        # Obliczenia prowizji
        kwota_brutto = ticket['amount']
        prowizja = interaction.client.config['commission_rate']
        kwota_netto = kwota_brutto * (1 - prowizja)

        # Aktualizacja statystyk
        update_user_stats(interaction.client, user.id, kwota_brutto)

        # Wysłanie voucha na kanał #🚀vouches
        vouches_channel = discord.utils.get(channel.guild.channels, name=interaction.client.config['channel_names']['vouches'])
        if vouches_channel:
            embed = base_embed(
                title=f":rocket: **NOWA UDANA WYMIANA** :rocket:",
                description=f"**:star: +rep @{user.name}**\n\n"
                            f"**Szczegóły transakcji:**\n"
                            f"┌──────────────\n"
                            f"│ :exchange_arrow: **Wymiana:** PayPal → {ticket['crypto']}\n"
                            f"│ :euro: **Kwota brutto:** {kwota_brutto} EUR\n"
                            f"│ :moneybag: **Po prowizji (40%):** {kwota_netto:.2f} EUR w {ticket['crypto']}\n"
                            f"│ :bust_in_silhouette: **Weryfikator:** @{interaction.user.name}\n"
                            f"└──────────────\n\n"
                            f"**:gem: Łącznie użytkownik wykonał już {get_user_stats(interaction.client, user.id)['exchanges']} wymian!**",
                color=interaction.client.config['colors']['success']
            )
            await add_banner_to_message(vouches_channel.send(embed=embed))

        # Log transakcji
        logs_channel = discord.utils.get(channel.guild.channels, name=interaction.client.config['channel_names']['transakcje'])
        if logs_channel:
            log_embed = base_embed(
                title=f":file_folder: **LOG TRANSAKCJI**",
                description=f"**Użytkownik:** @{user.name} ({user.id})\n"
                            f"**Staff:** @{interaction.user.name} ({interaction.user.id})\n"
                            f"**Kwota brutto:** {kwota_brutto} EUR\n"
                            f"**Krypto:** {ticket['crypto']}\n"
                            f"**Adres:** {ticket['address']}\n"
                            f"**Kwota netto:** {kwota_netto:.2f} EUR\n"
                            f"**Data:** {discord.utils.utcnow().strftime('%d.%m.%Y %H:%M:%S')}",
                color=interaction.client.config['colors']['info']
            )
            await logs_channel.send(embed=log_embed)

        # Zamknięcie ticketa
        ticket['status'] = 'confirmed'
        interaction.client.data_manager.save_data()

        # Usuń z open_tickets
        if str(user.id) in interaction.client.data_manager.open_tickets:
            del interaction.client.data_manager.open_tickets[str(user.id)]
            interaction.client.data_manager.save_data()

        await channel.send("✅ Transakcja potwierdzona! Ticket zostanie zamknięty za 30 sekund.")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=30))
        await channel.delete()

class Exchange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Exchange(bot))
