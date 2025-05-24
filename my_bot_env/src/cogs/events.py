import yaml
import wavelink
from pathlib import Path
from discord.ext import commands
from bot_commands import message as get_help_message

#   --------------------------------------------------------------------------      #
#   yaml:               yaml + Path help us to read the content, in a secure        #
#                       way, of the file application.yml                            #
#   wavelink:           Is the python client to connect to your lavalink            #
#                       server, and reproduce music.                                #
#   commands:           It's a discord submodule that provide a command system.     #
#   get_help_message:   It's the function that I use to send the available          #
#                       commands as a string.                                       #
#   --------------------------------------------------------------------------      #

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        if msg.content.strip().lower() == "!help":
            await msg.channel.send(get_help_message())
            return

#   --------------------------------------------------------------------------      #
#   on_message:             It filter all the messages send by the user, and        #
#                           when the command its !help, send back the commands      #
#                           that are available at that time in the bot.             #
#   --------------------------------------------------------------------------      #


    @commands.Cog.listener()
    async def on_ready(self):
        cfg_path = Path(__file__).parent.parent / "application.yml"
        cfg = yaml.safe_load(cfg_path.read_text())

        server_cfg = cfg["server"]
        host    = server_cfg["host"]
        port    = server_cfg["port"]       

        lavalink_srv = cfg.get("lavalink", {}).get("server", {})
        password    = lavalink_srv.get("password", "")

        print(f'Bot conectado como {self.bot.user} — Lavalink en {host}:{port}')
        node = wavelink.Node(
            uri=f"http://{host}:{port}",
            password=password
        )
        await wavelink.Pool.connect(client=self.bot, nodes=[node])

#   --------------------------------------------------------------------------      #
#   on_ready:           When the bot its connected, it shoots this function
#                       onces, taking the data of application.yml, then it 
#                       creates an object wavelink.Node and connects the 
#                       bot with to that node.
#   --------------------------------------------------------------------------      #



    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        track  = payload.track
        reason = payload.reason.lower()

        if reason != "finished":
            return

        print(f"Track ended: {track.title}, reason: {reason}")

        if not hasattr(player, "custom_queue") or not hasattr(player, "queue_index"):
            print("Player has no queue data.")
            return

        if player.queue_index + 1 < len(player.custom_queue):
            player.queue_index += 1

            next_track = player.custom_queue[player.queue_index]
            print(f"Now auto-playing: {next_track.title}")
            await player.play(next_track)
        else:
            print("End of queue reached.")

#   --------------------------------------------------------------------------      #
#   on_wavelonk_track_end:      It gets active once that a song finished, to        #
#                               advance to the next song.                           #
#   --------------------------------------------------------------------------      #

async def setup(bot):
    await bot.add_cog(Events(bot))

#   --------------------------------------------------------------------------      #
#   add_cog:            It creates and load an instance of Events, and then it      #
#                       registers to the bot, making available all the events.      #
#   --------------------------------------------------------------------------      #