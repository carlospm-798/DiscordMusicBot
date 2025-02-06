import os
import discord
import yt_dlp as youtube_dl
from discord.ext import commands
from dotenv import load_dotenv

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

# Comando para reproducir música desde YouTube con streaming
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

# Iniciar el bot
bot.run(TOKEN)



'''import os
import discord
import asyncio
import yt_dlp as youtube_dl
from discord.ext import commands
from dotenv import load_dotenv

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

# Lista de reproducción
queue = []






# Comando para unirse a un canal de voz
@bot.command(name="join")
async def join(ctx):
    global voice_client
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        await ctx.send(f"🔊 Conectado a {channel.name}")
    else:
        await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")






# Función para descargar y reproducir una canción (se ejecuta por cada canción)
async def download_and_play(song, ctx):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",  # Guardar el archivo temporalmente
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # Obtener metadata de la canción
        info = await asyncio.to_thread(ydl.extract_info, song['url'], download=True)
        audio_url = f"downloads/{info['id']}.mp3"  # Ruta del archivo descargado

    # Reproducir la canción
    voice_client.play(discord.FFmpegPCMAudio(audio_url), after=lambda e: print(f"Reproducción terminada: {e}"))

    while voice_client.is_playing():  # Esperar a que termine de reproducir
        await asyncio.sleep(1)

    return True  # Indicamos que la canción terminó




# Comando para reproducir música
@bot.command(name="play")
async def play(ctx, url: str):
    global voice_client, queue

    if voice_client is None or not voice_client.is_connected():
        await ctx.send("❌ No estoy en un canal de voz. Usa `!join` primero.")
        return

    await ctx.send(f"🎵 Buscando: {url}")

    ydl_opts = {"format": "bestaudio/best", "noplaylist": False}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        if "entries" in info:  # Si es una playlist
            queue.extend(info["entries"])  # Agregar canciones a la cola
            await ctx.send(f"📃 Se agregaron {len(info['entries'])} canciones a la cola.")
        else:
            queue.append(info)  # Agregar una sola canción
            await ctx.send(f"▶️ Se agregó a la cola: {info['title']}")

    # Iniciar reproducción si no está en curso
    if not voice_client.is_playing() and queue:
        await play_queue(ctx)  # Ejecutar reproducción de la cola




async def play_queue(ctx):
    global voice_client, queue

    while queue:  # Mientras haya canciones en la cola
        current_song = queue.pop(0)  # Obtener la primera canción
        await ctx.send(f"🎶 Reproduciendo: {current_song['title']}")

        # Reproducir la canción, sin bloquear el flujo de ejecución
        await download_and_play(current_song, ctx)

    await ctx.send("✅ Cola finalizada.")





        
async def play_next(ctx):
    global voice_client, queue, current_song_index

    if current_song_index >= len(queue):  # Si ya no hay canciones
        await ctx.send("✅ Cola finalizada.")
        return

    song = queue[current_song_index]  # Obtener la canción actual
    current_song_index += 1  # Avanzar el contador para la siguiente

    with youtube_dl.YoutubeDL({"format": "bestaudio/best"}) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, song["url"], download=False)
        audio_url = info["url"]

    voice_client.stop()
    voice_client.play(discord.FFmpegPCMAudio(audio_url), 
                      after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

    await ctx.send(f"🎶 Reproduciendo ahora: {song['title']} ({current_song_index}/{len(queue)})")

             





# Comando para pausar la música
@bot.command(name="pause")
async def pause(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("⏸️ Música pausada.")
    else:
        await ctx.send("❌ No hay música reproduciéndose.")

# Comando para reanudar la música pausada
@bot.command(name="resume")
async def resume(ctx):
    global voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("▶️ Música reanudada.")
    else:
        await ctx.send("❌ No hay música pausada.")

# Comando para saltar la canción actual
@bot.command(name="skip")
async def skip(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # Por ahora solo detiene la canción actual
        await ctx.send("⏭️ Canción saltada.")
    else:
        await ctx.send("❌ No hay música reproduciéndose.")

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
- `!pause` → Pausa la música.
- `!resume` → Reanuda la reproducción de música pausada.
- `!stop` → Detiene la música.
- `!skip` → Salta a la siguiente canción.

¡Disfruta de la música! 🎵
"""
    await ctx.send(help_message)


# Iniciar el bot
bot.run(TOKEN)
'''