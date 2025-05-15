import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
current_dir = os.path.dirname(__file__)
backend_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, backend_dir)
from services.utiles.json_clean import *


#### to make project file available####


from services.expressions_explainer_service import *
from services.utiles.lemmtize_word import lemmatize_word
from services.utiles.print_function_name import log_with_func_name



import json
import asyncio
import time


from ai_service.prompts.expressions_explainer_prompt import *
from ai_service.llm_loader.llm_ollama import load_llm

try:
    
    expressions_explainer_chain = expressions_explainer_prompt | load_llm('expressions_explainer')
    contextual_expression_explainer_chain = contextual_expression_explainer_prompt | load_llm('expressions_explainer')
except Exception as e:
    print(e)
async def fetch_or_cache_expression_info(expression):
    
    cached_info = fetch_expression_from_cached_db(expression)
    if cached_info:
        
        return expression, cached_info["meaning"], cached_info["etymology"]

    
    for attempt in range(3):
        try:
            start = time.time()
            
            print(f"Calling expressions_explainer_chain.ainvoke... at {start}")
            response = await expressions_explainer_chain.ainvoke({"expression": expression})
            print(f"expressions_explainer_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
            log_with_func_name(f" 🧠  expressions_explainer is done generating_meaning_etymology {expression}...")
            content = clean_content(response.content)
            json_block = extract_json_from_response(content)
            
            if not json_block:
                raise ValueError("No JSON structure found in meaning/etymology response")

            word_data = await decode_json_with_retry(json_block)
            
            if word_data:
                meaning = word_data.get("meaning", "")
                etymology = word_data.get("etymology", "")
                save_expressions_to_cached_db(expression, meaning, etymology)
                return expression, meaning, etymology
        except Exception as e:
            print(f"⚠️ Meaning/Etymology fetch failed for '{expression}' (attempt {attempt+1})")
            log_error(expression, e)
            await asyncio.sleep(1)
    return expression,None, None

async def fetch_contextual_explanation(expression, sentence):
    for attempt in range(3):
        try:
            start = time.time()
            
            print(f"Calling contextual_explainer_chain.ainvoke... at {start}")
            response = await contextual_expression_explainer_chain.ainvoke({"expression": expression, "sentence": sentence})
            print(f"contextual_explainer_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
            log_with_func_name(f"🧠expression_explainer is done explaining '{expression}' in context...")
            content = clean_content(response.content)
            json_block = extract_json_from_response(content)
            if not json_block:
                raise ValueError("No JSON structure in contextual response")

            return await decode_json_with_retry(json_block)
        except Exception as e:
            log_with_func_name(f"⚠️ Contextual explanation failed for '{word}' (attempt {attempt+1})")
            log_error(sentence, e)
            await asyncio.sleep(1)
    return None

async def expression_explainer_handle_expression_sentences(chunk_id, chunk, expression_list):
    expression_sentences_list = extract_expression_sentences(chunk, expression_list)
    explained_expressions = []
    failed_expressions = []

    for pair in expression_sentences_list:
        original_expression = pair["expression"]
        sentence = pair["sentence"]
        

        expression, meaning, etymology = await fetch_or_cache_expression_info(original_expression)

        if not meaning and not etymology:
            log_with_func_name(f"❌ Skipping '{original_expression}' due to failed meaning/etymology")
            failed_expressions.append({"expression": original_expression})
            continue

        context_result = await fetch_contextual_explanation(expression, sentence)

        if context_result:
            explained_expressions.append({
                "expression": original_expression,
                "meaning": meaning,
                "etymology": etymology,
                "contextual_meaning": context_result.get("contextual_meaning", ""),
                "example_sentences": context_result.get("example_sentences", [])
            })
            make_expression_explanation_update(chunk_id, explained_expressions)
        else:
            log_with_func_name(f"❌ Giving up on context for '{expression}'")
            failed_expressions.append({"expression": expression})
    if failed_expressions:
        with open("failed_expressions.json", "w", encoding="utf-8") as f:
            json.dump(failed_expressions, f, ensure_ascii=False, indent=2)

    return explained_expressions

