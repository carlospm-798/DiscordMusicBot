#   --------------------------------------------------------------------------      #
#   message:            Message just return a text that would be send to            #
#                       the user, when he ask to the commands.                      #
#   --------------------------------------------------------------------------      #

def message():

    help_message = """
    📜 **Commands list** 📜

    **🎤 Basic commands**
    - `!join` → Joins the bot to the discord voice channel.
    - `!leave` → Push out the bot of the discord voice channel.
    - `!play < + SoundCloud URL>` → Add a song or a playlist to the queue.
    - `!pause` → Pause the actual song.
    - `!play` → Re-runs the actual song.
    - `!next` → Reproduce the next song of the queue.
    - `!prev` → Reproduce the past song of the queue.

    ¡Enjoy the music! 🎵
    """

    return help_message