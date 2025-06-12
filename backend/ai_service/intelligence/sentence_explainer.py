import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
current_dir = os.path.dirname(__file__)
backend_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, backend_dir)
from services.utiles.json_clean import *


#### to make project file available####


from services.sentences_explainer_service import *
from services.utiles.print_function_name import log_with_func_name

import json
import asyncio
import time


from ai_service.chain.sentence_explainer_chain import sentence_explainer_chain, sentence_explainer_chain2


async def sentence_explainer(chunk_id, sentence_list):
    explained_sentences = []
    failed_expressions = []

    for sentence in sentence_list:
        context_result = None
        # Try chain1 first
        try:
            start = time.time()
            print(f"Calling sentence_explainer_chain.ainvoke... at {start}")
            response = await sentence_explainer_chain.ainvoke({"sentence": sentence})
            print(f"sentence_explainer_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
            log_with_func_name(f"sentence explainer is done explaining '{sentence}' ...")
            content = clean_content(response.content)
            json_block = extract_json_from_response(content)
            if not json_block:
                raise ValueError("No JSON structure in contextual response")
            context_result = await decode_json_with_retry(json_block)
        except Exception as e1:
            log_with_func_name(f"⚠️ Contextual explanation with chain1 failed for '{sentence}', trying chain2...")
            log_error(sentence, e1)
            await asyncio.sleep(1)
            # Try chain2 as fallback
            try:
                start2 = time.time()
                print(f"Calling sentence_explainer_chain2.ainvoke... at {start2}")
                response2 = await sentence_explainer_chain2.ainvoke({"sentence": sentence})
                print(f"sentence_explainer_chain2.ainvoke returned at {time.time()} (elapsed: {time.time() - start2:.2f}s)")
                log_with_func_name(f"sentence explainer (chain2) is done explaining '{sentence}' ...")
                content2 = clean_content(response2.content)
                json_block2 = extract_json_from_response(content2)
                if not json_block2:
                    raise ValueError("No JSON structure in contextual response from chain2")
                context_result = await decode_json_with_retry(json_block2)
            except Exception as e2:
                log_with_func_name(f"❌ Both chains failed for '{sentence}'")
                log_error(sentence, e2)
                context_result = None

        if context_result:
            explained_sentences.append({
                "sentence": sentence,
                "paraphrase": context_result.get("paraphrase", ""),
                "grammar": context_result.get("grammar", ""),
                "meaning": context_result.get("meaning", "")
            })
            make_sentence_explanation_update(chunk_id, explained_sentences)
        else:
            print("\n🟥🟥🟥-------------------- LOG START: Giving up on context --------------------🟥🟥🟥\n")
            log_with_func_name(f"❌ Giving up on context for '{sentence}' after both chains failed")
            print("\n🟥🟥🟥-------------------- LOG END: Giving up on context ----------------------🟥🟥🟥\n")
            failed_expressions.append({"sentence": sentence})
    if failed_expressions:
        with open("failed_expressions.json", "w", encoding="utf-8") as f:
            json.dump(failed_expressions, f, ensure_ascii=False, indent=2)

    return explained_sentences




            

