import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from services.chunk_article_service import *
from db.mongodb import articles_chunks
from services.word_explainer_service import *
from services.summerizer_service import *
from services.persona_service import *
from services.utiles.json_clean import *
from services.utiles.print_function_name import log_with_func_name

from ai_service.intelligence.word_explainer import *
from ai_service.intelligence.summarizer import *
from ai_service.intelligence.persona import *
from ai_service.chain.alfo_chain import *
import time
import asyncio
import json  ## configuration json file


async def summarize_task(chunk_id, chunk_text, summary_updates):
    if not await if_there_are_summary_summarized(chunk_id):
        summary = await summarizer_handle_summary(chunk_text)
        summary_updates.append(await make_summary_update(chunk_id, summary))

async def explain_words_task(chunk_id, chunk_text, word_list, word_updates):
    if not await if_there_are_word_explain(chunk_id):
        words = await word_explainer_handle_word_sentences(chunk_id, chunk_text, word_list)
        word_updates.append(make_word_explanation_update(chunk_id, words))

async def persona_task(article_id, chunk_id, persona_list, persona_updates):
    if not await if_there_are_persona(chunk_id):
        await upsert_persona_entries(article_id, chunk_id, persona_list)
        persona_updates.append(await make_persona_update(chunk_id, persona_list))

async def alfo_handle_chunked_article_decision(article_id):
    # Fetch chunked articles asynchronously
    chunks = await fetch_chunked_articles(article_id, articles_chunks)
    all_tasks = []
    word_updates = []
    persona_updates = []
    summary_updates = []


    for chunk in chunks:
        raw_chunk_text = chunk["chunk_text"]
        chunk_text = clean_content(raw_chunk_text)
        
        chunk_id = chunk["chunk_id"]

        # Send to Alfo and get response
        start = time.time()
        print(f"Calling alfo_handle_chunked_article_chain.ainvoke... at {start}")
        response = await alfo_handle_chunked_article_chain.ainvoke({"chunk_text": chunk_text})
        print(f"alfo_handle_chunked_article_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
        log_with_func_name(f" 🧠  Alfo is done thinking...")
        
        try:
            # Extract JSON content between the first '{' and the last '}'
            response.content = clean_content(response.content)
            json_start = response.content.find('{')
            json_end = response.content.rfind('}') + 1

            # Validate JSON content before parsing
            if json_start == -1 or json_end == -1:
                log_with_func_name(f"Invalid JSON format for chunk {chunk_id}")
                continue

            json_content = response.content[json_start:json_end]
            
            # Parse Alfo's output (ensure Alfo returns JSON)
            alfo_decision = json.loads(json_content)
            
            # Check and handle missing decisions
            
            ######## gpt version ########
            if alfo_decision["summarize"]:
                all_tasks.append(asyncio.create_task(
                    summarize_task(chunk_id, chunk_text, summary_updates)
                ))
            else:
                log_with_func_name(f"Chunk {chunk_id}: summarize not requested.")
            
            if alfo_decision["explain_words"] and isinstance(alfo_decision["word_list"], list):
                all_tasks.append(asyncio.create_task(
                    explain_words_task(chunk_id, chunk_text, alfo_decision["word_list"], word_updates)
                ))
            else:
                log_with_func_name(f"Chunk {chunk_id}: word explanation not requested.")
            
            if alfo_decision["personas"] and isinstance(alfo_decision["personas"], list):
                all_tasks.append(asyncio.create_task(
                    persona_task(article_id, chunk_id, alfo_decision["personas"], persona_updates)
                ))
            else:
                log_with_func_name(f"Chunk {chunk_id}: personas not requested.")
            
        except json.JSONDecodeError as e:
            log_with_func_name(f"Failed to decode JSON for chunk {chunk_id}: {e}")
        
        except Exception as e:
            log_with_func_name(f"An error occurred for chunk {chunk_id}: {e}")

        finally:
            # Any cleanup code if necessary
            log_with_func_name(f"Finished processing chunk {chunk_id}")
    # Now wait for both tasks to finish
    if all_tasks:
        await asyncio.gather(*all_tasks)

    if word_updates:
        await articles_chunks.bulk_write(word_updates)
        log_with_func_name("✅ Word explanations stored successfully.")
    if persona_updates:
        await articles_chunks.bulk_write(persona_updates)
        log_with_func_name("✅ Personas stored successfully.")
    if summary_updates:
        await articles_chunks.bulk_write(summary_updates)
        log_with_func_name("✅ Summaries stored successfully.")
    
    # Merge duplicate persona entries
    log_with_func_name("Merging duplicate persona entries...")
    await merge_all_personas()
    log_with_func_name("✅ Duplicate persona entries merged.")

    # ✅ Now safely combine summaries and word explanations
    log_with_func_name("🔵 Combining full article summaries and word explanations...")
    # Combine summaries after processing all chunks
    try:
        combined_summary = await combine_summaries(article_id)
        combined_summary = await summarize_large_combined_text(combined_summary)
        
        await store_combined_summaries_to_mongodb(article_id, combined_summary)
    except Exception as e:
        log_with_func_name(f"❌ Failed to combine summaries: {e}")
    
    # Combine word explanations after processing all chunks
    try:
        await store_combined_word_explanation_to_mongodb(article_id)
    except Exception as e:
        log_with_func_name(f"❌ Failed to store word explanations: {e}")
    
    try:
        await store_combined_persona_to_mongodb(article_id)
    except Exception as e:
        log_with_func_name(f"❌ Failed to store personas: {e}")

