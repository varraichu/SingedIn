import os
import chardet
import shutil

from langdetect import detect

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


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        detector = chardet.universaldetector.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']