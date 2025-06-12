
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chunk_article_service import fetch_chunked_articles
from services.utiles.json_clean import *
#from services.utiles.collection_utils import get_collections_for_tag
from services.utiles.print_function_name import log_with_func_name
from services.generate_question_service import store_question_to_mongo, fetch_chunked_questions, group_by_article_id
from ai_service.chain.generate_question_chain import generate_question_chain, generate_question_chain2, question_feedback_chain

import time

async def generate_chunk_questions(article_id:str, chunk_id:str , chunk: str, tag:str):
    fetch_first_result = await fetch_chunked_questions(article_id, tag)
    
    for doc in fetch_first_result:
        if doc.get("chunk_id") == chunk_id:
            # Remove MongoDB's internal _id if present, to match decoded_questions structure
            doc.pop("_id", None)
            return doc

    try:
        start = time.time()
        print(f"Calling generate_question_chain.invoke... at {start}")
        questions = await generate_question_chain.ainvoke({"chunk_text": chunk})
        print(f"generate_question_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")

        content = clean_content(questions.content)
        json_block = extract_json_from_response(content)
        if not json_block:
            raise ValueError("No JSON structure in contextual response")

        decoded_questions = await decode_json_with_retry(json_block) if json_block else None
        if decoded_questions is not None:
            # Add chunk_id to the dict before storing
            decoded_questions["chunk_id"] = chunk_id
            await store_question_to_mongo(article_id, decoded_questions, tag)
        return decoded_questions
    except Exception as e:
        import traceback
        log_with_func_name(f"⚠️ generate_question failed for '{chunk}', trying backup generate_question_chain2...")
        log_error(chunk, e)
        print(f"[DEBUG] Exception in generate_chunk_questions (primary): {type(e).__name__}: {e}")
        traceback.print_exc()
        await asyncio.sleep(1)
        # Try backup chain
        try:
            start = time.time()
            print(f"Calling generate_question_chain2.invoke... at {start}")
            questions = await generate_question_chain2.ainvoke({"chunk_text": chunk})
            print(f"generate_question_chain2.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")

            content = clean_content(questions.content)
            json_block = extract_json_from_response(content)
            if not json_block:
                raise ValueError("No JSON structure in contextual response (backup)")

            decoded_questions = await decode_json_with_retry(json_block) if json_block else None
            if decoded_questions is not None:
                # Add chunk_id to the dict before storing
                decoded_questions["chunk_id"] = chunk_id
                await store_question_to_mongo(article_id, decoded_questions, tag)
            return decoded_questions
        except Exception as e2:
            log_with_func_name(f"⚠️ generate_question backup (generate_question_chain2) failed for '{chunk}'")
            log_error(chunk, e2)
            print(f"[DEBUG] Exception in generate_chunk_questions (backup): {type(e2).__name__}: {e2}")
            traceback.print_exc()
            await asyncio.sleep(1)
            return []

    
async def chunk_question_feedback(chunk:str , question:str , answer: str):
    try:
        start = time.time()
        print(f"Calling question_feedback_chain.invoke... at {start}")
        feedback = await question_feedback_chain.ainvoke(
            {
                "chunk_text": chunk,
                "question": question,
                "answer": answer                
            })
        print(f"question_feedback_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
            
        content = clean_content(feedback.content)
        json_block = extract_json_from_response(content)
        if not json_block:
            raise ValueError("No JSON structure in contextual response")

        decoded_feedback = await decode_json_with_retry(json_block) if json_block else None
        
        return decoded_feedback
    except Exception as e:
        import traceback
        log_with_func_name(f"⚠️ question_feedback failed for '{chunk}'")
        log_error(chunk, e)
        print(f"[DEBUG] Exception in chunk_question_feedback: {type(e).__name__}: {e}")
        traceback.print_exc()
        await asyncio.sleep(1)
        return []


    
