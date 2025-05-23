import wavelink
from discord.ext import commands
from utils import get_player, MAX_TRACKS

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx):
        player = await get_player(ctx)
        await ctx.send(f"Conectado a {ctx.author.voice.channel.name}")

    @commands.command(name="leave")
    async def leave(self, ctx):
        player = ctx.voice_client
        if player and isinstance(player, wavelink.Player):
            await player.disconnect()
            if hasattr(player, "custom_queue"):
                del player.custom_queue
                del player.queue_index
            await ctx.send("Desconectado y cola limpiada.")
        else:
            await ctx.send("No estoy en ningún canal de voz.")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        player = await get_player(ctx)

        if not hasattr(player, "custom_queue"):
            player.custom_queue = []
            player.queue_index = -1

        tracks = await wavelink.Playable.search(search)
        if not tracks:
            return await ctx.send("No tracks found.")

        if isinstance(tracks, wavelink.Playlist):
            for t in tracks.tracks[:MAX_TRACKS]:
                player.custom_queue.append(t)
            await ctx.send(f"Added playlist: {tracks.name} ({len(player.custom_queue)} tracks)")
        else:
            track = tracks[0]
            player.custom_queue.append(track)
            await ctx.send(f"Added to queue: {track.title}")

        if not player.playing:
            player.queue_index = 0
            await player.play(player.custom_queue[0])

    @commands.command(name="next")
    async def skip(self, ctx):
        """Salta a la siguiente canción en la cola."""
        player = await get_player(ctx)

        # DEBUG START
        print("DEBUG !next:")
        print("  queue_index =", player.queue_index)
        print("  queue titles =", [t.title for t in player.custom_queue])
        print("  queue length =", len(player.custom_queue))
        # DEBUG END     


        if not hasattr(player, "custom_queue"):
            return await ctx.send("No music is playing.")

        if player.queue_index + 1 < len(player.custom_queue):
            player.queue_index += 1

            nxt = player.custom_queue[player.queue_index]
            await player.play(nxt)
            await ctx.send(f"Now playing: {nxt.title}")
        else:
            await ctx.send("There are no more songs in the queue.")

    @commands.command(name="prev")
    async def back(self, ctx):
        """Vuelve a la canción anterior en la cola."""
        player = await get_player(ctx)

        # DEBUG START
        print("DEBUG !next:")
        print("  queue_index =", player.queue_index)
        print("  queue titles =", [t.title for t in player.custom_queue])
        print("  queue length =", len(player.custom_queue))
        # DEBUG END     

        if not hasattr(player, "custom_queue"):
            return await ctx.send("No music is playing.")

        if player.queue_index > 0:
            player.queue_index -= 1
            prev_track = player.custom_queue[player.queue_index]
            await player.play(prev_track)
            await ctx.send(f"Now playing: {prev_track.title}")
        else:
            await ctx.send("There are no previous songs in the queue.")

async def setup(bot):
    await bot.add_cog(Music(bot))
