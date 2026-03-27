import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

class TapForceBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("Commandes synchronisées !")

bot = TapForceBot()

@bot.event
async def on_ready():
    print(f'Bot connecté avec succès en tant que {bot.user}')
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


bot.run(TOKEN)