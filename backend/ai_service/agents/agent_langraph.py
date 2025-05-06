import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from langgraph.graph import StateGraph
from models.persona_agent_state import PersonaAgentState
from ai_service.intelligence.persona import *
from ai_service.memory.persona_vector import *

graph_builder = StateGraph(PersonaAgentState)
#answer like an expert
# graph_builder.add_node("detect_role", detect_role_node)
# graph_builder.add_node("fetch_context", fetch_context_node)
# graph_builder.add_node("generate_answer", generate_answer_node)

# graph_builder.set_entry_point("detect_role")
# graph_builder.add_edge("detect_role", "fetch_context")
# graph_builder.add_edge("fetch_context", "generate_answer")
# graph_builder.set_finish_point("generate_answer")
#answer like an expert
#chat to user
graph_builder.add_node("detect_role", detect_role_node)
graph_builder.add_node("fetch_context", fetch_context_node)
graph_builder.add_node("chat_with_user", chat_with_user_node)

graph_builder.set_entry_point("detect_role")
graph_builder.add_edge("detect_role", "fetch_context")
graph_builder.add_edge("fetch_context", "chat_with_user")
graph_builder.set_finish_point("chat_with_user")
#chat to user
graph = graph_builder.compile()

import asyncio

# --- Function to receive a query in JSON and return answer in JSON ---
async def agent_langraph_answer(input_json: dict) -> dict:
    """
    Receives a JSON dict with a 'query' field, runs the persona agent graph, returns answer in JSON.
    Example input: {"query": "What would a businessman think about TikTok bans?"}
    Returns: {"answer": <str>}
    """
    initial_state = {"query": input_json["query"]}
    final_state = await graph.ainvoke(initial_state)
    return {"answer": final_state.get("answer", "")}

if __name__ == "__main__":
    async def main():
        initial_state = {
            "query": "What would a businessman think about TikTok bans?"
        }

        final_state = await graph.ainvoke(initial_state)
        print("&&"*50)
        print("Persona Answer:", final_state["answer"])
        print("&&"*50)
    asyncio.run(main())