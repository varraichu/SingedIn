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

class ChatBot:
    def __init__(self, vector_store):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # or "gpt-4o", depending on budget
            temperature=0.7
        )

        #plain retriever
        self.retriever = vector_store.as_retriever(   
            search_type='mmr',
            search_kwargs={"k": 3}
        )

        #multi-query retriever
        self.multi_query_retriever = MultiQueryRetriever.from_llm(

            retriever=vector_store.as_retriever(), llm=self.llm
        )

        #compression retriever
        compressor = LLMChainExtractor.from_llm(self.llm)
        self.compression_retriever = ContextualCompressionRetriever(

            base_compressor=compressor, base_retriever=self.retriever

        )

        self.sentence_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=0,
            separators=["\n\n", ".", "!", "?"]
        )

        self.prompt = ChatPromptTemplate.from_template("""
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
    
    def retrieveLyrics(self,userMessage):
        sentence_chunks = self.sentence_splitter.split_text(userMessage)
        print("sentence chunks = ",len(sentence_chunks))
        # print(sentence_chunks)

        results = []
            
        for i, chunk in enumerate(sentence_chunks):
            # print(f"Processing chunk {i+1}/{len(sentence_chunks)}: {chunk[:50]}...")
            print(f"Processing chunk {i+1}/{len(sentence_chunks)}")
                
            # Retrieve similar lyrics for this chunk
            
            # similar_lyrics = retriever.invoke(chunk)

            # similar_lyrics = multi_query_retriever.invoke(chunk)

            similar_lyrics = self.compression_retriever.invoke(chunk)
                
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

        return results

    def enhanceText(self, userMessage):
        chain = self.prompt | self.llm

        fetchedLyrics = self.retrieveLyrics(userMessage)

        final_sentences = []

        for chunk_result in fetchedLyrics:
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
        return final_paragraph