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

    try:
        print("collection already exists, deleting")
        client.delete_collection("lyrics-embeddings")
    except Exception as e:
        print("Deleting collection failed: ", e)

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
        chunk_size=400, #50
        chunk_overlap=80, #20
        length_function=len,
        is_separator_regex=False,
    )

    texts = [doc.page_content for doc in raw_docs]
    metadatas = [doc.metadata for doc in raw_docs]

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


# vector_store = initialiseChromaClient()
# addDataToVectorStore(vector_store=vector_store)

# singAI = ChatBot(vector_store=vector_store)
# final_response = singAI.enhanceText(userMessage="""
# Two weeks ago, I walked across the stage at my convocation, and it still doesn't feel real. For the past four years, getting on the DHL was the dream that seemed to always slip out of my hands. Semester after semester, I would push myself to the limit, staying up on weekends, missing out on gatherings, telling myself that this time, maybe, I'd finally make it. And every time I got close, something would happen; a grade lower than I expected, an assignment that didn't go the way I had planned, or just pure bad luck. It felt like a cycle of running harder and harder but always stumbling right before the finish line. There were moments where I wondered if all this effort even made sense, if maybe I was chasing something I wasn't meant to reach.\n What kept me going through those years were the people around me. My friends never stopped believing. They would cheer me on after every exam, they would tell me I had what it takes even when I felt like giving up. There were nights when I thought I couldn't take another setback, and a simple message from them would pull me back. They saw something in me I couldn't always see in myself, and that faith became my safety net. Without realizing it, they were carrying me forward every time I thought I was about to collapse.\n In my final year, something shifted. I stopped obsessing over the DHL. I told myself that if it happened, it would be a wonderful blessing, but if it didn't, I would still walk away proud of the effort I had given. I decided not to make it the center of my happiness anymore. And with that mindset, the burden somehow felt lighter. I could focus on the work itself instead of just the outcome. I didn't talk about it at home, not even with my parents. In fact, they had no idea what was coming. I wanted it to be a surprise, one final chapter in this journey that they could witness firsthand without carrying the weight of my struggles.\n And then, against all odds, it happened. The announcement came, and I saw my name on the DHL list. For a moment, I just stared, unable to process that the thing I had been chasing for four years was finally mine. It felt like all those tiny battles had finally come together in one victory.\n On convocation day, when my parents found out, the look on their faces made every single struggle worth it. They were surprised, proud, maybe even a little shocked, and in that moment, I felt like I had given them a gift that was years in the making. Walking off that stage, I realized this was proof of resilience, of faith, of persistence. It was a reminder that sometimes the journey matters as much as the destination.\n Today, I carry this achievement with a full heart. Grateful for the friends who carried me when I was falling, proud of the resilience that kept me standing, and humbled by the reminder that even when it feels impossible, sometimes the story ends better than you could have imagined.""")
