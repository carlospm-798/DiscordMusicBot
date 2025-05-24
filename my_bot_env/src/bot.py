import os
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN_exp")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', 
                   help_command=None,
                   intents=intents)

async def main():
    async with bot:
        # aquí cargamos los cogs DEFINITIVAMENTE antes de arrancar
        await bot.load_extension("cogs.music")
        await bot.load_extension("cogs.events")
        # y ahora sí, arrancamos el bot
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
