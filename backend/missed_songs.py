import os
import json

# Load your liked songs JSON
with open("liked_songs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Function to sanitize song/artist like in your lyrics saver
def sanitize(text: str) -> str:
    return "".join(c for c in text if c.isalnum() or c in " _-").strip()

# Build the set of expected filenames
expected_files = set()
for song in data:
    artist = sanitize(song["artist"])
    song_name = sanitize(song["name"])
    file_name = f"{artist}_{song_name}.txt"
    expected_files.add(file_name)

# Get actual files in lyrics folder
lyrics_dir = "lyrics"
actual_files = set(os.listdir(lyrics_dir))

# Compare
missing_files = expected_files - actual_files
extra_files = actual_files - expected_files

# Report
print(f"Total songs in JSON: {len(expected_files)}")
print(f"Files in lyrics folder: {len(actual_files)}")
print(f"Missing lyrics files: {len(missing_files)}")
print(f"Extra/unexpected files: {len(extra_files)}\n")

if missing_files:
    print("🚨 Missing songs:")
    for f in sorted(missing_files):
        print("  -", f)

if extra_files:
    print("\n⚠️ Extra files not in JSON:")
    for f in sorted(extra_files):
        print("  -", f)
