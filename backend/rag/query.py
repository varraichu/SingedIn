# rag/remix.py
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# load env
load_dotenv()
DB_DIR = "chroma_db"

# vector store
embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma(
    collection_name="lyrics",
    embedding_function=embed,
    persist_directory=DB_DIR,
)

# llm
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# prompt
prompt = ChatPromptTemplate.from_template("""
You are a playful writer who takes normal text and spices it up with famous song lyrics.  
Given the user's text and some related lyric snippets, rewrite the text by replacing or blending sentences with those lyrics. Append the artist and the song name in brackets next to the line you replaced it. Add as many relevant lyrics as you can to make the whole text fun.

USER TEXT:
{text}

LYRICS SNIPPETS:
{lyrics}

Now write the remixed version:
""")

def lyrical_remix(user_text: str, k: int = 5) -> str:
    # retrieve top lyric hits
    results = vectordb.similarity_search(user_text, k=k)

    # format with metadata
    formatted = []
    for doc in results:
        meta = doc.metadata
        artist = meta.get("artist", "Unknown Artist")
        title = meta.get("title", meta.get("file", "Unknown Title"))
        formatted.append(f"{doc.page_content.strip()}\n  — {artist} | {title}")

    lyric_snips = "\n\n".join(formatted)

    print("---- lyric_snips ----")
    print(lyric_snips)

    # run chain
    chain = prompt | llm
    resp = chain.invoke({"text": user_text, "lyrics": lyric_snips})
    return resp.content



if __name__ == "__main__":
    user_text = "The past quarter has been one of the most exhausting yet transformative stretches of my life. It started with a clear plan, but like all plans, reality had other intentions. Deadlines shifted, expectations grew heavier, and the simple to-do list on my desk turned into an avalanche of tasks. I found myself running from one meeting to the next, drafting slides on airplanes, and trying to catch up on code reviews late at night when the rest of the city was asleep. There were weeks when I didn't know whether I was moving forward or just running in circles. I'd wake up with my laptop on the bed and realize I had fallen asleep answering emails. The line between weekdays and weekends completely vanished.\n But in the middle of the chaos, there were moments that reminded me why I chose this path. A colleague's random message telling me that my small contribution had unblocked their entire team. The adrenaline rush of demo day when the product we had struggled with for months finally came to life in front of stakeholders. The pride in hearing our clients say that what we had built was going to change how they worked. Those sparks of light became my fuel, even when exhaustion pulled me down.\n Still, it wasn't just work. Life outside the office was shifting too. Friends I hadn't seen in months reached out, and we laughed over memories that made the late nights feel less lonely. I found comfort in long walks under streetlights, where the city hummed with stories bigger than mine. Music played the role it always does: my silent companion, blasting through my headphones when I needed to drown out doubt, or quietly reminding me of resilience when I was on the verge of breaking. I kept returning to those moments when a song lyric felt like it was written just for me, like the universe was whispering, 'You're not alone, keep going.'\n As the quarter comes to a close, I've realized it wasn't just about checking boxes or surviving the grind. It was about resilience, about learning to dance with uncertainty, about finding strength in struggle. There's still more work ahead — the road doesn't magically get easier. But now I carry with me the reminder that growth doesn't come in comfort; it comes in the late nights, the missed weekends, the times you doubt yourself and still choose to show up. And when I look ahead, I feel strangely hopeful. Because if I can make it through this season, carrying both the weight and the lessons, then maybe I'm stronger than I ever gave myself credit for."
    remix = lyrical_remix(user_text)
    print("----- Remix -----")
    print(remix)
