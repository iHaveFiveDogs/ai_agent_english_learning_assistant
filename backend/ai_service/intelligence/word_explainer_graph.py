import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.word_explainer_service import *
from services.utiles.json_clean import *
from ai_service.intelligence.word_explainer import *
from langchain_core.runnables import RunnableLambda
from models.upload_article_agentGraph_state import wordexplainerBuilder, WordExplainerState



# Entry node: should we explain words?
async def should_explain_words(state: WordExplainerState):
    if state.get("explain_words") and state.get("word_list"):
        exists = await if_there_are_word_explain(state["chunk_id"], state["chunked_collection"])
        return {**state, "skip": exists}
    return {**state, "skip": True}

# Explanation generation node
async def generate_word_explanations(state: WordExplainerState):
    if state.get("skip"):
        return {**state, "word_update": {}}
    explained = await word_explainer_handle_word_sentences(
        state["chunk_id"],
        state["chunk_text"],
        state["word_list"]
    )
    update = make_word_explanation_update(state["chunk_id"], explained)
    return {**state, "word_update": update}

# Routing function
def word_router(state: WordExplainerState):
    return "skip" if state.get("skip") else "generate"

# Build the graph

wordexplainerBuilder.add_node("check", RunnableLambda(should_explain_words))
wordexplainerBuilder.add_node("generate", RunnableLambda(generate_word_explanations))

wordexplainerBuilder.set_entry_point("check")
wordexplainerBuilder.add_conditional_edges(
    "check",
    RunnableLambda(word_router),
    {
        "generate": "generate",
        "skip": "generate"
    }
)
wordexplainerBuilder.set_finish_point("generate")

word_explanation_subgraph = wordexplainerBuilder.compile()

async def handle_all_word_chunks(decision_results: list[dict], chunked_collection):
    print("\n🟥🟥🟥--------------------  handle_all_word_chunks start --------------------🟥🟥🟥\n")
    
    updates = []
    for chunk in decision_results:
        explain_words = None
        word_list = None
        if "decision" in chunk and isinstance(chunk["decision"], dict):
            explain_words = chunk["decision"].get("should_explain_words")
            word_list = chunk["decision"].get("word_list")
        else:
            explain_words = chunk.get("explain_words")
            word_list = chunk.get("word_list")
        if chunk.get("chunk_id") and chunk.get("chunk_text") and explain_words and word_list:
            state = {
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["chunk_text"],
                "word_list": word_list,
                "chunked_collection": chunked_collection,
                "explain_words": explain_words
            }
            try:
                result = await word_explanation_subgraph.ainvoke(state)
                if not isinstance(result, dict):
                    log_with_func_name(f"[WORD_EXPLAINER] Warning: Expected dict from ainvoke, got {type(result)}: {result}")
                    result = {}
                update = result.get("word_update")
            except Exception as e:
                log_with_func_name(f"[WORD_EXPLAINER] Error in ainvoke for chunk {chunk.get('chunk_id')}: {e}")
                import traceback
                traceback.print_exc()
                update = None
            if update:
                updates.append(update)
        else:
            log_with_func_name(f"[WORD_EXPLAINER] Skipping chunk: {chunk.get('chunk_id')} (missing required fields or explain_words/word_list is falsy)")
    try:
        if updates:
            await chunked_collection.bulk_write(updates)
            log_with_func_name("✅ Word explanations written.")
    except Exception as e:
        log_with_func_name(f"❌ Failed to write word explanations: {e}")
        raise
    log_with_func_name(f"Returning from handle_all_word_chunks. Updates type: {type(updates)}, length: {len(updates)}")
    print("\n🟥🟥🟥--------------------  handle_all_word_chunks end --------------------🟥🟥🟥\n")
    return updates