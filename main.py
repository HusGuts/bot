import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import json
import random
import re

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
        print("Commands and Buttons sync!")

bot = TapForceBot()

@bot.event
async def on_ready():
    print(f'Bot connected: {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Tap Force Bot"))

# ==========================================
# COMMANDES DE FACTION ET BIENVENUE
# ==========================================

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
    channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, name="🙋╎ɢᴇɴᴇʀᴀʟ-ᴄʜᴀᴛ")
    if channel:
        embed = discord.Embed(title="🥊 New Member!", description=f"Welcome {member.mention}!", color=discord.Color.gold())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Step 1", value="Use `/faction`", inline=False)
        embed.add_field(name="Step 2", value="Read the rules <#1496975331033088130>", inline=False)
        embed.add_field(name="Step 3", value="Read and react to annoucements", inline=False)
        await channel.send(embed=embed)

# ==========================================
# MINI-JEU WHO IS ET LEADERBOARD
# ==========================================

def load_scores():
    try:
        with open("scores.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_score(user_id, points):
    scores = load_scores()
    user_id = str(user_id)
    scores[user_id] = scores.get(user_id, 0) + points
    with open("scores.json", "w") as f:
        json.dump(scores, f, indent=4)

class GuessModal(discord.ui.Modal, title="Who is this character?"):
    answer = discord.ui.TextInput(label="Character Name", placeholder="Enter the name here...", min_length=2, max_length=50)

    def __init__(self, correct_name, file_path):
        super().__init__()
        self.correct_name = correct_name.lower()
        self.file_path = file_path

    async def on_submit(self, interaction: discord.Interaction):
        user_answer = self.answer.value.strip().lower()
        
        if user_answer == self.correct_name:
            points_gained = 10
            save_score(interaction.user.id, points_gained)
            await interaction.response.send_message(f"✅ Well done {interaction.user.mention}! It was indeed **{self.correct_name.capitalize()}**. You win {points_gained} points!", ephemeral=False)
        else:
            await interaction.response.send_message(f"❌ Wrong answer {interaction.user.mention}! Try your luck next time.", ephemeral=True)

class WhoIsView(discord.ui.View):
    def __init__(self, correct_name, file_path):
        super().__init__(timeout=60)
        self.correct_name = correct_name
        self.file_path = file_path

    @discord.ui.button(label="Guess!", style=discord.ButtonStyle.primary)
    async def guess_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GuessModal(self.correct_name, self.file_path))
        self.stop()

@bot.tree.command(name="whois", description="Start a mini-game to guess the character!")
async def whois(interaction: discord.Interaction):
    path = "./WhoIs"
    files = [f for f in os.listdir(path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        return await interaction.response.send_message("The WhoIs folder is empty!", ephemeral=True)

    chosen_file = random.choice(files)
    character_name = re.sub(r'\d+', '', chosen_file.split('.')[0]).strip()
    
    file = discord.File(f"{path}/{chosen_file}", filename="image.png")
    embed = discord.Embed(title="Who is this character?", color=discord.Color.orange())
    embed.set_image(url="attachment://image.png")
    
    await interaction.response.send_message(file=file, embed=embed, view=WhoIsView(character_name, chosen_file))

@bot.tree.command(name="leaderboard", description="Show the top players")
async def leaderboard(interaction: discord.Interaction):
    scores = load_scores()
    if not scores:
        return await interaction.response.send_message("No scores yet!", ephemeral=True)

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    
    description = ""
    for i, (user_id, score) in enumerate(sorted_scores, 1):
        description += f"**{i}.** <@{user_id}> - {score} points\n"

    embed = discord.Embed(title="🏆 WhoIs Leaderboard", description=description, color=discord.Color.gold())
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)