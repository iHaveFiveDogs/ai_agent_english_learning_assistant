import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.utiles.json_clean import *


#### to make project file available####


from services.word_explainer_service import *
from services.utiles.lemmtize_word import lemmatize_word
from services.utiles.print_function_name import log_with_func_name

from ai_service.chain.word_explainer_chain import *

import json
import asyncio
import time


async def fetch_or_cache_word_info(word):
    base_word = lemmatize_word(word)
    cached_info = fetch_word_from_cached_db(base_word)
    if cached_info:
        
        return base_word, clean_ipa(cached_info["ipa"]), cached_info["etymology"]

    
    for attempt in range(3):
        try:
            start = time.time()
            print(f"Calling word_cached_chain.ainvoke... at {start}")
            response = await word_cached_chain.ainvoke({"word": base_word})
            print(f"word_cached_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
            log_with_func_name(f" 🧠  word explainer is done generating_ipa_etymology {base_word}...")
            content = clean_content(response.content)
            json_block = extract_json_from_response(content)
            
            if not json_block:
                raise ValueError("No JSON structure found in IPA/etymology response")

            word_data = await decode_json_with_retry(json_block)
            
            if word_data:
                ipa = clean_ipa(word_data.get("ipa", ""))
                etymology = word_data.get("etymology", "")
                save_words_to_cached_db(word, ipa, etymology)
                return base_word,ipa, etymology
        except Exception as e:
            print(f"⚠️ IPA/Etymology fetch failed for '{word}' (attempt {attempt+1})")
            log_error(word, e)
            await asyncio.sleep(1)
    return base_word,None, None

async def fetch_contextual_explanation(word, sentence):
    for attempt in range(3):
        try:
            start = time.time()
            print(f"Calling contextual_explainer_chain.ainvoke... at {start}")
            response = await contextual_explainer_chain.ainvoke({"word": word, "sentence": sentence})
            print(f"contextual_explainer_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
            log_with_func_name(f"🧠 Brain is done explaining '{word}' in context...")
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

async def word_explainer_handle_word_sentences(chunk_id, chunk, word_list):
    word_sentences_list = extract_word_sentences(chunk, word_list)
    explained_words = []
    failed_words = []

    for pair in word_sentences_list:
        original_word = pair["word"]
        sentence = pair["sentence"]
        base_word = lemmatize_word(original_word)

        base_word, ipa, etymology = await fetch_or_cache_word_info(base_word)

        if not ipa and not etymology:
            log_with_func_name(f"❌ Skipping '{original_word}' due to failed IPA/etymology")
            failed_words.append({"word": original_word})
            continue

        context_result = await fetch_contextual_explanation(original_word, sentence)

        if context_result:
            explained_words.append({
                "word": original_word,
                "base_word": base_word,
                "ipa": ipa,
                "etymology": etymology,
                "explanation": context_result.get("explanation", ""),
                "contextual_meaning": context_result.get("contextual_meaning", ""),
                "example_sentences": context_result.get("example_sentences", [])
            })
            make_word_explanation_update(chunk_id, explained_words)
        else:
            log_with_func_name(f"❌ Giving up on context for '{original_word}'")
            failed_words.append({"word": original_word})
    if failed_words:
        with open("failed_words.json", "w", encoding="utf-8") as f:
            json.dump(failed_words, f, ensure_ascii=False, indent=2)

    return explained_words

async def build_ipa_etymology_cache(uncached_words):
    for word in uncached_words:
        log_with_func_name(f"🔎 Checking: {word}")
        try:
            
            response = await word_cached_chain.ainvoke({"word": word})
            log_with_func_name(f" 🧠  word explainer is done building_ipa_etymology_cache...")
            content = clean_content(response.content)
            json_block = extract_json_from_response(content)
            result = await decode_json_with_retry(json_block)
            if result:
                save_words_to_cached_db([lemmatize_word(result["word"]), clean_ipa(result["ipa"]), result["etymology"]])
                log_with_func_name(f"✅ Saved: {word}")
            else:
                log_with_func_name(f"❌ Failed JSON for {word}")
        except Exception as e:
            log_error(word, e)

async def precache_ipa_etymology_from_txt(txt_path, batch_size=10):
    import os
    if not os.path.exists(txt_path):
        log_with_func_name(f"❌ File not found: {txt_path}")
        return

    with open(txt_path, "r", encoding="utf-8") as f:
        words = [lemmatize_word(line.strip()) for line in f if line.strip() and not fetch_word_from_cached_db(lemmatize_word(line.strip()))]

    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        log_with_func_name(f"📦 Processing batch: {batch}, {i} / {len(words)}")
        try:
            prompt_input = {"words": batch}

            
            response = await batch_ipa_chain.ainvoke(prompt_input)
            log_with_func_name(f" 🧠  word explainer is done generating_ipa_etymology...")
            
            content = clean_content(response.content)
            json_block = extract_json_from_response(content)
            # Patch: wrap JSON block with brackets if it looks like multiple dicts
            if json_block and not json_block.strip().startswith("["):
                json_block = "[" + json_block + "]"

            result = await decode_json_with_retry(json_block)

            if result and isinstance(result, list):
                for entry in result:
                    word = entry.get("word")
                    ipa = clean_ipa(entry.get("ipa", ""))
                    etymology = entry.get("etymology", "")
                    if word and ipa and etymology:
                        save_words_to_cached_db([{
                                "word": lemmatize_word(word),
                                "ipa": ipa,
                                "etymology": etymology
                            }])
                        log_with_func_name(f"✅ Saved: {word}")
                    else:
                        log_with_func_name(f"⚠️ Incomplete data for: {word}")
            else:
                log_with_func_name(f"⚠️ Batch failed. Falling back to word-by-word: {batch}")
                for word in batch:
                    try:
                        single_prompt = {"word": word}
                        single_response = await word_cached_chain.ainvoke(single_prompt)  # define this chain
                        single_content = clean_content(single_response.content)
                        json_block = extract_json_from_response(single_content)
                        single_result = await decode_json_with_retry(json_block)
                        if single_result:
                            save_words_to_cached_db([{
                                "word": lemmatize_word(single_result.get("word")),
                                "ipa": clean_ipa(single_result.get("ipa", "")),
                                "etymology": single_result.get("etymology", "")
                            }])
                            log_with_func_name(f"✅ Saved individually: {word}")
                        else:
                            log_with_func_name(f"❌ Failed individually: {word}")
                            log_error(word, e)
                    except Exception as e:
                        log_with_func_name(f"❌ Individual error for {word}: {e}")
                        log_error(word, e)
        except Exception as e:
            log_with_func_name(f"⚠️ Batch error: {e}")
            for word in batch:
                log_error(word, e)
            await asyncio.sleep(1)
            

