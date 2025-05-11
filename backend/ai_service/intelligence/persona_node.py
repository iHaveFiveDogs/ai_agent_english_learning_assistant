import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chunk_article_service import chunk_article, fetch_chunked_articles, upload_article_to_db, fetch_all_articles, fetch_single_article
from db.mongodb import articles_raw, articles_chunks
from services.word_explainer_service import *
from services.summerizer_service import *
from services.persona_service import *
from services.utiles.json_clean import *

from ai_service.intelligence.word_explainer import *
from ai_service.intelligence.summarizer import *
from ai_service.intelligence.persona import *
from ai_service.chain.alfo_chain import *
from langchain_core.runnables import RunnableLambda
from models.upload_article_agentGraph_state import personaBuilder

# --- Persona Storage Subgraph ---
async def should_store_persona(state):
    personas = state.get("decision", {}).get("personas")
    if personas and not await if_there_are_persona(state["chunk_id"], state["chunked_collection"]):
        return {**state, "skip": False}
    return {**state, "skip": True}

async def store_persona_node(state):
    personas = state["decision"]["personas"]
    await upsert_persona_entries(state["article_id"], state["chunk_id"], personas, state["chunked_collection"])
    update = await make_persona_update(state["chunk_id"], personas)
    return {**state, "persona_update": update}

def check_router(state):
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
persona_store_subgraph = personaBuilder.compile()

