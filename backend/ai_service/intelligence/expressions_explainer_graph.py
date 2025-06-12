import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.expressions_explainer_service import if_there_are_expression_explain, make_expression_explanation_update
from ai_service.intelligence.expressions_explainer import expression_explainer_handle_expression_sentences

from langchain_core.runnables import RunnableLambda
from models.upload_article_agentGraph_state import ExpressionsState, expressionsBuilder
from services.utiles.json_clean import *
from services.utiles.print_function_name import log_with_func_name

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
    print("\n🟧🟧🟧-------------------- handle_all_expression_chunks start--------------------🟧🟧🟧\n")
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
            try:
                result = await expressions_explainer_subgraph.ainvoke(state)
                if not isinstance(result, dict):
                    log_with_func_name(f"[EXPRESSION_EXPLAINER] Warning: Expected dict from ainvoke, got {type(result)}: {result}")
                    result = {}
                update = result.get("expression_update")
            except Exception as e:
                log_with_func_name(f"[EXPRESSION_EXPLAINER] Error in ainvoke for chunk {chunk.get('chunk_id')}: {e}")
                import traceback
                traceback.print_exc()
                update = None
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
    log_with_func_name(f"Returning from handle_all_expression_chunks. Updates type: {type(updates)}, length: {len(updates)}")
    print("\n🟧🟧🟧-------------------- handle_all_expression_chunks end--------------------🟧🟧🟧\n")
    return updates
