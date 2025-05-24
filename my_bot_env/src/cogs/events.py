import yaml
import wavelink
from pathlib import Path
from discord.ext import commands
from bot_commands import message as get_help_message

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        if msg.content.strip().lower() == "!help":
            help_text = get_help_message()
            await msg.channel.send(help_text)
            return                          # <— aquí detenemos el flujo

        # solo procesamos otros comandos
        await self.bot.process_commands(msg)



    @commands.Cog.listener()
    async def on_ready(self):
        # Ruta al application.yml
        cfg_path = Path(__file__).parent.parent / "application.yml"
        cfg = yaml.safe_load(cfg_path.read_text())

        server_cfg = cfg["server"]
        host    = server_cfg["host"]
        port    = server_cfg["port"]       

        # Sección 'lavalink.server'
        lavalink_srv = cfg.get("lavalink", {}).get("server", {})
        password    = lavalink_srv.get("password", "")

        print(f'Bot conectado como {self.bot.user} — Lavalink en {host}:{port}')
        node = wavelink.Node(
            uri=f"http://{host}:{port}",
            password=password
        )
        await wavelink.Pool.connect(client=self.bot, nodes=[node])
        


    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        # Se dispara al terminar una pista
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

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        # Debug de todos los mensajes entrantes del gateway
        print("SOCKET RESPONSE:", msg)

async def setup(bot):
    await bot.add_cog(Events(bot))