from lyricsgenius import Genius
from dotenv import load_dotenv
import os

load_dotenv()

# Get an environment variable
token = os.getenv("GENIUS_ACCESS_TOKEN")
def clean_lyrics(raw_lyrics: str) -> str:
    """
    Removes Genius extra text (contributors, translations, descriptions)
    and returns only the lyrics.
    """
    lines = raw_lyrics.splitlines()
    cleaned_lines = []

    start = False
    for line in lines:
        # Skip empty lines & unwanted headers
        if not start:
            # First real lyric starts after the line containing "Lyrics"
            if "Lyrics" in line:
                start = True
            continue

        # Skip section headers like [Chorus], [Verse] if you want
        if line.strip().startswith("[") and line.strip().endswith("]"):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()

# genius = Genius(token)
genius = Genius(
    token,
    timeout=15,
    remove_section_headers=True,   # removes [Chorus], [Verse] etc.
)

artist = "Charli XCX"
song_name = "365"
song = genius.search_song(song_name, artist)

print(clean_lyrics(song.lyrics))