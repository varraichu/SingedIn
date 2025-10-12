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
from langchain.retrievers.document_compressors import LLMChainExtractor, EmbeddingsFilter

from langchain.globals import set_debug, set_verbose

from dotenv import load_dotenv

load_dotenv()

# set_debug(True)

# Access variables
api_key = os.getenv("OPENAI_API_KEY")

class ChatBot:
    def __init__(self, vector_store):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )

        #plain retriever
        self.retriever = vector_store.as_retriever(   
            search_type='mmr',
            search_kwargs={
                "k": 3,
                "score_threshold": 0.9,
                "lambda_mult": 0.75,
            }
        )

        #multi-query retriever
        self.multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=vector_store.as_retriever(), llm=self.llm
        )

        #compression retriever
        compressor = LLMChainExtractor.from_llm(self.llm)

        self.embeddings_filter = EmbeddingsFilter(embeddings=OpenAIEmbeddings(model="text-embedding-3-small"), similarity_threshold=0.7)

        self.compression_retriever = ContextualCompressionRetriever(
            # base_compressor=self.embeddings_filter, base_retriever=self.retriever
            base_compressor=compressor, base_retriever=self.retriever
        )

        self.sentence_splitter = RecursiveCharacterTextSplitter(
            chunk_size=150,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "?"]
        )
        
        self.schema = {
                "title": "lyrics_remix",
                "description": "Sentence with the replaced lyric",
                "type": "object",
                "properties": {
                    "original_sentence": {
                        "type": "string",
                        "description": "The original sentence passed by the user",
                    },
                    "lyrics": {
                        "type": "string",
                        "description": "The candidate lyrics passed by the user with their source",
                    },
                    "modified_sentence": {
                        "type": "string",
                        "description": "The sentence infused with the chosen lyrics",
                    },
                    "song_name": {
                        "type": "string",
                        "description": "The name of the song used for infusion.",
                    },
                },
                "required": ["modified_sentence", "song_name"],
            }

        self.prompt = ChatPromptTemplate.from_template("""
You are rewriting a paragraph in a playful remix style.

Original sentence:
{sentence}

Candidate lyric lines with sources:
{lyrics}

Instructions:
- ALWAYS Format ANY inserted lyrics as: *lyric text*. No exceptions.
- Change the grammar of the lyric to match the tense of the original sentence (eg, changing from past to present, third person to first person, etc).
- If none fit, return the original sentence unchanged.
- If no lyrics are provided, repeat the original sentence exactly.
- Keep the overall tone consistent with the paragraph (storytelling, reflective, LinkedIn style).
- NEVER add extra lyrics beyond the candidates.
- NEVER change the song name's capitalisation or grammar.
                                                       
Example output format:
{{
    'original_sentence': 'I fulfilled my goals, and for that I am really proud of myself', 
    'lyrics': "I'm so, I'm so, I'm so, I'm so, I'm so proud of you\nI'm so, I'm so, I'm so, I'm so, I'm so proud of you\nI'm so, I'm so, I'm so, I'm so, I'm so proud of you", 
    'modified_sentence': "I fulfilled my goals, and for that I am really *proud of* myself", 
    'song_name': 'Make Me Proud'
}}
                                                       
Another example:
{{
    'original_sentence': 'They encouraged me when I needed it most',
    'lyrics': 'you believed in me',
    'modified_sentence': 'They *believed in me* when I needed it most',
    'song_name': 'Example Song'
}}
""")
    
    def retrieveLyrics(self, userMessage):
        sentence_chunks = self.sentence_splitter.split_text(userMessage)
        print("sentence chunks = ", len(sentence_chunks))

        results = []
            
        for i, chunk in enumerate(sentence_chunks):
            print(f"Processing chunk {i+1}/{len(sentence_chunks)}")
                
            # similar_lyrics = self.compression_retriever.invoke(chunk)
            similar_lyrics = self.multi_query_retriever.invoke(chunk)
                
            chunk_result = {
                "chunk_index": i,
                "original_chunk": chunk,
                "retrieved_lyrics": []
            }
                
            for j, doc in enumerate(similar_lyrics):
                lyric_info = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "rank": j + 1
                }
                chunk_result["retrieved_lyrics"].append(lyric_info)
                
            results.append(chunk_result)
        # print("results: ", results)
        return results

    def enhanceText(self, userMessage):
        chain = self.prompt | self.llm.with_structured_output(self.schema)

        fetchedLyrics = self.retrieveLyrics(userMessage)

        final_sentences = []

        for chunk_result in fetchedLyrics:
            sentence = chunk_result["original_chunk"]
            
            # Format lyrics with song title/source information
            lyrics = []
            for l in chunk_result["retrieved_lyrics"][:2]:
                content = l["content"]
                metadata = l["metadata"]
                
                # Extract song title from metadata
                # Adjust these keys based on your actual metadata structure
                song_title = metadata.get("song") or metadata.get("title") or metadata.get("source", "Unknown Song")
                
                lyrics.append(f"- \"{content}\" from: {song_title}")

            lyrics_text = "\n".join(lyrics)
            # Run LLM chain
            if lyrics_text == '':
                formatted_output = {
    'original_sentence': sentence, 
    'lyrics': "", 
    'modified_sentence': sentence, 
    'song_name': ''
}
                final_sentences.append(formatted_output)
            elif sentence == '':
                formatted_output = {
    'original_sentence': sentence, 
    'lyrics': "", 
    'modified_sentence': sentence, 
    'song_name': ''
}
                final_sentences.append(formatted_output)
            else:
                # print(f"\n{'='*50}")
                # print(f"SENTENCE: {sentence}")
                # print(f"\nLYRICS:\n{lyrics_text}")
                # print(f"{'='*50}\n")

                # formatted_prompt = self.prompt.format(sentence=sentence, lyrics=lyrics_text)
                # print(f"FORMATTED PROMPT:\n{formatted_prompt}\n")
                # print(f"sentence: {sentence}, lyrics: {lyrics_text}\n")
                try:

                    response = chain.invoke({
                        "sentence": sentence,
                        "lyrics": lyrics_text
                    })
                    # print(response)
                    final_sentences.append(response)
                except Exception as e:
                    return {"error: ", str(e)}
                
                # final_sentences.append(response.content.strip())

        # final_paragraph = " ".join(final_sentences)
        print(final_sentences)
        return final_sentences