import discord
from discord.ext import commands
from utils.embed_templates import base_embed, add_banner_to_message

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💰 Odbierz pieniądze", style=discord.ButtonStyle.success, custom_id="paypoland:ticket:money", emoji="💰")
    async def money_button(self, button, interaction):
        # Sprawdź czy użytkownik ma już otwarty ticket
        if str(interaction.user.id) in interaction.client.data_manager.open_tickets:
            channel_id = interaction.client.data_manager.open_tickets[str(interaction.user.id)]
            await interaction.response.send_message(f"Masz już otwarty ticket: <#{channel_id}>", ephemeral=True)
            return

        # Przekieruj do panelu wymiany? Tutaj możesz otworzyć modal z wyborem krypto
        await interaction.response.send_message("Przejdź do kanału #💰panel-odbierz-pieniadze i wybierz kryptowalutę.", ephemeral=True)

    @discord.ui.button(label="❓ Inne pytanie", style=discord.ButtonStyle.secondary, custom_id="paypoland:ticket:help", emoji="❓")
    async def help_button(self, button, interaction):
        # Tworzy ticket pomocniczy
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=interaction.client.config['category_names']['tickets'])
        if not category:
            await interaction.response.send_message("❌ Kategoria ticketów nie istnieje. Uruchom /buduj.", ephemeral=True)
            return

        channel_name = f"pomoc-{interaction.user.name}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        staff_role = discord.utils.get(guild.roles, name=interaction.client.config['role_names']['staff'])
        admin_role = discord.utils.get(guild.roles, name=interaction.client.config['role_names']['admin'])
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        # Zapisz ticket w danych
        interaction.client.data_manager.open_tickets[str(interaction.user.id)] = channel.id
        interaction.client.data_manager.ticket_data[str(channel.id)] = {
            "user_id": interaction.user.id,
            "type": "help",
            "created_at": discord.utils.utcnow().isoformat(),
            "status": "open"
        }
        interaction.client.data_manager.save_data()

        embed = base_embed(
            title="🆘 POMOC",
            description="Staff wkrótce się Tobą zajmie. Opisz swój problem.",
            color=interaction.client.config['colors']['info']
        )
        await channel.send(embed=embed)
        await channel.send(f"{staff_role.mention if staff_role else '@Staff'} Nowy ticket pomocy!")

        await interaction.response.send_message(f"✅ Utworzono ticket: {channel.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Tickets(bot))
