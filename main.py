import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import webserver

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
print(f"Token from .env: {os.getenv('DISCORD_TOKEN')}")

print("Loading environment variables...")
load_dotenv()
print("Environment variables loaded.")

print("Creating bot instance...")
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
print("Bot instance created.")
bot.owner_ids = {1384859365349003264}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    webserver.start_web_server()
    await bot.load_extension('src.cogs.general')
    await bot.load_extension('src.cogs.moderation')
    await bot.load_extension('src.cogs.utility')
    await bot.load_extension('src.cogs.giveaway')
    await bot.load_extension('src.cogs.tickets')
    await bot.load_extension('src.cogs.welcome')
    await bot.load_extension('src.cogs.autorole')
    await bot.load_extension('src.cogs.levels')
    await bot.load_extension('src.cogs.protection')
    await bot.load_extension('src.cogs.backup')

    await bot.load_extension('src.cogs.embed_creator')
    await bot.load_extension('src.cogs.moderation_panel')
    await bot.load_extension('src.cogs.support')
    await bot.load_extension('src.cogs.history')
    await bot.load_extension('src.cogs.interactions')
    await bot.load_extension('src.cogs.ticket_list')
    await bot.load_extension('src.cogs.alt_checker') # Load the new alt checker cog

    print(f"Total Cogs Loaded: {len(bot.cogs)}")
    print(f"Total Commands Loaded: {len(bot.commands)}")

    try:
        synced = await bot.tree.sync()
        print(f"Comandos Globais Sincronizados (Inicialização): {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar comandos na inicialização: {e}")

@bot.command()
@commands.is_owner()
async def reload(ctx, cog: str):
    """Reloads a cog."""
    try:
        await bot.unload_extension(cog)
        await bot.load_extension(cog)
        await ctx.send(f"Cog {cog} reloaded.")
    except Exception as e:
        await ctx.send(f"Error reloading cog {cog}: {e}")

print("Running the bot...")
try:
    bot.run(os.getenv('DISCORD_TOKEN'))
except Exception as e:
    print(f"Erro ao rodar o bot: {e}")
print("Bot finished running.")
