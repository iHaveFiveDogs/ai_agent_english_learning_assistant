import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from models.persona_agent_state import PersonaAgentState
from services.utiles.json_clean import *
from services.persona_service import *
from ai_service.chain.persona_chain import *
from ai_service.memory.persona_vector import *
import random
import hashlib
from langgraph.graph import StateGraph

def hash_fallback(query: str, persona_list: list[str]) -> str:
    index = int(hashlib.sha256(query.encode()).hexdigest(), 16) % len(persona_list)
    return persona_list[index]

async def persina_chain_detect_role(query: str, persona_list: list[str]) -> str:
    result = await persona_selector_chain.ainvoke({
        "query": query,
        "persona_list": ', '.join(persona_list)
    })
    role = result.content.strip().lower()
    print("chosen role is :", role)
    if role not in persona_list:
        print(f"⚠️ Role '{role}' not in persona list: {persona_list}")
        fallback = hash_fallback(query , persona_list)
        print(f"🔄 Random fallback to: {fallback}")
        return fallback
    return role
    result = await persona_selector_chain.ainvoke({
        "query": query,
        "persona_list": ', '.join(persona_list)
    })
    role = result.content.strip().lower()
    print("chosen role is :", role)
    if role not in persona_list:
        print(f"⚠️ Role '{role}' not in persona list: {persona_list}")
        fallback = random.choice(persona_list)
        print(f"🔄 Random fallback to: {fallback}")
        return fallback
    return role

#langraph version
async def detect_role_node(state: PersonaAgentState):
     
    persona_list = await fetch_all_persona_names()
    role = await persina_chain_detect_role(state["query"], persona_list)
    return {**state, "role": role}

async def persona_handle_user_question(role, context, query):
    return await persona_answer_question_chain.ainvoke({
        "persona": role,
        "context": context,
        "question": query
    })