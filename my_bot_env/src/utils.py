import wavelink
from discord.ext import commands

MAX_TRACKS = 100

async def get_player(ctx) -> wavelink.Player:
    if isinstance(ctx.voice_client, wavelink.Player):
        return ctx.voice_client

    if ctx.author.voice and ctx.author.voice.channel:
        return await ctx.author.voice.channel.connect(cls=wavelink.Player)

    raise commands.CommandError("You must be in a voice channel.")
