from langchain_core.runnables import RunnableLambda

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

from models.upload_article_agentGraph_state import summarizerBuilder




async def should_summarize(state):
    if await if_there_are_summary_summarized(state["chunk_id"]):
        return {**state, "skip": True}
    return {**state, "skip": False}

async def generate_summary_node(state):
    summary = await summarizer_handle_summary(state["chunk_text"])
    update = await make_summary_update(state["chunk_id"], summary)
    return {**state, "summary_update": update}


summarizerBuilder.add_node("check", RunnableLambda(should_summarize))
summarizerBuilder.add_node("summarize_node", RunnableLambda(generate_summary_node))

summarizerBuilder.set_entry_point("check")

def check_router(state):
    # Always return a valid key; fallback to 'summarize' if not 'skip'
    return "skip" if state.get("skip") else "summarize_node"

summarizerBuilder.add_conditional_edges(
    "check",
    RunnableLambda(check_router),
    {
        "summarize_node": "summarize_node",
        "skip": "summarize_node"  # If skip, go directly to finish
    }
)
summarizerBuilder.set_finish_point("summarize_node")

summarize_subgraph = summarizerBuilder.compile()