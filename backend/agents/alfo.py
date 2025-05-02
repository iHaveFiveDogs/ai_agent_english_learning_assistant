#Alfo , the butler's name
import sys
sys.stdout.reconfigure(encoding='utf-8')


import json  ## configuration json file
#### to make project file available####
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#### to make project file available####
from prompts.alfo_prompt import alfo_handle_chunked_article_prompt

from services.chunk_article_service import fetch_chunked_articles
from services.word_explainer_service import store_word_explanation_to_mongodb,if_there_are_word_explain,store_combined_word_explanation_to_mongodb
from services.summerizer_service import if_there_are_summary_summarized, store_chunked_summaries_to_mongodb,combine_summaries,store_combined_summaries_to_mongodb
from services.persona_service import store_chunked_personas_to_mongodb,if_there_are_persona,store_combined_persona_to_mongodb,upsert_persona_entries

from agents.word_explainer import word_explainer_handle_word_sentences
from agents.summarizer import summarizer_handle_summary,summarize_large_combined_text

from utiles.json_clean import clean_content
from utiles.llm_loader import load_llm


import asyncio


##############prepare alfo agent#################

try:
    alfo_handle_chunked_article_chain = alfo_handle_chunked_article_prompt | load_llm('alfo')
except Exception as e:
    print(e)
 

##############alfo agent#################


async def summarize_task(chunk_id, chunk_text):
    if not await if_there_are_summary_summarized(chunk_id):
        summary = await summarizer_handle_summary(chunk_text)
        await store_chunked_summaries_to_mongodb(chunk_id, summary)

async def explain_words_task(chunk_id, chunk_text, word_list):
    if not await if_there_are_word_explain(chunk_id):
        words = await word_explainer_handle_word_sentences(chunk_text, word_list)
        await store_word_explanation_to_mongodb(chunk_id, words)

async def persona_task(article_id, chunk_id, persona_list):
    if not await if_there_are_persona(chunk_id):
        await upsert_persona_entries(article_id, chunk_id, persona_list)
        await store_chunked_personas_to_mongodb(chunk_id, persona_list)
    
async def alfo_handle_chunked_article_decision(article_id):
    # Fetch chunked articles asynchronously
    
    chunks = await fetch_chunked_articles(article_id)
    
    all_tasks = []

    for chunk in chunks:
        chunk_text = chunk["chunk_text"]
        chunk_text = clean_content(chunk_text)
        
        chunk_id = chunk["chunk_id"]

        # Send to Alfo and get response
        print(" 🧠  Alfo is thinking...")
        response = alfo_handle_chunked_article_chain.invoke({"chunk_text": chunk_text})
        print(" 🧠  Alfo is done thinking...")
        
        try:
            # Extract JSON content between the first '{' and the last '}'
            response.content = clean_content(response.content)
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1
            json_content = response.content[json_start:json_end]
            
            # Validate JSON content before parsing
            if json_start == -1 or json_end == -1:
                print(f"Invalid JSON format for chunk {chunk_id}")
                continue

            # Parse Alfo's output (ensure Alfo returns JSON)
            alfo_decision = json.loads(json_content)

            # Check and handle missing decisions
            if not alfo_decision["summarize"]:
                print(f"Chunk {chunk_id}: summarize not requested.")

            if not alfo_decision["explain_words"]:
               print(f"Chunk {chunk_id}: word explanation not requested.")

            if not alfo_decision["personas"]:
                print(f"Chunk {chunk_id}: personas not requested.")
            ######## gpt version ########
            if alfo_decision["summarize"]:
                all_tasks.append(asyncio.create_task(summarize_task(chunk_id, chunk_text)))
            
            if alfo_decision["explain_words"] and isinstance(alfo_decision["word_list"], list):
                all_tasks.append(asyncio.create_task(explain_words_task(chunk_id, chunk_text, alfo_decision["word_list"])))
            
            if alfo_decision["personas"] and isinstance(alfo_decision["personas"], list):
                all_tasks.append(asyncio.create_task(persona_task(article_id, chunk_id, alfo_decision["personas"])))
            
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON for chunk {chunk_id}: {e}")
        
        except Exception as e:
            print(f"An error occurred for chunk {chunk_id}: {e}")

        finally:
            # Any cleanup code if necessary
            print(f"Finished processing chunk {chunk_id}")
    # Now wait for both tasks to finish
    if all_tasks:
        await asyncio.gather(*all_tasks)
    # ✅ Now safely combine summaries and word explanations
    print("🔵 Combining full article summaries and word explanations...")
    # Combine summaries after processing all chunks
    try:
        combined_summary = await combine_summaries(article_id)
        combined_summary = await summarize_large_combined_text(combined_summary)
        
        await store_combined_summaries_to_mongodb(article_id, combined_summary)
    except Exception as e:
        print(f"❌ Failed to combine summaries: {e}")

    # Combine word explanations after processing all chunks
    try:
        await store_combined_word_explanation_to_mongodb(article_id)
    except Exception as e:
        print(f"❌ Failed to store word explanations: {e}")

    try:
        
        await store_combined_persona_to_mongodb(article_id)
    except Exception as e:
        print(f"❌ Failed to store personas: {e}")


###############################################################

# Test function for Alfo



if __name__ == "__main__":
    asyncio.run(alfo_handle_chunked_article_decision('test_article_4'))