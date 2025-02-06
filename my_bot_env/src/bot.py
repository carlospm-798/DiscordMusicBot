import os
import discord
import yt_dlp as youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
from asyncio import Queue

# Cargar el token desde .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

# Crear el bot con prefijo "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# Variable global para la conexión de voz
voice_client = None

song_queue = Queue()




@bot.command(name="queue_length")
async def queue_length(ctx):
    length = song_queue.qsize()
    await ctx.send(f"🎵 Hay {length} canciones en la cola.")





async def play_next(ctx):
    if not song_queue.empty():
        song_info = await song_queue.get()
        print(f"Reproduciendo siguiente canción: {song_info}")
        await ctx.send(f"▶️ Reproduciendo: {song_info['title']}")

        def after_playing(error):
            if error:
                print(f"Error en la reproducción: {error}")
            bot.loop.create_task(play_next(ctx))

        voice_client.play(
            discord.FFmpegPCMAudio(song_info["url"]),
            after=after_playing
        )


# Comando para unirse a un canal de voz
@bot.command(name="join")
async def join(ctx):
    global voice_client
    if ctx.author.voice:  # Verifica si el usuario está en un canal de voz
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        await ctx.send(f"🔊 Conectado a {channel.name}")
    else:
        await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")



@bot.command(name="play")
async def play(ctx, url: str):
    global voice_client
    if voice_client is None or not voice_client.is_connected():
        await ctx.send("❌ No estoy en un canal de voz. Usa `!join` primero.")
        return

    await ctx.send(f"🎵 Buscando: {url}")

    # Configuración de yt-dlp para obtener la URL de streaming sin descargar
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,  # Permite manejar listas manualmente
        "default_search": "ytsearch",  # Permite buscar por nombre si no es un link
        "quiet": True,  # Reduce logs innecesarios
    }

    # Extraer la URL del audio sin descargar
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print(f"Información extraída: {info}")

        # Si es una playlist, extraer las URLs manualmente
        if "entries" in info:
            for entry in info["entries"]:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl_entry:
                    entry_info = ydl_entry.extract_info(entry["webpage_url"], download=False)
                    audio_url = entry_info["url"]  # URL para streaming
                    song_info = {
                        "title": entry_info["title"],
                        "url": audio_url
                    }
                    await song_queue.put(song_info)
                    print(f"Agregada a la cola: {song_info}")
        else:  # Si es una sola canción
            audio_url = info["url"]  # URL para streaming
            song_info = {
                "title": info["title"],
                "url": audio_url
            }
            await song_queue.put(song_info)
            print(f"Agregada a la cola: {song_info}")

    # Reproducir la primera canción en la cola si no hay reproducción en curso
    if not voice_client.is_playing():
        await play_next(ctx)
        





# Comando para omitir a la siguiente canción
@bot.command(name="skip")
async def skip(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        voice_client.cleanup()  # Asegúrate de que el proceso ffmpeg se limpia adecuadamente
    await ctx.send("⏩ Canción omitida.")
    if not song_queue.empty():
        await play_next(ctx)






# Comando para detener la música
@bot.command(name="stop")
async def stop(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("⏹️ Música detenida.")
    else:
        await ctx.send("❌ No hay música reproduciéndose.")





# Comando para desconectar el bot del canal de voz
@bot.command(name="leave")
async def leave(ctx):
    global voice_client
    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send("👋 Desconectado del canal de voz.")
    else:
        await ctx.send("❌ No estoy en un canal de voz.")



@bot.command(name="commands")  # Comandos
async def commands_list(ctx):
    help_message = """
📜 **Lista de Comandos** 📜

**🎤 Comandos Básicos**
- `!join` → Hace que el bot se una al canal de voz.
- `!leave` → Expulsa al bot del canal de voz.

**🎶 Comandos de Reproducción**
- `!play <URL>` → Reproduce audio desde una URL de YouTube.
- `!stop` → Detiene la música.

¡Disfruta de la música! 🎵
"""
    await ctx.send(help_message)



# Iniciar el bot
bot.run(TOKEN)
