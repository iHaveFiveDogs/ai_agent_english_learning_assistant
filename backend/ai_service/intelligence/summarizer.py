import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.utiles.json_clean import *
from services.utiles.print_function_name import log_with_func_name

from ai_service.chain.summarizer_chain import summarizer_chain
import time

async def summarizer_handle_summary(chunk, chunked_collection):
    # Invoke summarizer chain
    try:
        start = time.time()
        print(f"Calling summarizer_chain.invoke... at {start}")
        response = summarizer_chain.invoke({
            "chunk_text": chunk,
            "chunked_collection": chunked_collection
        })
        print(f"summarizer_chain.invoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")

        log_with_func_name(" 🧠  summarizer is done thinking...")
        response.content = clean_content(response.content)
        response.content = clean_json_block(response.content)
        
        response.content = response.content.replace('\n', '').replace('\r', '').replace('\t', '')
        response.content = response.content.replace('“', '"').replace('”', '"')  # Smart quotes to straight

        if response.content.count('"summary"') > 1:
            log_with_func_name("Warning: Multiple 'summary' keys found.")

        if response.content.count('{') != response.content.count('}'):
            log_with_func_name("Warning: Unbalanced braces in JSON content")
        
        # Extract JSON content between the first '{' and the last '}'
        json_start = response.content.find('{')
        json_end = response.content.rfind('}') + 1
        json_content = response.content[json_start:json_end]
        
        # Validate JSON content before parsing
        if json_start == -1 or json_end == -1:
            log_with_func_name("Invalid JSON format detected.")
            return chunk  # Return chunk_text if JSON format is invalid
        
        # Clean and validate JSON content
        json_content = json_content.replace('\n', '').replace('\t', '').replace('\r', '')
        
        # Remove trailing commas
        json_content = json_content.rstrip(', ')
        # Attempt to fix common JSON issues

        weird_chars = find_weird_unicode_chars(json_content)
        if weird_chars:
            log_with_func_name(f"⚠️ Weird Unicode characters found in JSON response for chunk '{chunk}': {weird_chars}")
            log_error(json_content, f"Weird Unicode characters found in JSON response for chunk '{chunk}'")
            return chunk
    
        summary = await decode_json_with_retry(json_content)
        
        if summary is None:
            return chunk  # Return chunk_text if decoding failed
    
        return summary
    except Exception as e:
        log_with_func_name(f"Failed to decode JSON: {e}")
        log_error(json_content, e)
        return chunk # Return chunk_text if an exception occurs
    
async def summarize_large_combined_text(combined_summary_text, chunked_collection, chunk_word_limit=800):
    log_with_func_name("Summarizing large combined text...")
    # 1. Split combined text
    words = combined_summary_text.split()
    summary_chunks = [" ".join(words[i:i+chunk_word_limit]) for i in range(0, len(words), chunk_word_limit)]

    final_summaries = []

    # 2. Summarize each small chunk safely
    for idx, small_chunk in enumerate(summary_chunks):
        log_with_func_name(f"🌟 Summarizing sub-chunk {idx+1}/{len(summary_chunks)}...")

        summarized_chunk = await summarizer_handle_summary(small_chunk, chunked_collection)

        if isinstance(summarized_chunk, dict) and 'summary' in summarized_chunk:
            final_summaries.append(summarized_chunk["summary"])
        else:
            # Fallback: use original small_chunk text
            final_summaries.append(small_chunk)

    # 3. Merge all small summaries into one global summary
    global_summary = " ".join(final_summaries)
    log_with_func_name("✅ Global summary created.")
    return global_summary
