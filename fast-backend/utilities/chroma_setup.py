import chromadb
import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings

from dotenv import load_dotenv

# from chatbot import ChatBot

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")



def initialiseChromaClient():
    print("Setting up chroma db")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_DIR = os.path.join(BASE_DIR, "..", "my_chroma_db")
    client = chromadb.PersistentClient(path=DB_DIR)

    # try:
    #     print("collection already exists, deleting")
    #     client.delete_collection("lyrics-embeddings")
    # except Exception as e:
    #     print("Deleting collection failed: ", e)

    print("creating collection")
    collection = client.get_or_create_collection(name="lyrics-embeddings")
    print("Chroma db setup successfully")

    return Chroma(
        client=client,
        collection_name="lyrics-embeddings",
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    )


def addDataToVectorStore(vector_store):
    text_loader_kwargs = {"autodetect_encoding": True}

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LYRICS_DIR = os.path.join(BASE_DIR, "..", "lyrics")

    loader = DirectoryLoader(LYRICS_DIR, glob="**/*.txt", show_progress=True, loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
    raw_docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200, #50
        chunk_overlap=50, #20
        length_function=len,
        is_separator_regex=False,
    )

    texts = [doc.page_content for doc in raw_docs]
    raw_metadatas = [doc.metadata for doc in raw_docs]
    metadatas = []
    
    for item in raw_metadatas:
        filename = os.path.basename(item['source']).replace('txt', '')
        if "_" in filename:
            artist,song = filename.split("_", 1)
        else:
            artist,song = filename, ''
        safe_song = "".join(c for c in song if c.isalnum() or c in " _-").strip()
        metadatas.append({"artist": artist, "song": safe_song})
    
    # print("metadatas: ", metadatas)
    chunks = text_splitter.create_documents(texts=texts, metadatas=metadatas)
    print(f"Adding {len(chunks)} chunks to chroma db ")
    BATCH_SIZE = 5000
    try:
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i+BATCH_SIZE]
            vector_store.add_documents(documents=batch)
            print(f"Added batch {i//BATCH_SIZE + 1} ({len(batch)} docs)")
        print(f"Added chunks to chroma db ")
    except Exception as e:
        print("Adding chunks failed: ", e)