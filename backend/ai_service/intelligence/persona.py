import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from models.persona_agent_state import PersonaAgentState
from services.utiles.json_clean import *
from services.persona_service import *
from ai_service.chain.persona_chain import *
from ai_service.memory.persona_vector import *


import hashlib
import json
import re
import time
import random

def hash_fallback(query: str, persona_list: list[str]) -> str:
    index = int(hashlib.sha256(query.encode()).hexdigest(), 16) % len(persona_list)
    return persona_list[index]

async def persona_chain_detect_role(query: str, persona_list: list[str]) -> str:
    start = time.time()
    print(f"Calling persona_selector_chain.ainvoke... at {start}")
    result = await persona_selector_chain.ainvoke({
        "query": query,
        "persona_list": ', '.join(persona_list)
    })
    print(f"persona_selector_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
    role = ""
    try:
        result_json = json.loads(result.content)
        role = result_json.get("persona", "").strip().lower()
    except json.JSONDecodeError:
        print("⚠️ LLM returned non-JSON content:", result.content)
        # Try regex rescue:
        match = re.search(r'"?persona"?\s*[:=]\s*"([^"]+)"', result.content)
        if match:
            role = match.group(1).strip().lower()
            role = role.replace("_", " ")
            print(f"🆘 Regex rescued role: {role}")
    if role not in persona_list:
        print(f"⚠️ Role '{role}' not in persona list: {persona_list}")
        fallback = hash_fallback(query , persona_list)
        print(f"🔄 Random fallback to: {fallback}")
        return fallback
    print(f"✅ Chosen role is: {role}")
    return role

async def persona_handle_user_question(role, context, query):
    start = time.time()
    print(f"Calling persona_answer_question_chain.ainvoke... at {start}")
    result = await persona_answer_question_chain.ainvoke({
        "persona": role,
        "context": context,
        "question": query
    })
    print(f"persona_answer_question_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
    return result

async def persona_chat_with_user(role, context, query):
    start = time.time()
    print(f"Calling persona_chat_chain.ainvoke... at {start}")
    result = await persona_chat_chain.ainvoke({
        "persona": role,
        "context": context,
        "question": query
    })
    print(f"persona_chat_chain.ainvoke returned at {time.time()} (elapsed: {time.time() - start:.2f}s)")
    
    return result

async def persona_chat_stream(role, context, query):
    start = time.time() 
    print(f"Streaming from persona_chat_chain.astream... at {start}")
    
    stream = persona_chat_chain.astream({
        "persona": role,
        "context": context,
        "question": query
    })

    async for chunk in stream:
        yield chunk

#langraph version
async def detect_role_node(state: PersonaAgentState):
    
    persona_list = await fetch_all_persona_names()
    role = await persona_chain_detect_role(state["query"], persona_list)

    return {**state, "role": role}

async def random_role_node(state: PersonaAgentState):
        
    persona_list = await fetch_all_persona_names_through_article(state["article_id"])
    if not persona_list:
        role = 'teacher'
    else:
        role = random.choice(persona_list)

    return {**state, "role": role}

async def generate_answer_node(state: PersonaAgentState):
    
    result = await persona_handle_user_question(state["role"], state["context"], state["query"])
    return {**state, "answer": result.content if result else "No response."}

async def chat_with_user_node(state: PersonaAgentState):
    
    result = await persona_chat_with_user(state["role"], state["context"], state["query"])
    return {**state, "answer": result.content if result else "No response."}

async def chat_with_user_stream_node(state: PersonaAgentState):
    
    stream = persona_chat_chain.astream({
        "persona": state["role"],
        "context": state["context"],
        "question": state["query"]
    })
    async for chunk in stream:
        content = chunk.content
        yield {"answer": content}  # ✅ streaming part

    # Final state (if needed)
    yield {
        **state,
        "answer": ""  # You can leave this blank or return final state
    }