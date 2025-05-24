import wavelink
from discord.ext import commands

#   --------------------------------------------------------------------------      #
#   wavelink:           Is the client that interact with the Lavalink server,       #
#                       and reproduces audio.                                       #
#   commands:           It's a submodule that facilitates the creation of bots,     #
#                       based in commands and cogs.                                 #
#   --------------------------------------------------------------------------      #

MAX_TRACKS = 100

#   --------------------------------------------------------------------------      #
#   MAX_TRACKS:         Is a constant that defines the max value of songs in        #
#                       total, to avoid gigant lists.                               #
#   --------------------------------------------------------------------------      #

async def get_player(ctx) -> wavelink.Player:
    if isinstance(ctx.voice_client, wavelink.Player):
        return ctx.voice_client

    if ctx.author.voice and ctx.author.voice.channel:
        return await ctx.author.voice.channel.connect(cls=wavelink.Player)

    raise commands.CommandError("You must be in a voice channel.")

#   --------------------------------------------------------------------------      #
#   get_player:         It's an async helper that unify all the lógic               #
#                       to create or use the audio reproduction for the bot.        #
#   --------------------------------------------------------------------------      #