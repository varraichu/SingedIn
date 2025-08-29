import chardet
import os

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        detector = chardet.universaldetector.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']

path = './lyrics/'
files_list = os.listdir(path=path)

for file in files_list:
    file_path = os.path.join(path, file)
    
    # Detect encoding
    encoding = detect_encoding(file_path)

    if encoding and encoding.lower() != "utf-8":
        print(f"Converting {file} from {encoding} → utf-8")

        # Read full binary content
        with open(file_path, "rb") as f:
            raw = f.read()

        # Decode using detected encoding
        text = raw.decode(encoding, errors="replace")

        # Re-write in UTF-8
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

    # encoding = detect_encoding(file_path)
    # print(f'The encoding of the file is: {encoding}')
