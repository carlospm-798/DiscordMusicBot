import random
import wavelink
from discord.ext import commands
from utils import get_player, MAX_TRACKS

#   --------------------------------------------------------------------------      #
#   wavelink:           Is the client that interact with the Lavalink server,       #
#                       and reproduces audio.                                       #
#   commands:           It's the dicord submodule that offers us a command          #
#                       system and cogs.                                            #
#   get_player:         It's an utility in utils.py that returns a wavelink.Player  #
#                       asociate with the voice channel.                            #
#   MAX_TRACKS:         It's a constant the limits the number of the songs          #
#                       in the playlist.                                            #
#   --------------------------------------------------------------------------      #

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx):
        player = await get_player(ctx)
        await ctx.send(f"Connected {ctx.author.voice.channel.name}")

#   --------------------------------------------------------------------------      #
#   join:       It creates or reconnect the Player and take it to the voice         #
#               channel of the user. Finally, it sends a message to the user        #
#               that confirms the connection.                                       #
#   --------------------------------------------------------------------------      #

    @commands.command(name="leave")
    async def leave(self, ctx):
        player = ctx.voice_client
        if player and isinstance(player, wavelink.Player):
            await player.disconnect()
            if hasattr(player, "custom_queue"):
                del player.custom_queue
                del player.queue_index
            await ctx.send("Disconnected")
        else:
            await ctx.send("I'm not in a voice channel")

#   --------------------------------------------------------------------------      #
#   leave:      It recover a Player directly from the voice channel, and if it      #
#               exists and its a waveink.Player, it disconnect it with a await      #
#               player.disconnect(). Then it cleans the attributes custom_queue     #
#               and queue_index to reset the queue.                                 #
#   --------------------------------------------------------------------------      #

    @commands.command(name="pause")
    async def pause(self, ctx):
        player = await get_player(ctx)
        
        try:
            await player.pause(True)
        except Exception as e:
            print(f"[ERROR] player.pause() raised: {e}")
            return await ctx.send(f"❌ Error during the pause: `{e}`")
        
        await ctx.send("⏸️ Pause")

#   --------------------------------------------------------------------------      #
#   pause:      It pauses the actual song using a True value, adding an try exept   #
#               bloc, to catch any lavalink error.
#   --------------------------------------------------------------------------      #

    @commands.command(name="play")
    async def play(self, ctx, *, search: str = None):
        player = await get_player(ctx)

        if search is None:
            if player.paused:
                await player.pause(False)
                return await ctx.send("▶️ Playing")
            return await ctx.send("You should indicate and URL if I'm not in pause")
            

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

#   --------------------------------------------------------------------------      #
#   play:       If the bot is not reproducing anything, it start with the first     #
#               song of the queue. If there's a URL, it adds a song or a playlist.  #
#               Without arguments, checks it is in pause, so then pass a False to   #
#               pause for continue the reproduction..                               #
#   --------------------------------------------------------------------------      #

    @commands.command(name="next")
    async def skip(self, ctx):
        player = await get_player(ctx)   

        if not hasattr(player, "custom_queue"):
            return await ctx.send("No music is playing.")

        if player.queue_index + 1 < len(player.custom_queue):
            player.queue_index += 1

            nxt = player.custom_queue[player.queue_index]
            await player.play(nxt)
            await ctx.send(f"Now playing: {nxt.title}")
        else:
            await ctx.send("There are no more songs in the queue.")

#   --------------------------------------------------------------------------      #
#   skip:       It validates that a custom_queue exists, and advance to the next    #
#               song, notifying to the channel.                                     #
#   --------------------------------------------------------------------------      #

    @commands.command(name="prev")
    async def back(self, ctx):
        player = await get_player(ctx)   

        if not hasattr(player, "custom_queue"):
            return await ctx.send("No music is playing.")

        if player.queue_index > 0:
            player.queue_index -= 1
            prev_track = player.custom_queue[player.queue_index]
            await player.play(prev_track)
            await ctx.send(f"Now playing: {prev_track.title}")
        else:
            await ctx.send("There are no previous songs in the queue.")

#   --------------------------------------------------------------------------      #
#   skip:       It validates that a custom_queue exists, and advance to the         #
#               past song, notifying to the channel.                                #
#   --------------------------------------------------------------------------      #

    @commands.command(name="stop")
    async def stop(self, ctx):

        player = await get_player(ctx)

        if getattr(player, "playing", False) or getattr(player, "paused", False):
            await player.stop()
        
        if hasattr(player, "custom_queue"):
            player.custom_queue.clear()
            player.queue_index = -1
        
        await ctx.send("⏹️ Reproducción detenida y cola vaciada.")

#   --------------------------------------------------------------------------      #
#   stop:       It check that there's a playlist, and then it cleans all the        #
#               queue.
#   --------------------------------------------------------------------------      #

    @commands.command(name="shuffle")
    async def shuffle(self, ctx):

        player = await get_player(ctx)

        if not hasattr(player, "custom_queue") or not player.custom_queue:
            return await ctx.send("❌ No hay música en la cola para mezclar.")
        
        current = player.queue_index

        already_played = player.custom_queue[: current + 1]
        to_shuffle = player.custom_queue[current + 1 :]

        random.shuffle(to_shuffle)

        player.custom_queue = already_played + to_shuffle

        await ctx.send("🔀 ¡Cola mezclada aleatoriamente a partir de la pista actual!")

        if not to_shuffle:
            return await ctx.send("❌ No hay canciones pendientes para mezclar.")
        
#   --------------------------------------------------------------------------      #
#   shuffle:        Takes the songs that are not played yet, and mixes it           #
#                   in a random way.                                                #
#   --------------------------------------------------------------------------      #


async def setup(bot):
    await bot.add_cog(Music(bot))

#   --------------------------------------------------------------------------      #
#   setup:      It adds an instance to the bot to activate all the                  #
#               available commands.                                                 #
#   --------------------------------------------------------------------------      #