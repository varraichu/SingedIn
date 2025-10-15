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

from nltk.tokenize import sent_tokenize

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
            retriever=vector_store.as_retriever(
                search_type='mmr',
                search_kwargs={
                    "k": 20,
                "score_threshold": 0.9,
                "lambda_mult": 0.75,
                }
            ), llm=self.llm
        )

        #compression retriever
        compressor = LLMChainExtractor.from_llm(self.llm)

        self.embeddings_filter = EmbeddingsFilter(embeddings=OpenAIEmbeddings(model="text-embedding-3-small"), similarity_threshold=0.7)

        self.compression_retriever = ContextualCompressionRetriever(
            # base_compressor=self.embeddings_filter, base_retriever=self.retriever
            base_compressor=compressor, base_retriever=self.retriever
        )

        self.sentence_splitter = RecursiveCharacterTextSplitter(
            chunk_size=250,
            chunk_overlap=0,
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
You are rewriting a sentence in a playful remix style while maintaining narrative flow.

Context for tone and grammar:
Previous sentence: {previous_sentence}
Next sentence: {next_sentence}

Original sentence to modify:
{sentence}

Candidate lyric lines with sources:
{lyrics}

Instructions:
- Use the previous and next sentences ONLY to understand the narrative tone, tense, and grammatical flow. DO NOT modify them.
- ALWAYS format ANY inserted lyrics as: *lyric text*. No exceptions.
- Change the grammar of the lyric to match the tense and perspective of the original sentence (e.g., past to present, third person to first person, etc.).
- Ensure the modified sentence flows naturally when read between the previous and next sentences.
- Maintain consistent tone with the surrounding context (storytelling, reflective, LinkedIn style).
- If none of the lyrics fit naturally, return the original sentence unchanged.
- If no lyrics are provided, return the original sentence exactly.
- NEVER add extra lyrics beyond the candidates provided.
- NEVER change the song name, it's capitalization or grammar.
- The modified sentence should feel like a seamless part of the paragraph, not a jarring insertion.

Example output format:
{{
    'original_sentence': 'I fulfilled my goals, and for that I am really proud of myself', 
    'lyrics': "I'm so, I'm so, I'm so, I'm so, I'm so proud of you\\nI'm so, I'm so, I'm so, I'm so, I'm so proud of you", 
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

        self.prompt_second_pass = ChatPromptTemplate.from_template("""
            You are taking an array with chunks of sentences, and fixing their grammar so that the final sentences match the original paragraph sent.
        Original Paragraph:
        {paragraph}

        Array with sentences:
        {array}
                                                                                                                                                        Instructions:
- Fix grammar/flow in the modified_sentence fields only
- Keep all other fields (original_sentence, lyrics, song_name) unchanged
- Maintain the ** markers around lyric-influenced text
""")
            



    def retrieveLyrics(self, userMessage):
        # sentence_chunks = self.sentence_splitter.split_text(userMessage)
        sentence_chunks = sent_tokenize(userMessage)
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

    def secondPass(self, userMessage, firstPassOutput):
        chain = self.prompt_second_pass | self.llm.with_structured_output(self.schema)
        try:
            response = chain.invoke({
                        "paragraph": userMessage,
                        "array": firstPassOutput
                    })
            print("second pass response: ", response)
            return response
        except Exception as e:
            return {"error: ", str(e)}

    def enhanceText(self, userMessage):
        chain = self.prompt | self.llm.with_structured_output(self.schema)

        fetchedLyrics = self.retrieveLyrics(userMessage)

        final_sentences = []

        for i, chunk_result in enumerate(fetchedLyrics):
            previous_sentence = ""
            next_sentence = ""
            if i != 0:
                previous_sentence = fetchedLyrics[i-1]["original_chunk"]
            
            if i != len(fetchedLyrics)-1:
                next_sentence = fetchedLyrics[i+1]["original_chunk"]

            sentence = chunk_result["original_chunk"]
            print(f"prev: {previous_sentence}\n")            
            print(f"next: {next_sentence}\n")            
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
                        "previous_sentence": previous_sentence,
                        "next_sentence": next_sentence,
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
        # final_response = self.secondPass(userMessage, final_sentences)
        # print("\n")
        # print("Grande finale",final_response)
        return final_sentences
    
    def retrieveLyricsForFullText(self, userMessage):

        similar_lyrics = self.multi_query_retriever.invoke(userMessage)
        chunk_result = []
                
        for j, doc in enumerate(similar_lyrics):
            lyric_info = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "rank": j + 1
            }
            chunk_result.append(lyric_info)
        print(f"Retrieval length: {len(chunk_result)}")
        print(chunk_result)
        return chunk_result

    def singText(self, userMessage):
        chain = self.prompt | self.llm.with_structured_output(self.schema)

        fetchedLyrics = self.retrieveLyricsForFullText(userMessage)
        print("\n")
        print(f"fetched lyrics length: {len(fetchedLyrics)}")
        print("\n")
        final_sentences = []

        lyrics = []
        for chunk_result in fetchedLyrics:
            sentence = userMessage
            print(f"chunk result: {chunk_result}, \n")
            
            # Format lyrics with song title/source information
            content = chunk_result["content"]
            metadata = chunk_result["metadata"]
                
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
                print(f"\n{'='*50}")
                print(f"SENTENCE: {sentence}")
               
                print(f"lyrics length: {len(lyrics)}")
                print(f"{'='*50}\n")

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
        # final_response = self.secondPass(userMessage, final_sentences)
        print("\n")
        # print("Grande finale",final_response)
        return final_sentences
        # return final_response