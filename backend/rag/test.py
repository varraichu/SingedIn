from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

DB_DIR = "chroma_db"

embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma(
    collection_name="lyrics",
    embedding_function=embed,
    persist_directory=DB_DIR,
)

query = "Hey guys! Back in June I graduated from LUMS with a DHL! Yes! I was finally on the DHL!!! After months of struggling and always coming so close to it, I finally did it. One way or another, my plans were always thwarted. I remember in Spring 23, I came so close to having the DHL, but it just wasn't the right time. In senior year, I had lost all hopes for being on the DHL, but I did not give up. Part of me still wanted to give it a shot. So I worked hard on the weekends. My friends really supported me throughout the journey and believed in me more than I did. I am extremely proud of this achievement."
results = vectordb.similarity_search(query, k=5)

for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content}  | {doc.metadata}")
