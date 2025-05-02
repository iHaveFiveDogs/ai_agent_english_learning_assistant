import sys
sys.stdout.reconfigure(encoding='utf-8')

#### to make project file available####
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#### to make project file available####


from prompts.summarizer_prompt import summarizer_prompt

from utiles.json_clean import clean_content, clean_json_block, log_error,decode_json_with_retry,find_weird_unicode_chars
from utiles.llm_loader import load_llm
# And for console output
import sys
sys.stdout.reconfigure(encoding='utf-8')

##############prepare summarizer agent#################
try:
    summarizer_chain = summarizer_prompt | load_llm('summarizer')
except Exception as e:
    print(e)

##############summarizer agent#################


async def summarizer_handle_summary(chunk):
    # Invoke summarizer chain
    try:
        print(" 🧠  summarizer is thinking...")
        
        response = summarizer_chain.invoke({
            "chunk_text": chunk
        })

        
        print(" 🧠  summarizer is done thinking...")
    # Log the raw response content for debugging
        response.content = clean_content(response.content)
        response.content = clean_json_block(response.content)
        
        response.content = response.content.replace('\n', '').replace('\r', '').replace('\t', '')
        response.content = response.content.replace('“', '"').replace('”', '"')  # Smart quotes to straight

        if response.content.count('"summary"') > 1:
            print("Warning: Multiple 'summary' keys found.")

        if response.content.count('{') != response.content.count('}'):
            print("Warning: Unbalanced braces in JSON content")
        
        # Extract JSON content between the first '{' and the last '}'
        json_start = response.content.find('{')
        json_end = response.content.rfind('}') + 1
        json_content = response.content[json_start:json_end]
        
        # Validate JSON content before parsing
        if json_start == -1 or json_end == -1:
            print("Invalid JSON format detected.")
            return chunk  # Return chunk_text if JSON format is invalid
        
        # Clean and validate JSON content
        json_content = json_content.replace('\n', '').replace('\t', '').replace('\r', '')
        
        # Remove trailing commas
        json_content = json_content.rstrip(', ')
        # Attempt to fix common JSON issues

        weird_chars = find_weird_unicode_chars(json_content)
        if weird_chars:
            print(f"⚠️ Weird Unicode characters found in JSON response for chunk '{chunk}': {weird_chars}")
            log_error(json_content, f"Weird Unicode characters found in JSON response for chunk '{chunk}'")
            return chunk
    
        summary = await decode_json_with_retry(json_content)
        
        if summary is None:
            return chunk  # Return chunk_text if decoding failed
        
        return summary
    except Exception as e:
        print(f"Failed to decode JSON: {e}")
        log_error(json_content, e)
        return chunk  # Return chunk_text if an exception occurs
    
async def summarize_large_combined_text(combined_summary_text, chunk_word_limit=500):
    print("Summarizing large combined text...")
    # 1. Split combined text
    words = combined_summary_text.split()
    summary_chunks = [" ".join(words[i:i+chunk_word_limit]) for i in range(0, len(words), chunk_word_limit)]

    final_summaries = []

    # 2. Summarize each small chunk safely
    for idx, small_chunk in enumerate(summary_chunks):
        print(f"🌟 Summarizing sub-chunk {idx+1}/{len(summary_chunks)}...")
        summarized_chunk = await summarizer_handle_summary(small_chunk)

        if isinstance(summarized_chunk, dict) and 'summary' in summarized_chunk:
            final_summaries.append(summarized_chunk["summary"])
        else:
            # Fallback: use original small_chunk text
            final_summaries.append(small_chunk)

    # 3. Merge all small summaries into one global summary
    global_summary = " ".join(final_summaries)
    print("✅ Global summary created.")
    return global_summary
   
