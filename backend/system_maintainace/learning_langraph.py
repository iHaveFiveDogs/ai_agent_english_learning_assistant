# 🧠 LangGraph Workshop - Module 5: Persona + Memory + Retry Logic

# ✅ GOAL: Combine persona response with vector memory, and add basic retry handling
# If vector search fails, fallback to generic LLM answer
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.persona_agent_state import personaAgentBuilder,logAgentBuilder
from langchain_core.runnables import RunnableLambda
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import random
from ai_service.llm_loader.llm_ollama import load_llm
from ai_service.memory.persona_vector import embedding_fn

# ---
# 1. Setup dummy context and vector memory
texts = [
    "Teachers explain difficult concepts in simple ways.",
    "Engineers solve problems using technical skills.",
    "Artists express ideas visually and emotionally."
]
splitter = RecursiveCharacterTextSplitter(chunk_size=40, chunk_overlap=0)
docs = splitter.create_documents(texts)

vectorstore = Chroma.from_documents(docs, embedding_fn)
retriever = vectorstore.as_retriever()
llm = load_llm('persona')

# ---
# 2. Persona selector node (from Module 4)
def select_persona_node(state):
    query = state["query"]
    if "teach" in query:
        return {"persona": "teacher"}
    elif "fix" in query:
        return {"persona": "engineer"}
    elif "paint" in query:
        return {"persona": "artist"}
    else:
        return {"persona": random.choice(["teacher", "engineer", "artist"])}

# ---
# 3. Memory node: use retriever → fallback if no docs found
def fetch_memory_node(state):
    query = state["query"]
    docs = retriever.get_relevant_documents(query)
    if docs:
        context = " ".join([doc.page_content for doc in docs])
        return {"context": context, "has_context": True}
    else:
        return {"context": "", "has_context": False}

# ---
# 4. Persona-based responder (with context if present)
def response_node(state):
    persona = state.get("persona")
    query = state["query"]
    context = state.get("context", "")
    prompt = f"You are a {persona}. Answer the question: Context: {context}\nQuestion: {query}"
    answer = llm.invoke(prompt).content
    return {"answer": answer}
#sub graph
def echo_response_node(state):
    return {"answer": f"Echoing for {state.get('role', 'unknown')}: {state.get('query', '')}"}

logAgentBuilder.add_node("echo", RunnableLambda(echo_response_node))
logAgentBuilder.set_entry_point("echo")
logAgentBuilder.set_finish_point("echo")
subgraph = logAgentBuilder.compile()

# ---
# 2. Main graph: Inject logging + subgraph reuse

# Logger node
def log_input(state):
    print(f"📝 LOG: query='{state.get('query', '')}' role='{state.get('role', 'unknown')}'")
    return {}


personaAgentBuilder.add_node("select_persona", RunnableLambda(select_persona_node))
personaAgentBuilder.add_node("fetch_memory", RunnableLambda(fetch_memory_node))
personaAgentBuilder.add_node("generate_response", RunnableLambda(response_node))
personaAgentBuilder.add_node("log", RunnableLambda(log_input))
personaAgentBuilder.add_node("echo_subgraph", subgraph)

personaAgentBuilder.set_entry_point("select_persona")
personaAgentBuilder.add_edge("select_persona", "fetch_memory")
personaAgentBuilder.add_edge("fetch_memory", "log")
personaAgentBuilder.add_edge("log", "echo_subgraph")
personaAgentBuilder.add_edge("echo_subgraph", "generate_response")
personaAgentBuilder.set_finish_point("generate_response")

graph = personaAgentBuilder.compile()

# ---
# 6. Run demo
import asyncio

async def run_workshop_graph():
    queries = [
        "Can you teach me something about science?",
        "How do I fix a broken machine?",
        "What inspires you to paint?",
        "What's your take on AI?"
    ]
    for q in queries:
        print(f"\n--- Query: {q} ---")
        result = await graph.ainvoke({"query": q})
        print("✅ Response:", result["answer"])

if __name__ == "__main__":
    asyncio.run(run_workshop_graph())

# ---
# ✅ RESULT:
# Each query selects a persona, attempts to fetch memory (vector search),
# and then generates an answer accordingly. If memory fails, context is skipped.

# NEXT: In Module 6, we’ll explore nested graphs (subgraphs), logging hooks, and performance patterns.
