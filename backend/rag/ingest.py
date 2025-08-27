# rag/ingest.py
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# paths
LYRICS_DIR = "lyrics"   # where your .txt files are
DB_DIR = "chroma_db"    # persistent vector store

# embeddings
embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# chroma collection
vectordb = Chroma(
    collection_name="lyrics",
    embedding_function=embed,
    persist_directory=DB_DIR,
)

# splitter (line-level but with some context)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,    # ~ one or two lines
    chunk_overlap=30,
    separators=["\n"]
)

docs, metas = [], []

for fname in os.listdir(LYRICS_DIR):
    if fname.endswith(".txt"):
        with open(os.path.join(LYRICS_DIR, fname), encoding="utf-8") as f:
            text = f.read().strip()
        if not text:
            continue

        # derive metadata
        song = os.path.splitext(fname)[0]   # filename as fallback
        artist, title = None, song
        if "_" in song:
            artist, title = song.split("_", 1)

        # split into chunks
        chunks = splitter.split_text(text)
        docs.extend(chunks)
        metas.extend([{"artist": artist, "title": title, "file": fname}] * len(chunks))

print(f"Prepared {len(docs)} chunks from {len(os.listdir(LYRICS_DIR))} files.")

# add to DB
BATCH_SIZE = 5000
for i in range(0, len(docs), BATCH_SIZE):
    batch_docs = docs[i:i+BATCH_SIZE]
    batch_metas = metas[i:i+BATCH_SIZE]
    vectordb.add_texts(texts=batch_docs, metadatas=batch_metas)
    print(f"Inserted {i + len(batch_docs)} / {len(docs)} chunks...")

print("✅ Ingestion complete. Data persisted to chroma_db/")
