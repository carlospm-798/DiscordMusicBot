#   | Soundcloud Music bot for Discord.
#   | Carlos P.M. + ChatGPT o4-mini-high model.
#   | 05 23, 2025.

import os
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands

#   --------------------------------------------------------------------------      #
#   os:         Used to access the environment variables.                           #
#   asyncio:    Used to manage the loop of the python events,                       #
#               to work with async functions.                                       #
#   discord:    Main library of Discord.py                                          #
#                                                                                   #
#   dotenv.load_dotenv():    To use the variables that were defined in a .env       #
#   commands:   It's a submodule that facilitates the creation of bots,             #
#               based in commands and cogs.                                         #
#   --------------------------------------------------------------------------      #

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN_exp")

#   --------------------------------------------------------------------------      #
#   load_dotenv():      Loads the environment variables of a .env file.             #
#   TOKEN:              Saves the token of the discord app. It's a safe way to      #
#                       not save the token in the script.                           #
#   --------------------------------------------------------------------------      #

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

#   --------------------------------------------------------------------------      #
#   intents:            Helps to optimized the resources and improve the            #
#                       privacy. It just send to the user the events that           #
#                       are explicity open by the "intents". Without correct        #
#                       intents, the bot cannot receive some events.                #
#   --------------------------------------------------------------------------      #

bot = commands.Bot(command_prefix='!', 
                   help_command=None,
                   intents=intents)

#   --------------------------------------------------------------------------      #
#   commands.Bot:       It's a subclass of discord.Client to facilitates the        #
#                       creation of bots based on commands.                         #
#                       We have an acces of API events as an example:               #
#                       on_message, on_voice_state_update, etc.                     #
#   command_prefix:     Takes the preficx !, and the name of the command.           #
#   help_command:       When we uses 'None', we can set our !help command,          #
#                       instead of uses the discord help command.                   #
#   --------------------------------------------------------------------------      #

async def main():
    async with bot:
        await bot.load_extension("cogs.music")
        await bot.load_extension("cogs.events")
        await bot.start(TOKEN)

#   --------------------------------------------------------------------------      #
#   main:               In this case is an asyn function.                           #
#   async with bot:     It opens an automatic context that executes that call       #
#                       to bot.login() and bot.close(), to clean the conections.    #
#   .load_extension:    Loads music and events before running.                      #
#   .start:             Connects the bot to Discord, and starts the loop of         #
#                       events.                                                     #
#   --------------------------------------------------------------------------      #

if __name__ == "__main__":
    asyncio.run(main())