
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chunk_article_service import fetch_chunked_articles
from services.utiles.json_clean import *
from services.utiles.collection_utils import get_collections_for_tag
import traceback
from pprint import pprint
from ai_service.chain.alfo_chain import alfo_handle_chunked_article_chain



# --- alfo make dicisions ---
async def prepare_chunk_states(article_id: str, tag: str) -> list[dict]:
    
    chunks = await fetch_chunked_articles(article_id, tag)
    
    prepared_states = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        chunk_text = clean_content(chunk["chunk_text"])
        try:
            response = await alfo_handle_chunked_article_chain.ainvoke({"chunk_text": chunk_text})
            # Handle AIMessage (LangChain)
            if hasattr(response, 'content'):
                print(f"[prepare_chunk_states] Got AIMessage, extracting content...")
                content = response.content
                try:
                    decision = json.loads(clean_json_block(content))
                    
                    pprint(f"[prepare_chunk_states] Parsed AIMessage content to dict: {decision}")
                except Exception as e:
                    print(f"[prepare_chunk_states] Failed to parse AIMessage content as dict: {e}\nContent: {content}")
                    decision = {}
            # Handle string
            elif isinstance(response, str):
                print(f"[prepare_chunk_states] Got string, trying to parse as JSON...")
                try:
                    decision = json.loads(clean_json_block(response))
                    pprint(f"[prepare_chunk_states] Parsed string to dict: {decision}")
                except Exception as e:
                    
                    decision = {}
            # Handle tuple (e.g., (json_str, ...))
            elif isinstance(response, tuple) and len(response) > 0:
                print(f"[prepare_chunk_states] Got tuple, trying to parse first element as JSON...")
                try:
                    decision = json.loads(clean_json_block(response[0]))
                    
                except Exception as e:
                    
                    decision = {}
            # Already dict
            elif isinstance(response, dict):
                decision = response
            else:
                
                decision = {}
        except Exception as e:
            print(f"[prepare_chunk_states] Error in ainvoke for chunk {chunk_id}: {e}")
            
            traceback.print_exc()
            decision = {}
            decision = None
        raw_collection, chunked_collection, _ = get_collections_for_tag(tag)
        prepared_states.append({
            "chunk_id": chunk_id,
            "chunk_text": chunk_text,
            "article_id": article_id,                  # needed for persona path
            "chunked_collection": chunked_collection,
            "raw_collection": raw_collection,
            "tag": tag,
            "decision": decision
        })
    print(f"[prepare_chunk_states] Returning {len(prepared_states)} prepared states of type {type(prepared_states)}")
    return prepared_states
