import os
import chardet
import shutil
import re

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


def extract_unique_non_verse_sections(text: str) -> str:
    lines = text.splitlines()
    output = []
    seen_sections = set()
    current_section = None
    buffer = []

    for line in lines:
        header_match = re.match(r'^\[(.+?)\]', line.strip())

        if header_match:
            # when new section starts, decide whether to keep the previous one
            if current_section and current_section not in seen_sections and not current_section.lower().startswith("verse"):
                # remove headers from buffer before adding
                cleaned = [l for l in buffer if not re.match(r'^\[.+?\]', l.strip())]
                output.extend(cleaned)
                seen_sections.add(current_section)

            current_section = header_match.group(1)
            buffer = [line]
        else:
            buffer.append(line)

    # handle last section
    if current_section and current_section not in seen_sections and not current_section.lower().startswith("verse"):
        cleaned = [l for l in buffer if not re.match(r'^\[.+?\]', l.strip())]
        output.extend(cleaned)

    # join and clean up
    return "\n".join(line.strip() for line in output if line.strip())