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


async def reproduce(ctx):
    global voice_client
    if not song_queue.empty():
        song_info = await song_queue.get()
        await ctx.send(f"▶️ Reproduciendo: {song_info['title']}")

        def after_playing(error):
            if error:
                print(f"Error en la reproducción: {error}")
            bot.loop.create_task(reproduce(ctx))

        voice_client.play(
            discord.FFmpegPCMAudio(song_info["url"]),
            after=after_playing
        )


@bot.command(name="join")
async def join(ctx):
    global voice_client
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        await ctx.send(f"🔊 Conectado a {channel.name}")
    else:
        await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")


@bot.command(name="add")
async def add(ctx, url: str):
    global voice_client
    if voice_client is None or not voice_client.is_connected():
        await ctx.send("❌ No estoy en un canal de voz. Usa `!join` primero.")
        return

    await ctx.send(f"🎵 Agregando: {url}")

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

        audio_url = info["url"]  # URL para streaming
        song_info = {
            "title": info["title"],
            "url": audio_url
        }
        await song_queue.put(song_info)

    # Reproducir la URL de audio directamente
    voice_client.stop()
    voice_client.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: print(f"Reproducción terminada: {e}"))
    await ctx.send(f"▶️ Reproduciendo: {info['title']}")

'''
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
        "noplaylist": True,  # Evita descargar playlists completas
        "default_search": "ytsearch",  # Permite buscar por nombre si no es un link
        "quiet": True,  # Reduce logs innecesarios
    }

    # Extraer la URL del audio sin descargar
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]  # URL para streaming

    # Reproducir la URL de audio directamente
    voice_client.stop()
    voice_client.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: print(f"Reproducción terminada: {e}"))
    await ctx.send(f"▶️ Reproduciendo: {info['title']}")
'''

@bot.command(name="stop")
async def stop(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("⏹️ Música detenida.")
    else:
        await ctx.send("❌ No hay música reproduciéndose.")


@bot.command(name="leave")
async def leave(ctx):
    global voice_client
    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send("👋 Desconectado del canal de voz.")
    else:
        await ctx.send("❌ No estoy en un canal de voz.")


@bot.command(name="commands")
async def commands_list(ctx):
    help_message = """
📜 **Lista de Comandos** 📜

**🎤 Comandos Básicos**
- `!join` → Hace que el bot se una al canal de voz.
- `!leave` → Expulsa al bot del canal de voz.

**🎶 Comandos de Reproducción**
- `!add <URL>` → Agrega una canción a la cola y la reproduce si no hay música.
- `!stop` → Detiene la música.

¡Disfruta de la música! 🎵
"""
    await ctx.send(help_message)


bot.run(TOKEN)
