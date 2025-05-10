
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chunk_article_service import *
from services.word_explainer_service import *
from services.summerizer_service import *
from services.persona_service import *
from services.utiles.json_clean import *


from ai_service.intelligence.word_explainer import *
from ai_service.intelligence.summarizer import *
from ai_service.intelligence.persona import *
from ai_service.chain.alfo_chain import *
from langchain_core.runnables import RunnableLambda
from models.upload_article_agentGraph_state import wordexplainerBuilder



# --- Word Explanation Subgraph ---
async def should_explain(state):
    if state.get("decision", {}).get("explain_words") and state.get("decision", {}).get("word_list"):
        if not await if_there_are_word_explain(state["chunk_id"]):
            return {**state, "skip": False}
    return {**state, "skip": True}

async def generate_word_explanations(state):
    word_list = state["decision"]["word_list"]
    words = await word_explainer_handle_word_sentences(state["chunk_id"], state["chunk_text"], word_list)
    update = make_word_explanation_update(state["chunk_id"], words)
    return {**state, "word_update": update}

def check_router(state):
    # Always return a valid key; fallback to 'generate' if not 'skip'
    return "skip" if state.get("skip") else "generate"

wordexplainerBuilder.add_node("should_explain", RunnableLambda(should_explain))
wordexplainerBuilder.add_node("generate", RunnableLambda(generate_word_explanations))
wordexplainerBuilder.set_entry_point("should_explain")
wordexplainerBuilder.add_conditional_edges(
    "should_explain",
    RunnableLambda(check_router),
    {
        "generate": "generate",
        "skip": "generate"  # If skip, go directly to finish
    })
wordexplainerBuilder.set_finish_point("generate")
word_explanation_subgraph = wordexplainerBuilder.compile()