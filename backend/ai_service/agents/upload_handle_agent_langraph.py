
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chunk_article_service import *
from services.word_explainer_service import *
from services.summerizer_service import *
from services.persona_service import *
from services.utiles.json_clean import *
from services.utiles.collection_utils import get_collections_for_tag


from ai_service.intelligence.word_explainer import *
from ai_service.intelligence.summarizer import *
from ai_service.intelligence.persona import *
from ai_service.chain.alfo_chain import *
from langchain_core.runnables import RunnableLambda
from intelligence.each_chunker_handle_node import alfo_chunk_subgraph
from models.upload_article_agentGraph_state import alfoBuilder
import time
from models.article_model import Article


# --- Node: Load Chunks ---
async def load_chunks_node(state):
    # Pass the tag, not the collection, to fetch_chunked_articles
    chunks = await fetch_chunked_articles(state["article_id"], state["tag"])
    return {**state, "chunks": chunks}
# --- Node: Process Each Chunk ---
async def process_chunks_node(state):
    summary_updates, word_updates, persona_updates = [], [], []

    async def process_chunk(chunk):
        start = time.time() 
        chunk_state = {
            "article_id": state["article_id"],
            "chunk_id": chunk["chunk_id"],
            "chunk_text": clean_content(chunk["chunk_text"]),
            "chunked_collection": state["chunked_collection"]  # Pass through for downstream use
        }
        chunk_id = chunk["chunk_id"]  # ✅ Define it for logging
        try:
            
            result = await alfo_chunk_subgraph.ainvoke(chunk_state)
            
            print(f"[DEBUG] Elapsed: {time.time() - start:.2f}s")
            summary_update = result.get("summary_update", {})
            word_update = result.get("word_update", {})
            persona_update = result.get("persona_update", {})
            if summary_update:
                summary_updates.append(summary_update)
                print(f"⚠️ Chunk {chunk_id}  generate a summary.")
            else:
                print(f"⚠️ Chunk {chunk_id} did not generate a summary.")
            if word_update:
                word_updates.append(word_update)
            if persona_update:
                persona_updates.append(persona_update)
        except Exception as e:
            print(f"[ERROR] Chunk {chunk['chunk_id']} failed in ainvoke: {e}")
            log_with_func_name(f"❌ Error processing chunk {chunk['chunk_id']}: {e}")
            raise
    chunks = state.get("chunks", [])
    await asyncio.gather(*(process_chunk(c) for c in chunks))

    return {
        **state,
        "summary_updates": summary_updates,
        "word_updates": word_updates,
        "persona_updates": persona_updates
    }

async def bulk_write_node(state):
    summary_updates = state.get("summary_updates", [])
    word_updates = state.get("word_updates", [])
    persona_updates = state.get("persona_updates", [])

    if summary_updates:
        await state["chunked_collection"].bulk_write(summary_updates)
        log_with_func_name("✅ Summaries stored successfully.")
    if word_updates:
        await state["chunked_collection"].bulk_write(word_updates)
        log_with_func_name("✅ Word explanations stored successfully.")
    if persona_updates:
        await state["chunked_collection"].bulk_write(persona_updates)
        log_with_func_name("✅ Personas stored successfully.")
    return state
    log_with_func_name("✅ Merged duplicate personas.")
    return state

async def merge_personas_node(state):
    await merge_all_personas(state["chunked_collection"])
# --- Node: Combine Summaries ---
async def combine_summaries_node(state):
    try:
        combined = await combine_summaries(state["article_id"], state["chunked_collection"])
        combined = await summarize_large_combined_text(combined, state["chunked_collection"])
        await store_combined_summaries_to_mongodb(state["article_id"], combined, state["raw_collection"])
        return {**state, "combined_summary": combined}
    except Exception as e:
        log_with_func_name(f"❌ Failed to combine summaries: {e}")
        return state

async def store_combined_results_node(state):
    try:
        await store_combined_word_explanation_to_mongodb(state["article_id"], state["chunked_collection"], state["raw_collection"])
    except Exception as e:
        log_with_func_name(f"❌ Failed to store word explanations: {e}")
    try:
        await store_combined_persona_to_mongodb(state["article_id"],state["chunked_collection"],state["raw_collection"])
    except Exception as e:
        log_with_func_name(f"❌ Failed to store personas: {e}")
    return state

alfoBuilder.add_node("load_chunks", RunnableLambda(load_chunks_node))
alfoBuilder.add_node("process_chunks", RunnableLambda(process_chunks_node))
alfoBuilder.add_node("bulk_write", RunnableLambda(bulk_write_node))
alfoBuilder.add_node("merge_personas", RunnableLambda(merge_personas_node))
alfoBuilder.add_node("combine_summaries", RunnableLambda(combine_summaries_node))
alfoBuilder.add_node("store_combined", RunnableLambda(store_combined_results_node))

alfoBuilder.set_entry_point("load_chunks")
alfoBuilder.add_edge("load_chunks", "process_chunks")
alfoBuilder.add_edge("process_chunks", "bulk_write")
alfoBuilder.add_edge("bulk_write", "merge_personas")
alfoBuilder.add_edge("merge_personas", "combine_summaries")
alfoBuilder.add_edge("combine_summaries", "store_combined")
alfoBuilder.set_finish_point("store_combined")

alfo_article_graph = alfoBuilder.compile()


async def upload_article_pipeline_with_langraph(article: Article , tag):
    article_id = await upload_article_to_db(article, tag)
    await chunk_article(article_id , tag)
    raw_collection, chunked_collection, _ = get_collections_for_tag(tag)
    await alfo_article_graph.ainvoke({
        "article_id": ObjectId(article_id),
        "chunks": [],
        "summary_updates": [],
        "word_updates": [],
        "persona_updates": [],
        "combined_summary": "",
        # Optional per-chunk context — initialized as None or empty
        "chunk_id": "",
        "chunk_text": "",
        "decision": {},
        "summarize": False,
        "explain_words": False,
        "word_list": [],
        "personas": [],
        "summary_update": {},
        "word_update": {},
        "persona_update": {},
        "raw_collection":raw_collection,
        "chunked_collection":chunked_collection,
        "tag":tag
    })
    return article_id
