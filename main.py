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

# --- CLASSES DES VUES ---

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="🔒 Close & Archive", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ⚠️ REMPLACE CES IDS PAR LES TIENS ⚠️
        ID_ARCHIVE_SUPPORT = 1488163475816583279  # Ton ID actuel
        ID_ARCHIVE_BUILD = 1488180429965230130    # Ton NOUVEL ID pour les builds
        NOM_ROLE_MODO = "Co-Leader"
        # ---------------------------------------

        await interaction.response.defer(ephemeral=True)
        
        channel = interaction.channel
        guild = interaction.guild
        
        # Détection du type de ticket par le nom du salon
        if channel.name.startswith("build-"):
            category_id = ID_ARCHIVE_BUILD
            prefix = "📁 Archive Build"
        else:
            category_id = ID_ARCHIVE_SUPPORT
            prefix = "📁 Archive Support"

        category_archive = guild.get_channel(category_id)
        role_modo = discord.utils.get(guild.roles, name=NOM_ROLE_MODO)

        if not category_archive:
            return await interaction.followup.send(f"❌ Error: Archive category ({category_id}) not found.", ephemeral=True)

        # Permissions : Lecture pour Staff, rien pour le joueur
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        if role_modo:
            overwrites[role_modo] = discord.PermissionOverwrite(view_channel=True, send_messages=False)

        try:
            # On renomme et on déplace
            await channel.edit(
                name=f"done-{channel.name}",
                category=category_archive,
                overwrites=overwrites,
                reason=f"Archivé par {interaction.user}"
            )
            
            embed_archive = discord.Embed(
                title=prefix,
                description=f"Ticket closed by : {interaction.user.mention}",
                color=discord.Color.dark_grey()
            )
            await channel.send(embed=embed_archive)
            await interaction.followup.send("✅ Ticket successfully archived.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error during archiving: {e}", ephemeral=True)

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
        ticket_channel = await interaction.guild.create_text_channel(name=channel_name, overwrites=overwrites)

        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title="📞 Club Support",
            description=f"Hey {interaction.user.mention}!\nExplain your problem here.\n\n*Click the red button to archive.*",
            color=discord.Color.green()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketView())

class CreateBuildTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔨 Create Build Ticket", style=discord.ButtonStyle.green, custom_id="create_build_ticket_btn")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_modo = discord.utils.get(interaction.guild.roles, name="Co-Leader")
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), 
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        if role_modo:
            overwrites[role_modo] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"build-{interaction.user.name}"
        ticket_channel = await interaction.guild.create_text_channel(name=channel_name, overwrites=overwrites)

        await interaction.response.send_message(f"Build ticket created: {ticket_channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title="🔨 Build Support",
            description=f"Welcome {interaction.user.mention}!\nTell us which build you need help with.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketView())

# --- CONFIGURATION DU BOT ---

class TapForceBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # On enregistre les 3 vues pour qu'elles restent actives après redémarrage
        self.add_view(CreateTicketView())
        self.add_view(CreateBuildTicketView())
        self.add_view(CloseTicketView())
        await self.tree.sync()
        print("Commands and Buttons sync!")

bot = TapForceBot()

@bot.event
async def on_ready():
    print(f'Bot connected: {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Tap Force Bot"))

# --- COMMANDES SLASH ---

@bot.tree.command(name="setup_ticket", description="[Staff] Install the Support ticket panel")
@app_commands.default_permissions(manage_channels=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Support Center",
        description="Need help? Click the button below to open a private ticket.",
        color=discord.Color.dark_theme()
    )
    await interaction.channel.send(embed=embed, view=CreateTicketView())
    await interaction.response.send_message("Support panel installed!", ephemeral=True)

@bot.tree.command(name="setup_build", description="[Staff] Install the Build ticket panel")
@app_commands.default_permissions(manage_channels=True)
async def setup_build(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔨 Strategy & Builds",
        description="Click below to request help for a specific build.",
        color=discord.Color.blue()
    )
    await interaction.channel.send(embed=embed, view=CreateBuildTicketView())
    await interaction.response.send_message("Build panel installed!", ephemeral=True)

@bot.tree.command(name="faction", description="Choose your favourite faction !")
@app_commands.choices(choix=[
    app_commands.Choice(name="Mantis", value="Mantis"),
    app_commands.Choice(name="Kodiak", value="Kodiak"),
    app_commands.Choice(name="Howler", value="Howler"),
    app_commands.Choice(name="Crane", value="Crane"),
    app_commands.Choice(name="Cobra", value="Cobra"),
    app_commands.Choice(name="Griffin", value="Griffin")])
async def faction(interaction: discord.Interaction, choix: app_commands.Choice[str]):
    role = discord.utils.get(interaction.guild.roles, name=choix.value)
    if role is None:
        return await interaction.response.send_message("Role not found!", ephemeral=True)
    
    if role in interaction.user.roles:
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"You left the faction **{choix.value}**.", ephemeral=True)
    else:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"Welcome to the faction **{choix.value}** !", ephemeral=True)

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, name="🙋╎𝖦𝖾𝗇𝖾𝗋𝖺𝗅-𝖢𝗁𝖺𝗍╎")
    if channel:
        embed = discord.Embed(title="🥊 New Member!", description=f"Welcome {member.mention}!", color=discord.Color.gold())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Step 1", value="Use `/faction`", inline=False)
        await channel.send(embed=embed)

bot.run(TOKEN)