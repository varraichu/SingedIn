import os
import json
import time

from lyricsgenius import Genius
from langdetect import detect
from dotenv import load_dotenv

from helpers.lyrics_helper import clean_lyrics, detect_encoding

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "..", "files")
FILES_DIR = os.path.abspath(FILES_DIR)
LIKED_SONGS_PATH = os.path.join(FILES_DIR, "liked_songs.json")

# Load liked songs JSON
with open(LIKED_SONGS_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

# Genius API token
token = os.getenv("GENIUS_ACCESS_TOKEN")

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
os.makedirs("empty_lyrics", exist_ok=True)
os.makedirs("non_english_lyrics", exist_ok=True)

def fetchLyricsForSongs():
    for idx, liked_song in enumerate(data, start=1):
        song_name = liked_song["name"]
        artist = liked_song["artist"]

        # Sanitize filename
        safe_artist = "".join(c for c in artist if c.isalnum() or c in " _-").strip()
        safe_song = "".join(c for c in song_name if c.isalnum() or c in " _-").strip()
        file_name = f"{safe_artist}_{safe_song}.txt"

        # Skip if already saved
        if (os.path.exists(os.path.join("lyrics", file_name)) or 
            os.path.exists(os.path.join("empty_lyrics", file_name)) or
            os.path.exists(os.path.join("non_english_lyrics", file_name))):
            print(f"⏩ Skipping {song_name} by {artist} (already saved)")
            continue

        try:
            print(f"[{idx}/{len(data)}] Searching for {song_name} by {artist}...")
            song = genius.search_song(song_name, artist)

            if song:
                formattedLyrics = clean_lyrics(song.lyrics)
                
                if not formattedLyrics:
                    file_path = os.path.join("empty_lyrics", file_name)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(formattedLyrics)
                    print(f"Empty lyrics saved for {song_name} by {artist}")
                    continue
                
                try:
                    lang = detect(formattedLyrics)
                    if lang != "en":
                        file_path = os.path.join("non_english_lyrics", file_name)
                        print(f"Non-English lyrics detected for {song_name} by {artist}")
                    else:
                        file_path = os.path.join("lyrics", file_name)
                except Exception as e:
                    print("error detecting file language: ", e)
                    file_path = os.path.join("lyrics", file_name)



                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(formattedLyrics)

                encoding = detect_encoding(file_path=file_path)
                if encoding and encoding.lower() != "utf-8":
                    print(f"Converting {file_path} from {encoding} → utf-8")

                    # Read full binary content
                    with open(file_path, "rb") as f:
                        raw = f.read()

                    # Decode using detected encoding
                    text = raw.decode(encoding, errors="replace")

                    # Re-write in UTF-8
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(text) 

                print(f"✅ Saved lyrics for {song_name} by {artist}")
            else:
                data2.append(liked_song)
                print(f"❌ Lyrics not found for {song_name} by {artist}")

        except Exception as e:
            print(f"⚠️ Error with {song_name} by {artist}: {e}")

        # Delay to avoid rate-limiting
        time.sleep(1)
    
    MISSING_SONGS_PATH = os.path.join(FILES_DIR, "missing_songs.json")
    with open(MISSING_SONGS_PATH, "w", encoding="utf-8") as new_file:
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