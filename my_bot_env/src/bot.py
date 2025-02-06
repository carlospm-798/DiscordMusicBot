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

# Comando para reproducir música desde YouTube
@bot.command(name="play")
async def play(ctx, url: str):
    global voice_client
    if voice_client is None or not voice_client.is_connected():
        await ctx.send("❌ No estoy en un canal de voz. Usa `!join` primero.")
        return

    await ctx.send(f"🎵 Buscando: {url}")

    # Configuración de yt-dlp para obtener el audio
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": "downloads/%(id)s.%(ext)s",  # Guardar el archivo temporalmente
    }

    # Extraer la información del enlace
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        audio_url = f"downloads/{info['id']}.mp3"  # Ruta del archivo descargado

    # Reproducir el archivo de audio
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
