# make summarizer node
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.summerizer_service import *
from ai_service.intelligence.summarizer import *
from models.upload_article_agentGraph_state import summarizerBuilder, SummarizerState
from langchain_core.runnables import RunnableLambda

async def should_summarize(state: SummarizerState):
    clean_state = {k: v for k, v in state.items() if k not in ("chunk_id", "chunked_collection", "article_id", "decision")}

    if "chunk_id" in state and "chunked_collection" in state:
        exists = await if_there_are_summary_summarized(state["chunk_id"], state["chunked_collection"])
        return {**clean_state, "skip": exists}
    else:
        print(f"[should_summarize] ❌ Missing keys: {list(state.keys())}")
        return {**clean_state, "skip": True}


async def generate_summary_node(state: SummarizerState):
    clean_state = {k: v for k, v in state.items() if k not in ("chunk_id", "chunk_text", "chunked_collection", "decision", "article_id")}

    if "chunk_id" in state and "chunk_text" in state and "chunked_collection" in state:
        summary = await summarizer_handle_summary(state["chunk_text"], state["chunked_collection"])
        update = await make_summary_update(state["chunk_id"], summary)
        return {**clean_state, "summary_update": update}
    else:
        print(f"[generate_summary_node] ❌ Missing keys: {list(state.keys())}")
        return {**clean_state, "skip": True}


summarizerBuilder.add_node("check", RunnableLambda(should_summarize))
summarizerBuilder.add_node("summarize_node", RunnableLambda(generate_summary_node))

summarizerBuilder.set_entry_point("check")

def check_router(state: SummarizerState):
    return "skip" if state.get("skip") else "summarize_node"

summarizerBuilder.add_conditional_edges(
    "check",
    RunnableLambda(check_router),
    {
        "summarize_node": "summarize_node",
        "skip": "summarize_node"  # If skip, go directly to finish
    })
summarizerBuilder.set_finish_point("summarize_node")

summarize_subgraph = summarizerBuilder.compile()


async def handle_all_summary_chunks(decision_results: list[dict], chunked_collection):
    assert chunked_collection is not None, "❌ chunked_collection missing from state"
    updates = []

    for chunk in decision_results:
        should_summarize = None
        if "decision" in chunk and isinstance(chunk["decision"], dict):
            should_summarize = chunk["decision"].get("should_summarize")
        else:
            should_summarize = chunk.get("should_summarize")

        if chunk.get("chunk_id") and chunk.get("chunk_text") and should_summarize:
            state = {
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["chunk_text"],
                "chunked_collection": chunked_collection,
                "should_summarize": should_summarize,
            }
            result = await summarize_subgraph.ainvoke(state)
            update = result.get("summary_update")
            if update:
                updates.append(update)
        else:
            log_with_func_name(f"Skipping chunk: {chunk.get('chunk_id')} (missing required fields)")

    # ✅ Bulk write if there’s anything to write
    if updates:
        await chunked_collection.bulk_write(updates)
        log_with_func_name("✅ Summaries written to MongoDB.")
    else:
        log_with_func_name("No summary updates to write.")
    log_with_func_name("Returning from handle_all_summary_chunks")
    return updates