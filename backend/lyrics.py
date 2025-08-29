from lyricsgenius import Genius
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

# Load liked songs JSON
with open("liked_songs2.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Genius API token
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
        if not start:
            if "Lyrics" in line:
                start = True
            continue
        if line.strip().startswith("[") and line.strip().endswith("]"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

# Genius client
genius = Genius(
    token,
    timeout=60,                 
    remove_section_headers=True,
    retries=3    
)

data2 = []

# Make sure output folder exists
os.makedirs("lyrics", exist_ok=True)

for idx, liked_song in enumerate(data, start=1):
    song_name = liked_song["name"]
    artist = liked_song["artist"]

    # Sanitize filename
    safe_artist = "".join(c for c in artist if c.isalnum() or c in " _-").strip()
    safe_song = "".join(c for c in song_name if c.isalnum() or c in " _-").strip()
    file_name = f"{safe_artist}_{safe_song}.txt"
    file_path = os.path.join("lyrics", file_name)

    # Skip if already saved
    if os.path.exists(file_path):
        print(f"⏩ Skipping {song_name} by {artist} (already saved)")
        continue

    try:
        print(f"[{idx}/{len(data)}] Searching for {song_name} by {artist}...")
        song = genius.search_song(song_name, artist)

        if song:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_lyrics(song.lyrics))
            print(f"✅ Saved lyrics for {song_name} by {artist}")
        else:
            data2.append(liked_song)
            print(f"❌ Lyrics not found for {song_name} by {artist}")

    except Exception as e:
        print(f"⚠️ Error with {song_name} by {artist}: {e}")

    # Delay to avoid rate-limiting
    time.sleep(1)

with open("missing_lyrics.json", "w", encoding="utf-8") as new_file:
    json.dump(data2, new_file, ensure_ascii=False, indent=4)


# song_name = "Life is good"
# artist = "Future"

#     # Sanitize filename
# safe_artist = "".join(c for c in artist if c.isalnum() or c in " _-").strip()
# safe_song = "".join(c for c in song_name if c.isalnum() or c in " _-").strip()
# file_name = f"{safe_artist}_{safe_song}.txt"
# file_path = os.path.join("lyrics", file_name)

# # Skip if already saved
# if os.path.exists(file_path):
#     print(f"⏩ Skipping {song_name} by {artist} (already saved)")

# try:
#     song = genius.search_song(song_name, artist)

#     if song:
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(clean_lyrics(song.lyrics))
#         print(f"✅ Saved lyrics for {song_name} by {artist}")
#     else:
#         print(f"❌ Lyrics not found for {song_name} by {artist}")

# except Exception as e:
#     print(f"⚠️ Error with {song_name} by {artist}: {e}")

#     # Delay to avoid rate-limiting
# time.sleep(1)