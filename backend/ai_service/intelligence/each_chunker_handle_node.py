
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
from models.upload_article_agentGraph_state import each_chunker_builder
from ai_service.intelligence.persona_node import persona_store_subgraph
from ai_service.intelligence.word_explainer_node import word_explanation_subgraph
from ai_service.intelligence.summarizer_node import summarize_subgraph

async def alfo_decision_of_each_chunk_node(state):
    chunk_text = state["chunk_text"]
    response = await alfo_handle_chunked_article_chain.ainvoke({"chunk_text": chunk_text})

    try:
        content = clean_content(response.content)
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start == -1 or json_end == -1:
            print(f"⚠️ [alfo_decision_node] Invalid JSON for {chunk_id}")
            return {**state, "decision": {}}
        decision = json.loads(content[json_start:json_end])
        print(f"[DEBUG] Alfo Decision: {json.dumps(decision, indent=2)}")
        return {**state, "decision": decision}
    except Exception as e:
        print(f"⚠️ Alfo JSON parsing failed: {e}")
        return {**state, "decision": {}}

def alfo_decision_router(state):
    decision = state.get("decision", {})
    if decision.get("summarize"):
        return "summarize_node"
    elif decision.get("explain_words"):
        return "explain_node"
    elif decision.get("personas"):
        return "personas_node"
    else:
        return "personas_node"

each_chunker_builder.add_node("alfo_decision_node", RunnableLambda(alfo_decision_of_each_chunk_node))


each_chunker_builder.add_node("summarize_node", summarize_subgraph)

each_chunker_builder.add_node("explain_node", word_explanation_subgraph)

each_chunker_builder.add_node("personas_node", persona_store_subgraph)


each_chunker_builder.set_entry_point("alfo_decision_node")

each_chunker_builder.add_conditional_edges(
    "alfo_decision_node",
    RunnableLambda(alfo_decision_router),
    {
        "summarize_node": "summarize_node",
        "explain_node": "explain_node",
        "personas_node": "personas_node"
    }
)

each_chunker_builder.add_edge("alfo_decision_node", "summarize_node")

each_chunker_builder.add_edge("summarize_node", "explain_node")

each_chunker_builder.add_edge("explain_node", "personas_node")

each_chunker_builder.set_finish_point("personas_node")

alfo_chunk_subgraph = each_chunker_builder.compile()