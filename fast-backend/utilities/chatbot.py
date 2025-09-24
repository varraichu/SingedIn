import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

from dotenv import load_dotenv

load_dotenv()

# Access variables
api_key = os.getenv("OPENAI_API_KEY")



# def custom_text_loader(file_path):
#     return TextLoader(file_path, encoding="utf-8")

text_loader_kwargs = {"autodetect_encoding": True}

loader = DirectoryLoader('../lyrics/', glob="**/*.txt", show_progress=True, loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
raw_docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=50,
    chunk_overlap=20,
    length_function=len,
    is_separator_regex=False,
)

texts = [doc.page_content for doc in raw_docs]
metadatas = [doc.metadata for doc in raw_docs]

chunks = text_splitter.create_documents(texts=texts, metadatas=metadatas)
print(len(chunks))

vector_db = Chroma(
    collection_name='lyics',
    database='my_chroma_db',    
)

vector_store = vector_db.from_documents(chunks, OpenAIEmbeddings(model='text-embedding-3-small'))

# print(vector_store.get(include=["embeddings", "metadatas"]))  
llm = ChatOpenAI(
    model="gpt-4o-mini",  # or "gpt-4o", depending on budget
    temperature=0.7
)

#plain retriever
retriever = vector_store.as_retriever(   
    search_type='mmr',
    search_kwargs={"k": 3}
)

#multi-query retriever
multi_query_retriever = MultiQueryRetriever.from_llm(

    retriever=vector_store.as_retriever(), llm=llm

)


#compression retriever
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(

    base_compressor=compressor, base_retriever=retriever

)

sentence_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=0,
    separators=["\n\n", ".", "!", "?"]
)

paragraph = """
Two weeks ago, I walked across the stage at my convocation, and it still doesn't feel real. For the past four years, getting on the DHL was the dream that seemed to always slip out of my hands. Semester after semester, I would push myself to the limit, staying up on weekends, missing out on gatherings, telling myself that this time, maybe, I'd finally make it. And every time I got close, something would happen; a grade lower than I expected, an assignment that didn't go the way I had planned, or just pure bad luck. It felt like a cycle of running harder and harder but always stumbling right before the finish line. There were moments where I wondered if all this effort even made sense, if maybe I was chasing something I wasn't meant to reach.\n What kept me going through those years were the people around me. My friends never stopped believing. They would cheer me on after every exam, they would tell me I had what it takes even when I felt like giving up. There were nights when I thought I couldn't take another setback, and a simple message from them would pull me back. They saw something in me I couldn't always see in myself, and that faith became my safety net. Without realizing it, they were carrying me forward every time I thought I was about to collapse.\n In my final year, something shifted. I stopped obsessing over the DHL. I told myself that if it happened, it would be a wonderful blessing, but if it didn't, I would still walk away proud of the effort I had given. I decided not to make it the center of my happiness anymore. And with that mindset, the burden somehow felt lighter. I could focus on the work itself instead of just the outcome. I didn't talk about it at home, not even with my parents. In fact, they had no idea what was coming. I wanted it to be a surprise, one final chapter in this journey that they could witness firsthand without carrying the weight of my struggles.\n And then, against all odds, it happened. The announcement came, and I saw my name on the DHL list. For a moment, I just stared, unable to process that the thing I had been chasing for four years was finally mine. It felt like all those tiny battles had finally come together in one victory.\n On convocation day, when my parents found out, the look on their faces made every single struggle worth it. They were surprised, proud, maybe even a little shocked, and in that moment, I felt like I had given them a gift that was years in the making. Walking off that stage, I realized this was proof of resilience, of faith, of persistence. It was a reminder that sometimes the journey matters as much as the destination.\n Today, I carry this achievement with a full heart. Grateful for the friends who carried me when I was falling, proud of the resilience that kept me standing, and humbled by the reminder that even when it feels impossible, sometimes the story ends better than you could have imagined."""

sentence_chunks = sentence_splitter.split_text(paragraph)
print(len(sentence_chunks))
# print(sentence_chunks)

results = []
    
for i, chunk in enumerate(sentence_chunks):
    # print(f"Processing chunk {i+1}/{len(sentence_chunks)}: {chunk[:50]}...")
    print(f"Processing chunk {i+1}/{len(sentence_chunks)}")
        
    # Retrieve similar lyrics for this chunk
    
    # similar_lyrics = retriever.invoke(chunk)

    # similar_lyrics = multi_query_retriever.invoke(chunk)

    similar_lyrics = compression_retriever.invoke(chunk)
        
    chunk_result = {
        "chunk_index": i,
        "original_chunk": chunk,
        "retrieved_lyrics": []
    }
        
    # Process retrieved documents
    for j, doc in enumerate(similar_lyrics):
        lyric_info = {
            "content": doc.page_content,
            "metadata": doc.metadata,  # filename, source info, etc.
            "rank": j + 1
        }
        chunk_result["retrieved_lyrics"].append(lyric_info)
        
    results.append(chunk_result)

# print(results)



prompt = ChatPromptTemplate.from_template("""
You are rewriting a paragraph in a playful remix style.

Original sentence:
{sentence}

Candidate lyric lines:
{lyrics}

Instructions:
- If a lyric fits naturally, rewrite the sentence with that lyric inserted.
- If none fit, return the original sentence unchanged.
- Keep the overall tone consistent with the paragraph (storytelling, reflective, LinkedIn style).
- Do not add extra lyrics beyond the candidates.
- Change the grammar of the lyric to match the tense of the original sentence.
""")

chain = prompt | llm

final_sentences = []

for chunk_result in results:
    sentence = chunk_result["original_chunk"]
    lyrics = [l["content"] for l in chunk_result["retrieved_lyrics"]]
    # Join top lyrics into one string
    lyrics_text = "\n".join(f"- {lyric}" for lyric in lyrics)
    
    # lyrics = []
    # for l in chunk_result["retrieved_lyrics"]:
    #     content = l["content"]
    #     metadata = l["metadata"]
    #     # you can pick which metadata fields you care about
    #     # e.g. filename or artist
    #     source = metadata.get("source", "unknown")
    
    #     lyrics.append(f"- \"{content}\" (from: {source})")

    # lyrics_text = "\n".join(lyrics)

    
    
    # Run LLM chain
    response = chain.invoke({
        "sentence": sentence,
        "lyrics": lyrics_text
    })
    
    final_sentences.append(response.content.strip())

final_paragraph = " ".join(final_sentences)
print(final_paragraph)


# docs = retriever.invoke(sentence_chunks)
# print(docs)
