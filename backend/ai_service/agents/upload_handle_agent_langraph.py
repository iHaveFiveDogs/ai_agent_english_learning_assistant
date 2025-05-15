
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chunk_article_service import *
from services.word_explainer_service import *
from services.expressions_explainer_service import *
from services.summerizer_service import *
from services.persona_service import *
from services.sentences_explainer_service import store_combined_sentence_explanation_to_mongodb
from services.utiles.json_clean import *
from services.utiles.collection_utils import get_collections_for_tag

from ai_service.intelligence.alfo_graph import prepare_chunk_states
from ai_service.intelligence.word_explainer_graph import handle_all_word_chunks
from ai_service.intelligence.summarizer_graph import handle_all_summary_chunks
from ai_service.intelligence.summarizer import summarize_large_combined_text
from ai_service.intelligence.persona_graph import handle_all_persona_chunks
from ai_service.intelligence.expressions_explainer_graph import handle_all_expression_chunks
from ai_service.intelligence.sentences_explainer_graph import handle_all_sentence_chunks
from langchain_core.runnables import RunnableLambda
from models.upload_article_agentGraph_state import MergeState,mergeBuilder
from pprint import pprint

# --- Node: Main Dispatcher ---
async def do_jobs(state: MergeState):
    try:
        raw_collection, chunk_collection, _ = get_collections_for_tag(state["tag"])
        chunk_states = await prepare_chunk_states(state["article_id"], state["tag"])
        
        await asyncio.gather(
            handle_all_summary_chunks(chunk_states, chunk_collection),
            handle_all_word_chunks(chunk_states, chunk_collection),
            handle_all_expression_chunks(chunk_states, chunk_collection),
            handle_all_sentence_chunks(chunk_states, chunk_collection),
            handle_all_persona_chunks(chunk_states, chunk_collection, state["article_id"])
        )
        return {
            **state,
            "chunked_collection": chunk_collection,
            "raw_collection": raw_collection
        }
    except Exception as e:
        log_with_func_name(f"❌ Failed to dispatch jobs: {repr(e)}")
        # Return an error state so downstream nodes do not proceed with None collections
        return {**state, "error": f"do_jobs failed: {repr(e)}"}
# --- Node: Merge Personas ---
async def merge_personas_node(state: MergeState):
    if not hasattr(state["chunked_collection"], "distinct"):
        raise TypeError(f"chunked_collection is not a collection: {type(state['chunked_collection'])} {state['chunked_collection']}")
    await merge_all_personas(state["chunked_collection"])
    return state
# --- Node: Combine Summaries ---
async def combine_summaries_node(state: MergeState):
    try:
        combined = await combine_summaries(state["article_id"], state["chunked_collection"])
        combined = await summarize_large_combined_text(combined, state["chunked_collection"])
        await store_combined_summaries_to_mongodb(state["article_id"], combined, state["raw_collection"])
        return {**state, "combined_summary": combined}
    except Exception as e:
        log_with_func_name(f"❌ Failed to combine summaries: {e}")
        return state
# --- Node: Store Combined Results ---
async def store_combined_results_node(state: MergeState):
    try:
        await store_combined_word_explanation_to_mongodb(state["article_id"], state["chunked_collection"], state["raw_collection"])
    except Exception as e:
        log_with_func_name(f"❌ Failed to store word explanations: {e}")
    try:
        await store_combined_persona_to_mongodb(state["article_id"], state["chunked_collection"], state["raw_collection"])
    except Exception as e:
        log_with_func_name(f"❌ Failed to store personas: {e}")
    try:
        await store_combined_expression_explanation_to_mongodb(state["article_id"], state["chunked_collection"], state["raw_collection"])
    except Exception as e:
        log_with_func_name(f"❌ Failed to store expressions: {e}")
    try:
        await store_combined_sentence_explanation_to_mongodb(state["article_id"], state["chunked_collection"], state["raw_collection"])
    except Exception as e:
        log_with_func_name(f"❌ Failed to store sentences: {e}")
    return state
# --- Build the Merge Graph ---
mergeBuilder.add_node("do_jobs", RunnableLambda(do_jobs))
mergeBuilder.add_node("merge_personas", RunnableLambda(merge_personas_node))
mergeBuilder.add_node("combine_summaries", RunnableLambda(combine_summaries_node))
mergeBuilder.add_node("store_combined", RunnableLambda(store_combined_results_node))

mergeBuilder.set_entry_point("do_jobs")
mergeBuilder.add_edge("do_jobs", "merge_personas")
mergeBuilder.add_edge("merge_personas", "combine_summaries")
mergeBuilder.add_edge("combine_summaries", "store_combined")
mergeBuilder.set_finish_point("store_combined")

merge_graph = mergeBuilder.compile()

async def run_merge_pipeline(article_id: str, tag: str):
    """
    Execute the full merge pipeline using the compiled merge_graph.
    """
    
    initial_state = {
        "article_id": ObjectId(article_id),
        "tag": tag,
        "raw_collection": None,
        "chunked_collection": None,
        "summary_updates": [],
        "word_updates": [],
        "expression_updates": [],
        "key_sentence_updates": [],
        "persona_updates": []
    }
    

    try:
        final_state = await merge_graph.ainvoke(initial_state)
        print(f"[merge_pipeline] ✅ After do_jobs: {type(final_state['chunked_collection'])}")
        log_with_func_name("✅ Merge pipeline completed successfully.")
        return final_state
    except Exception as e:
        log_with_func_name(f"❌ Merge pipeline failed: {e}")
        return {"error": str(e)}

