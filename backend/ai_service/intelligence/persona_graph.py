import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.persona_service import *
from services.utiles.json_clean import *

from ai_service.intelligence.word_explainer import *
from ai_service.intelligence.summarizer import *
from ai_service.intelligence.persona import *
from ai_service.chain.alfo_chain import *
from langchain_core.runnables import RunnableLambda
from models.upload_article_agentGraph_state import personaBuilder, PersonaState

async def should_store_persona(state: PersonaState):
    if not state.get("personas"):
        return {**state, "skip": True}

    if "chunk_id" not in state or "chunked_collection" not in state:
        print(f"[should_store_persona] ❌ Missing keys: {list(state.keys())}")
        return {**state, "skip": True}

    already_stored = await if_there_are_persona(state["chunk_id"], state["chunked_collection"])
    return {**state, "skip": already_stored}

async def store_persona_node(state: PersonaState):
    if state.get("skip") or not state.get("personas"):
        return {**state, "persona_update": {}}

    await upsert_persona_entries(
        state["article_id"],
        state["chunk_id"],
        state["personas"],
        state["chunked_collection"]
    )
    update = await make_persona_update(state["chunk_id"], state["personas"])
    return {**state, "persona_update": update}

def check_router(state: PersonaState):
    # Always return a valid key; fallback to 'generate' if not 'skip'
    return "skip" if state.get("skip") else "store"

personaBuilder.add_node("check", RunnableLambda(should_store_persona))
personaBuilder.add_node("store", RunnableLambda(store_persona_node))
personaBuilder.set_entry_point("check")
personaBuilder.add_conditional_edges(
    "check",
    RunnableLambda(check_router),
    {
        "store": "store",
        "skip": "store"
    }
)
personaBuilder.set_finish_point("store")
persona_subgraph = personaBuilder.compile()

async def handle_all_persona_chunks(decision_results: list[dict], chunked_collection, article_id):
    assert chunked_collection is not None, "❌ chunked_collection missing from state"
    updates = []

    for chunk in decision_results:
        personas = None
        if "decision" in chunk and isinstance(chunk["decision"], dict):
            personas = chunk["decision"].get("personas_list")
        else:
            personas = chunk.get("personas")

        if personas:
            state = {
                "chunk_id": chunk["chunk_id"],
                "chunk_text": chunk["chunk_text"],
                "personas": personas,
                "chunked_collection": chunked_collection,
                "article_id": article_id
            }
            result = await persona_subgraph.ainvoke(state)
            update = result.get("persona_update")
            if update:
                updates.append(update)

    if updates:
        await chunked_collection.bulk_write(updates)
        log_with_func_name("✅ Persona entries stored.")
    log_with_func_name("Returning from handle_all_persona_chunks")
    return updates
