from langchain_core.tools import tool
from services.persona_service import fetch_all_persona_names
from ai_service.memory.persona_vector import get_relevant_docs_by_role
from ai_service.intelligence.persona import persina_chain_detect_role, persona_handle_user_question
from models.personaInput import PersonaInput
from models.persona_agent_state import PersonaAgentState
from langgraph.graph import StateGraph



@tool(args_schema=PersonaInput)
async def persona_tool_fn(persona_input: PersonaInput | str) -> str:
    """
        Dynamic tool: retrieves memory and lets a role-specific AI answer the query.
        The role is extracted from the query automatically.
        Accepts a dictionary with a single key 'query' which is the user's question.
    """
    print("Received in tool:", persona_input)
    if isinstance(persona_input, str):
        print("Received string instead of PersonaInput! Wrapping in PersonaInput.")
        persona_input = PersonaInput(query=persona_input)
    query = persona_input.query
    print("input into tool query content:", query)
    persona_list = await fetch_all_persona_names()
    role = await persina_chain_detect_role(query,persona_list)
    docs = await get_relevant_docs_by_role(role, query)
    if not docs:
        return f"⚠️ No memory found for '{role}'. Try another role."
    context = "\r\n".join([doc.page_content for doc in docs])

    result = await persona_handle_user_question(role, context, query)

    return result.content if result and result.content else "No response."
    role = await persina_chain_detect_role(query,persona_list)
    docs = await get_relevant_docs_by_role(role, query)
    if not docs:
        return f"⚠️ No memory found for '{role}'. Try another role."
    context = "\r\n".join([doc.page_content for doc in docs])

    result = await persona_handle_user_question(role, context, query)

    return result.content if result and result.content else "No response."

    result = await persona_handle_user_question(role, context, query)

    return result.content if result and result.content else "No response."
    role = await persina_chain_detect_role(query,persona_list)
    docs = await get_relevant_docs_by_role(role, query)
    if not docs:
        return f"⚠️ No memory found for '{role}'. Try another role."
    context = "\r\n".join([doc.page_content for doc in docs])

    result = await persona_handle_user_question(role, context, query)

    return result.content if result and result.content else "No response."
# langraph version
async def fetch_context_node(state: PersonaAgentState):
    
    docs = await get_relevant_docs_by_role(state["role"], state["query"])
    context = "\n".join([doc.page_content for doc in docs]) if docs else "No relevant docs"
    return {**state, "context": context}

def combine_tools():
    tools = [persona_tool_fn]

    return tools

