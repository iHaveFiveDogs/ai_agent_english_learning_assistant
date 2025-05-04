import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from langgraph.graph import StateGraph
from models.persona_agent_state import PersonaAgentState
from ai_service.intelligence.persona import detect_role_node
from ai_service.tool.persona_tool import fetch_context_node

async def generate_answer_node(state: PersonaAgentState):
    from ai_service.intelligence.persona import persona_handle_user_question
    result = await persona_handle_user_question(state["role"], state["context"], state["query"])
    return {**state, "answer": result.content if result else "No response."}

graph_builder = StateGraph(PersonaAgentState)

graph_builder.add_node("detect_role", detect_role_node)
graph_builder.add_node("fetch_context", fetch_context_node)
graph_builder.add_node("generate_answer", generate_answer_node)

graph_builder.set_entry_point("detect_role")
graph_builder.add_edge("detect_role", "fetch_context")
graph_builder.add_edge("fetch_context", "generate_answer")
graph_builder.set_finish_point("generate_answer")

graph = graph_builder.compile()

import asyncio

if __name__ == "__main__":
    async def main():
        initial_state = {
            "query": "What would a businessman think about TikTok bans?"
        }

        final_state = await graph.ainvoke(initial_state)
        print("Persona Answer:", final_state["answer"])

    asyncio.run(main())