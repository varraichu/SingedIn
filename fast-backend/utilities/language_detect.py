from langdetect import detect
import os
import shutil

path = "lyrics"
non_english_path = "non-english-lyrics"
empty_path = "empty-lyrics"

os.makedirs(non_english_path, exist_ok=True)
os.makedirs(empty_path, exist_ok=True)

non_english = []
empty_files = []

for file in os.listdir(path):
    if not file.endswith(".txt"):
        continue

    src_path = os.path.join(path, file)

    # skip if it's already moved
    if not os.path.isfile(src_path):
        continue

    with open(src_path, encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        empty_files.append(file)
        shutil.move(src_path, os.path.join(empty_path, file))
        continue

    try:
        lang = detect(text)
        if lang != "en":
            non_english.append((file, lang))
            shutil.move(src_path, os.path.join(non_english_path, file))
    except Exception as e:
        non_english.append((file, "unknown"))
        shutil.move(src_path, os.path.join(non_english_path, file))

print("Non-English files count:", len(non_english))
for flop in non_english:
    print(flop)

print("Empty files count:", len(empty_files))
for boo in empty_files:
    print(boo)
