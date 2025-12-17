import os

from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.retrievers import MultiQueryRetriever
# from langchain.globals import set_debug, set_verbose


from nltk.tokenize import sent_tokenize

from dotenv import load_dotenv

load_dotenv()

# set_debug(True)

api_key = os.getenv("OPENAI_API_KEY")

class ChatBot:
    def __init__(self, vector_store, temperature: float = 0.3, similarity: float =0.9):
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature
        )

        #multi-query retriever
        self.multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=vector_store.as_retriever(
                search_type='mmr',
                search_kwargs={
                    "k": 20,
                "score_threshold": similarity,
                "lambda_mult": 0.75,
                }
            ), llm=self.llm
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
- CRITICAL: Preserve all [NEWLINE] tokens exactly as they appear in the original sentence
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

    def retrieveLyrics(self, userMessage):
        sentence_chunks = sent_tokenize(userMessage)
        print("sentence chunks = ", len(sentence_chunks))

        results = []
            
        for i, chunk in enumerate(sentence_chunks):
            print(f"Processing chunk {i+1}/{len(sentence_chunks)}")
            if len(chunk) >= 10:    
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
            else:
                chunk_result = {
                    "chunk_index": i,
                    "original_chunk": chunk,
                    "retrieved_lyrics": []
                }
                results.append(chunk_result)
        return results

    def enhanceText(self, userMessage):
        chain = self.prompt | self.llm.with_structured_output(self.schema)
        
        # Step 1: Split by paragraphs but keep track of boundaries
        paragraphs = userMessage.split('\n')
        
        # Step 2: Fetch lyrics for ALL sentences across ALL paragraphs
        all_sentences = []  # Flat list of all sentence chunks
        paragraph_boundaries = []  # Track where each paragraph ends
        
        for para_idx, para in enumerate(paragraphs):
            if not para.strip():  # Skip empty paragraphs
                continue
                
            fetchedLyrics = self.retrieveLyrics(para)
            
            start_idx = len(all_sentences)
            all_sentences.extend(fetchedLyrics)
            end_idx = len(all_sentences)
            
            paragraph_boundaries.append({
                'para_idx': para_idx,
                'start': start_idx,
                'end': end_idx
            })
        
        # Step 3: Process with GLOBAL context (previous/next across paragraphs)
        final_sentences = []
        statistics = {
            "total_sentences": len(all_sentences),
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_cost": 0,
            "total_llm_calls": 0
        }
        
        for i, chunk_result in enumerate(all_sentences):
            previous_sentence = ""
            next_sentence = ""
            
            # Get previous sentence (even from previous paragraph)
            if i > 0:
                previous_sentence = all_sentences[i-1]["original_chunk"]
            
            # Get next sentence (even from next paragraph)
            if i < len(all_sentences) - 1:
                next_sentence = all_sentences[i+1]["original_chunk"]
            
            sentence = chunk_result["original_chunk"]
            
            # ... your existing lyrics formatting code ...
            lyrics = []
            for l in chunk_result["retrieved_lyrics"][:2]:
                content = l["content"]
                metadata = l["metadata"]
                song_title = metadata.get("song") or metadata.get("title") or metadata.get("source", "Unknown Song")
                lyrics.append(f"- \"{content}\" from: {song_title}")
            
            lyrics_text = "\n".join(lyrics)
            
            # Handle empty cases
            if not lyrics_text or not sentence:
                formatted_output = {
                    'original_sentence': sentence, 
                    'lyrics': lyrics_text, 
                    'modified_sentence': sentence, 
                    'song_name': ''
                }
                final_sentences.append(formatted_output)
            else:
                try:
                    print("="*50)
                    print(f"prev: {previous_sentence}")
                    print(f"current: {sentence}")
                    print(f"next: {next_sentence}")
                    print("="*50)
                    print("\n")
                    with get_openai_callback() as cb:
                        response = chain.invoke({
                            "previous_sentence": previous_sentence,
                            "next_sentence": next_sentence,
                            "sentence": sentence,
                            "lyrics": lyrics_text
                        })
                        final_sentences.append(response)
                    
                    statistics["total_tokens"] += cb.total_tokens
                    statistics["prompt_tokens"] += cb.prompt_tokens
                    statistics["completion_tokens"] += cb.completion_tokens
                    statistics["total_cost"] += cb.total_cost
                    statistics["total_llm_calls"] += 1

                except Exception as e:
                    # return {"error": str(e)}
                    print(f"Error processing sentence {i}: {str(e)}")
                    # Fallback to original sentence
                    formatted_output = {
                        'original_sentence': sentence, 
                        'lyrics': lyrics_text, 
                        'modified_sentence': sentence, 
                        'song_name': ''
                    }
                    final_sentences.append(formatted_output)
        
        # Step 4: Add newlines at paragraph boundaries
        for boundary in paragraph_boundaries:
            if boundary['end'] - 1 < len(final_sentences):
                final_sentences[boundary['end'] - 1]['modified_sentence'] += '\n'
        
        print(f"\nTotal sentences: {statistics['total_sentences']}")
        print(f"Total Cost (USD): ${statistics['total_cost']}")
        
        return {"final_sentences": final_sentences or [], "statistics": statistics}