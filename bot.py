import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

class TapForceBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(CreateTicketView())
        self.add_view(CloseTicketView())
        await self.tree.sync()
        print("Commands and Boutons sync !")

bot = TapForceBot()

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="🔒 Close ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class CreateTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create a ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket_btn")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_modo = discord.utils.get(interaction.guild.roles, name="Co-Leader")
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), 
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        if role_modo:
            overwrites[role_modo] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"ticket-{interaction.user.name}"
        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            reason=f"Ticket create by {interaction.user}"
        )

        await interaction.response.send_message(f"Your ticket has been create : {ticket_channel.mention}", ephemeral=True)

        # Envoie le message d'accueil dans le nouveau ticket
        embed = discord.Embed(
            title="📞 Club Support",
            description=f"Hey {interaction.user.mention} !\nSomeone will answer you.\nExplain your problem.\n\n*To close this ticket, click the red button below.*",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketView())

@bot.event
async def on_ready():
    print(f'Bot connected perfect {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Tap Force Bot"))

@bot.tree.command(name="faction", description="Choose your favourite faction !")
@app_commands.choices(choix=[
    app_commands.Choice(name="Mantis", value="Mantis"),
    app_commands.Choice(name="Kodiak", value="Kodiak"),
    app_commands.Choice(name="Howler", value="Howler"),
    app_commands.Choice(name="Crane", value="Crane"),
    app_commands.Choice(name="Cobra", value="Cobra"),
    app_commands.Choice(name="Griffin", value="Griffin")])

async def faction(interaction: discord.Interaction, choix: app_commands.Choice[str]):
    nom_role = choix.value
    
    role = discord.utils.get(interaction.guild.roles, name=nom_role)
    
    if role is None:
        await interaction.response.send_message(f"This role **{nom_role}** doesnt exist. Faction didnt exist or admin are lazy !", ephemeral=True)
        return

    if role in interaction.user.roles:
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"You left the faction **{nom_role}**.", ephemeral=True)
    else:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"Welcome to the faction **{nom_role}** !", ephemeral=True)

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    
    if channel is None:
        channel = discord.utils.get(member.guild.text_channels, name="🙋╎𝖦𝖾𝗇𝖾𝗋𝖺𝗅-𝖢𝗁𝖺𝗍╎")

    if channel is not None:
        embed = discord.Embed(
            title="🥊A new member has joined !",
            description=f"Welcome {member.mention} on Stampede Of Fury Club !",
            color=discord.Color.gold())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Step 1", value="Use  command `/faction` too choose your favourite faction.", inline=False)
        embed.add_field(name="Step 2", value="Read the Rules !", inline=False)
        embed.set_footer(text="Enjoy !")
        
        await channel.send(embed=embed)

@bot.tree.command(name="setup_ticket", description="[Staff] Install the ticket panel")
@app_commands.default_permissions(manage_channels=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Support Center",
        description="Need help, have a question for the staff, or want to report an issue?\nClick the button below to open a private ticket.",
        color=discord.Color.dark_theme()
    )
    await interaction.channel.send(embed=embed, view=CreateTicketView())
    
    await interaction.response.send_message("Panel successfully installed!", ephemeral=True)

bot.run(TOKEN)