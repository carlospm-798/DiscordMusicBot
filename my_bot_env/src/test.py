#https://www.youtube.com/watch?v=UL7qSFHMON4&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=2
import yt_dlp

def get_playlist_urls(playlist_url, max_videos=5):
    ydl_opts = {
        "noplaylist": False,
        "quiet": True,  # Evita spam en la consola
        "extract_flat": True,  # Extrae solo los metadatos esenciales
        "force_generic_extractor": True,  # Usamos un extractor genérico para evitar detalles adicionales
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        
        if "entries" in info:
            urls = [entry["url"] for entry in info["entries"][:max_videos]]  # Tomar solo las primeras 5
            return urls
        else:
            return info

playlist_url = "https://www.youtube.com/watch?v=UL7qSFHMON4&list=RDGMEMHDXYb1_DDSgDsobPsOFxpA&index=2"
urls = get_playlist_urls(playlist_url)
print(urls)  # Verifica que solo muestra las 5 primeras URLs

