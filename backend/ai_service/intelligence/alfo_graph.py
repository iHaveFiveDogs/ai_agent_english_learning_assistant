
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chunk_article_service import *
from services.word_explainer_service import *
from services.expressions_explainer_service import *
from services.summerizer_service import *
from services.persona_service import *
from services.utiles.json_clean import *


from ai_service.intelligence.word_explainer import *
from ai_service.intelligence.summarizer import *
from ai_service.intelligence.persona import *
from ai_service.chain.alfo_chain import *



# --- alfo make dicisions ---
async def prepare_chunk_states(article_id: str, tag: str) -> list[dict]:
    print(f"[prepare_chunk_states] Called with article_id={article_id}, tag={tag}")
    chunks = await fetch_chunked_articles(article_id, tag)
    print(f"[prepare_chunk_states] Fetched {len(chunks)} chunks from DB")
    prepared_states = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        chunk_text = clean_content(chunk["chunk_text"])
        print(f"[prepare_chunk_states] Processing chunk: {chunk_id}")
        try:
            response = await alfo_handle_chunked_article_chain.ainvoke({"chunk_text": chunk_text})
            content = clean_content(response.content)
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            decision = json.loads(content[json_start:json_end]) if json_start != -1 and json_end != -1 else {}
            print(f"[ALFO] ✅ Chunk {chunk_id} decision:\n{json.dumps(decision, indent=2)}")
        except Exception as e:
            print(f"[ALFO] ❌ Chunk {chunk_id} failed: {e}")
            decision = {}

        # Use get_collections_for_tag to get actual collection names
        from services.utiles.collection_utils import get_collections_for_tag
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
    print(f"[prepare_chunk_states] Returning {len(prepared_states)} prepared states")
    return prepared_states

