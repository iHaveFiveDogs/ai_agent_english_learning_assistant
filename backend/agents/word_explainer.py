import sys
sys.stdout.reconfigure(encoding='utf-8')


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from prompts.word_explainer_prompt import word_explainer_prompt, word_cached_prompt,contextual_explainer_prompt, batch_ipa_prompt

from services.word_explainer_service import extract_word_sentences, save_words_to_cached_db, fetch_word_from_cached_db
#### to make project file available####
import json
import asyncio

from utiles.json_clean import clean_content, clean_ipa,decode_json_with_retry,extract_json_from_response,log_error
from utiles.llm_loader import load_llm
from utiles.lemmtize_word import lemmatize_word
##############prepare word_explainer agent#################
try:
    word_explainer_chain = word_explainer_prompt | load_llm('word_explainer')
    word_cached_chain = word_cached_prompt | load_llm('word_explainer')
    batch_ipa_chain = batch_ipa_prompt | load_llm('word_explainer')
    contextual_explainer_chain = contextual_explainer_prompt | load_llm('word_explainer')
except Exception as e:
    print(e)


##############word_explainer agent#################

async def fetch_or_cache_word_info(word):
    base_word = lemmatize_word(word)
    cached_info = fetch_word_from_cached_db(base_word)
    if cached_info:
        print(f"🟢 Using cached info for '{base_word}'")
        return base_word, clean_ipa(cached_info["ipa"]), cached_info["etymology"]

    print(f"🔍 Fetching IPA & etymology from LLM for '{base_word}'")
    for attempt in range(3):
        try:
            print(f" 🧠  word explainer is generating_ipa_etymology...")
            response = await word_cached_chain.ainvoke({"word": base_word})
            print(f" 🧠  word explainer is done generating_ipa_etymology...")
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
            print(f"🧠 Explaining '{word}' in context...")
            response = await contextual_explainer_chain.ainvoke({"word": word, "sentence": sentence})
            print(f"🧠 Brain is done explaining '{word}' in context...")
            content = clean_content(response.content)
            json_block = extract_json_from_response(content)
            if not json_block:
                raise ValueError("No JSON structure in contextual response")

            return await decode_json_with_retry(json_block)
        except Exception as e:
            print(f"⚠️ Contextual explanation failed for '{word}' (attempt {attempt+1})")
            log_error(sentence, e)
            await asyncio.sleep(1)
    return None

async def word_explainer_handle_word_sentences(chunk, word_list):
    word_sentences_list = extract_word_sentences(chunk, word_list)
    explained_words = []
    failed_words = []

    for pair in word_sentences_list:
        original_word = pair["word"]
        sentence = pair["sentence"]
        base_word = lemmatize_word(original_word)
        base_word, ipa, etymology = await fetch_or_cache_word_info(base_word)
        if not ipa and not etymology:
            print(f"❌ Skipping '{original_word}' due to failed IPA/etymology")
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
        else:
            print(f"❌ Giving up on context for '{original_word}'")
            failed_words.append({"word": original_word})
    if failed_words:
        with open("failed_words.json", "w", encoding="utf-8") as f:
            json.dump(failed_words, f, ensure_ascii=False, indent=2)

    return explained_words

async def build_ipa_etymology_cache(uncached_words):
    for word in uncached_words:
        print(f"🔎 Checking: {word}")
        try:
            print(f" 🧠  word explain is building_ipa_etymology_cache...")
            response = await word_cached_chain.ainvoke({"word": word})
            print(f" 🧠  word explain is done building_ipa_etymology_cache...")
            content = clean_content(response.content)
            json_block = extract_json_from_response(content)
            result = await decode_json_with_retry(json_block)
            if result:
                save_words_to_cached_db([lemmatize_word(result["word"]), clean_ipa(result["ipa"]), result["etymology"]])
                print(f"✅ Saved: {word}")
            else:
                print(f"❌ Failed JSON for {word}")
        except Exception as e:
            log_error(word, e)

async def precache_ipa_etymology_from_txt(txt_path, batch_size=10):
    import os
    if not os.path.exists(txt_path):
        print(f"❌ File not found: {txt_path}")
        return

    with open(txt_path, "r", encoding="utf-8") as f:
        words = [lemmatize_word(line.strip()) for line in f if line.strip() and not fetch_word_from_cached_db(lemmatize_word(line.strip()))]

    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        print(f"📦 Processing batch: {batch}, {i} / {len(words)}")
        try:
            prompt_input = {"words": batch}
            print(f" 🧠  word explainer is generating_ipa_etymology...")
            response = await batch_ipa_chain.ainvoke(prompt_input)
            print(f" 🧠  word explainer is done generating_ipa_etymology...")
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
                        print(f"✅ Saved: {word}")
                    else:
                        print(f"⚠️ Incomplete data for: {word}")
            else:
                print(f"⚠️ Batch failed. Falling back to word-by-word: {batch}")
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
                            print(f"✅ Saved individually: {word}")
                        else:
                            print(f"❌ Failed individually: {word}")
                            log_error(word, e)
                    except Exception as e:
                        print(f"❌ Individual error for {word}: {e}")
                        log_error(word, e)
        except Exception as e:
            print(f"⚠️ Batch error: {e}")
            for word in batch:
                log_error(word, e)
            await asyncio.sleep(1)
            

if __name__ == "__main__":
    # Test data
    test_chunk = "The quick brown fox jumps over the lazy dog."
    test_word_list = ["quick", "lazy"]
    
    # Run the word explainer function
    words = asyncio.run(word_explainer_handle_word_sentences(test_chunk, test_word_list))
    
    # Print the results
    for word_pack in words:
        print(json.dumps(word_pack['ipa'], indent=2))