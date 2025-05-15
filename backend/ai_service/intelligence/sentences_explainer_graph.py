import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.sentences_explainer_service import *
from services.utiles.json_clean import *


from ai_service.intelligence.sentence_explainer import *
from langchain_core.runnables import RunnableLambda
from models.upload_article_agentGraph_state import SentenceKeyState, sentenceBuilder


# Entry node: should we explain sentences for this chunk?
async def should_explain_sentences(state: SentenceKeyState):
    # Skip if already explained
    exists = await if_there_are_sentence_explain(
        state["chunk_id"], 
        state["chunked_collection"]
    )
    return {**state, "skip": exists}

# Actual sentence explanation node
async def generate_sentence_explanations(state: SentenceKeyState):
    if state.get("skip"):
        return {**state, "key_sentence_update": {}}
    explained = await sentence_explainer(
        state["chunk_id"],
        state["key_sentences"]
    )
    update = make_sentence_explanation_update(state["chunk_id"], explained)
    return {**state, "key_sentence_update": update}

# Router function
def sentence_router(state: SentenceKeyState):
    return "skip" if state.get("skip") else "generate"

# Build the graph
sentenceBuilder.add_node("check", RunnableLambda(should_explain_sentences))
sentenceBuilder.add_node("generate", RunnableLambda(generate_sentence_explanations))

sentenceBuilder.set_entry_point("check")
sentenceBuilder.add_conditional_edges(
    "check",
    RunnableLambda(sentence_router),
    {
        "generate": "generate",
        "skip": "generate"  # Both go to same end for now
    }
)
sentenceBuilder.set_finish_point("generate")

sentence_explainer_subgraph = sentenceBuilder.compile()


async def handle_all_sentence_chunks(decision_results: list[dict], chunked_collection):
    assert chunked_collection is not None, "❌ chunked_collection missing from state"
    
    updates = []
    for chunk in decision_results:
        
        key_sentences = None
        if "decision" in chunk and isinstance(chunk["decision"], dict):
            key_sentences = chunk["decision"].get("key_sentences_list")
        else:
            key_sentences = chunk.get("key_sentences")
        
        if chunk.get("chunk_id") and chunk.get("chunk_text") and key_sentences:
            state = {
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["chunk_text"],
                "key_sentences": key_sentences,
                "chunked_collection": chunked_collection
            }
            
            print("\n🟦🟦🟦-------------------- LOG START: sentence_explainer_subgraph.ainvoke --------------------🟦🟦🟦\n")
            result = await sentence_explainer_subgraph.ainvoke(state)
            print("\n🟦🟦🟦-------------------- LOG END: sentence_explainer_subgraph.ainvoke ----------------------🟦🟦🟦\n")
            update = result.get("key_sentence_update")
            
            if update:
                updates.append(update)
        else:
            print("\n🟧🟧🟧-------------------- LOG START: Skipping chunk --------------------🟧🟧🟧\n")
            log_with_func_name(f"[SENTENCE_EXPLAINER] Skipping chunk: {chunk.get('chunk_id')} (missing required fields or extract_expressions/expressions is falsy)")
            print("\n🟧🟧🟧-------------------- LOG END: Skipping chunk ----------------------🟧🟧🟧\n")
    try:
        if updates:
            await chunked_collection.bulk_write(updates)
            log_with_func_name("✅ Sentence explanations written.")
    except Exception as e:
        print("\n🟥🟥🟥-------------------- LOG START: Failed to write sentence explanations --------------------🟥🟥🟥\n")
        log_with_func_name(f"❌ Failed to write sentence explanations: {e}")
        print("\n🟥🟥🟥-------------------- LOG END: Failed to write sentence explanations ----------------------🟥🟥🟥\n")
        raise
    log_with_func_name("Returning from handle_all_sentence_chunks")
    return updates
