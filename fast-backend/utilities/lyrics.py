import os
import json
import time

from lyricsgenius import Genius
from langdetect import detect
from dotenv import load_dotenv

from helpers.lyrics_helper import clean_lyrics, detect_encoding, extract_unique_non_verse_sections

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
    retries=3    
)

data2 = []

# Make sure output folder exists
LYRICS_DIR = os.path.join(BASE_DIR, "..", "lyrics_chorus")
EMPTY_DIR = os.path.join(BASE_DIR, "..", "empty_lyrics_chorus")
NON_ENGLISH_DIR = os.path.join(BASE_DIR,"..", "non_english_lyrics_chorus")

os.makedirs(LYRICS_DIR, exist_ok=True)
os.makedirs(EMPTY_DIR, exist_ok=True)
os.makedirs(NON_ENGLISH_DIR, exist_ok=True)

def fetchLyricsForSongs():
    for idx, liked_song in enumerate(data, start=1):
        song_name = liked_song["name"]
        artist = liked_song["artist"]

        # Sanitize filename
        safe_artist = "".join(c for c in artist if c.isalnum() or c in " _-").strip()
        safe_song = "".join(c for c in song_name if c.isalnum() or c in " _-").strip()
        file_name = f"{safe_artist}_{safe_song}.txt"

        # Skip if already saved
        if (os.path.exists(os.path.join(LYRICS_DIR, file_name)) or 
            os.path.exists(os.path.join(EMPTY_DIR, file_name)) or
            os.path.exists(os.path.join(NON_ENGLISH_DIR, file_name))):
            print(f"⏩ Skipping {song_name} by {artist} (already saved)")
            continue

        try:
            print(f"[{idx}/{len(data)}] Searching for {song_name} by {artist}...")
            song = genius.search_song(song_name, artist)

            if song:
                # print("lyrics: ", song.lyrics, "\n")
                # cleaned_lyrics = clean_lyrics(song.lyrics)
                # print("cleaned lyrics: ", cleaned_lyrics, "\n")
            
                formattedLyrics = extract_unique_non_verse_sections(song.lyrics)
                # print("formatted lyrics: ", formattedLyrics, "\n")
                if not formattedLyrics:
                    file_path = os.path.join(EMPTY_DIR, file_name)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(formattedLyrics)
                    print(f"Empty lyrics saved for {song_name} by {artist}")
                    continue
                
                try:
                    lang = detect(formattedLyrics)
                    if lang != "en":
                        file_path = os.path.join(NON_ENGLISH_DIR, file_name)
                        print(f"Non-English lyrics detected for {song_name} by {artist}")
                    else:
                        file_path = os.path.join(LYRICS_DIR, file_name)
                except Exception as e:
                    print("error detecting file language: ", e)
                    file_path = os.path.join(LYRICS_DIR, file_name)



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