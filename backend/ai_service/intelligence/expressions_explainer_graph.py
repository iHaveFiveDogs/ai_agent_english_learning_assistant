import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.expressions_explainer_service import *
from services.summerizer_service import *
from services.persona_service import *
from services.utiles.json_clean import *


from ai_service.intelligence.word_explainer import *
from ai_service.intelligence.expressions_explainer import *
from ai_service.intelligence.summarizer import *
from ai_service.intelligence.persona import *
from ai_service.chain.alfo_chain import *
from langchain_core.runnables import RunnableLambda
from models.upload_article_agentGraph_state import ExpressionsState, expressionsBuilder


# Entry node: should we explain expressions for this chunk?
async def should_explain_expressions(state: ExpressionsState):
    # Skip if already explained
    exists = await if_there_are_expression_explain(
        state["chunk_id"], 
        state["chunked_collection"]
    )
    return {**state, "skip": exists}

# Actual expression explanation node
async def generate_expression_explanations(state: ExpressionsState):
    
    if state.get("skip"):
        
        return {**state, "expression_update": {}}
    
    explained = await expression_explainer_handle_expression_sentences(
        state["chunk_id"],
        state["chunk_text"],
        state["expressions"]
    )
    
    update = make_expression_explanation_update(state["chunk_id"], explained)
    return {**state, "expression_update": update}

# Router function
def expression_router(state: ExpressionsState):
    return "skip" if state.get("skip") else "generate"

# Build the graph
expressionsBuilder.add_node("check", RunnableLambda(should_explain_expressions))
expressionsBuilder.add_node("generate", RunnableLambda(generate_expression_explanations))

expressionsBuilder.set_entry_point("check")
expressionsBuilder.add_conditional_edges(
    "check",
    RunnableLambda(expression_router),
    {
        "generate": "generate",
        "skip": "generate"  # Both go to same end for now
    }
)
expressionsBuilder.set_finish_point("generate")

expressions_explainer_subgraph = expressionsBuilder.compile()


async def handle_all_expression_chunks(decision_results: list[dict], chunked_collection):
    assert chunked_collection is not None, "❌ chunked_collection missing from state"
    updates = []
    for chunk in decision_results:
        extract_expressions = None
        expressions = None
        if "decision" in chunk and isinstance(chunk["decision"], dict):
            extract_expressions = chunk["decision"].get("should_explain_expressions")
            expressions = chunk["decision"].get("expressions_list")
        else:
            extract_expressions = chunk.get("extract_expressions")
            expressions = chunk.get("expressions")
        if chunk.get("chunk_id") and chunk.get("chunk_text") and extract_expressions and expressions:
            state = {
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["chunk_text"],
                "expressions": expressions,
                "chunked_collection": chunked_collection,
                "extract_expressions": extract_expressions
            }
            result = await expressions_explainer_subgraph.ainvoke(state)
            update = result.get("expression_update")
            if update:
                updates.append(update)
        else:
            log_with_func_name(f"[EXPRESSION_EXPLAINER] Skipping chunk: {chunk.get('chunk_id')} (missing required fields or extract_expressions/expressions is falsy)")
    try:
        if updates:
            await chunked_collection.bulk_write(updates)
            log_with_func_name("✅ Expression explanations written.")
    except Exception as e:
        log_with_func_name(f"❌ Failed to write expression explanations: {e}")
        raise
    log_with_func_name("Returning from handle_all_expression_chunks")
    return updates
