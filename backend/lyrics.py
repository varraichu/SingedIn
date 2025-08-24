from lyricsgenius import Genius
from dotenv import load_dotenv
import os
import json

load_dotenv()


with open("liked_songs.json", "r",encoding="utf-8") as file:
    data = json.load(file)

# print(data)

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

for liked_song in data:
    song_name = liked_song["name"]
    artist = liked_song["artist"]

    # sanitize filename
    safe_artist = "".join(c for c in artist if c.isalnum() or c in " _-").strip()
    safe_song = "".join(c for c in song_name if c.isalnum() or c in " _-").strip()
    file_name = f"{safe_artist}_{safe_song}.txt"

    song = genius.search_song(song_name, artist)

    if song:  # avoid crash if None
        os.makedirs("lyrics", exist_ok=True)  # make sure folder exists
        with open(f"lyrics/{file_name}", "w", encoding="utf-8") as file:
            file.write(clean_lyrics(song.lyrics))
        print(f"Saved lyrics for {song_name} by {artist}")
    else:
        print(f"❌ Lyrics not found for {song_name} by {artist}")



# print(clean_lyrics(song.lyrics))