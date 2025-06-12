import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from services.utiles.json_clean import *
from services.utiles.print_function_name import log_with_func_name
from ai_service.chain.chosen_text_chain import *


async def context_explainer_handle_article(user_context):
    try:
        log_with_func_name(" 🧠  context plainer is thinking...")
        response = await context_explainer_chain.ainvoke({"sentence": user_context})
        log_with_func_name(" 🧠  context plainer is done thinking...")

        # Use json_clean utilities for all cleaning and extraction
        content = clean_content(response.content)
        json_block = extract_json_from_response(content)
        if not json_block:
            raise ValueError("No JSON structure in contextual response")
        result = await decode_json_with_retry(json_block)
        if result is not None:
            return result
        # Fallback to context_explainer_chain2 if first attempt fails
        log_with_func_name("[Fallback] Trying context_explainer_chain2...")
        response2 = await context_explainer_chain2.ainvoke({"sentence": user_context})
        content2 = clean_content(response2.content)
        json_block2 = extract_json_from_response(content2)
        if not json_block2:
            raise ValueError("No JSON structure in fallback contextual response")
        result2 = await decode_json_with_retry(json_block2)
        if result2 is not None:
            return result2
        print("[ERROR] Both context_explainer_chain and context_explainer_chain2 failed to produce valid JSON.")
        log_error(json_block2, Exception("Both chains failed to decode JSON"))
        return None
    except Exception as e:
        print(f"Failed to decode JSON: {e}")
        log_error(user_context, e)
        return None