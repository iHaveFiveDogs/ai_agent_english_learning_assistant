from typing import TypedDict, Optional
from langgraph.graph import StateGraph
from bson import ObjectId 

class AlfoState(TypedDict, total=False):
    article_id: ObjectId
    chunk_id: str
    chunk_text: str
    decision: dict
    summarize: bool                # ✅ extracted from decision
    explain_words: bool           # ✅ extracted from decision
    word_list: list[str]          # ✅ needed by explainer node
    personas: list[str]           # ✅ needed by persona node
    summary_update: dict
    word_update: dict
    persona_update: dict
    summary_updates: list[dict]       # ✅ Add this
    word_updates: list[dict]          # ✅ Add this
    persona_updates: list[dict]       # ✅ Add this
    chunks: list
    combined_summary: str 

# 4. Build the graph
alfoBuilder = StateGraph(AlfoState)
summarizerBuilder = StateGraph(AlfoState)
wordexplainerBuilder = StateGraph(AlfoState)
personaBuilder = StateGraph(AlfoState)
each_chunker_builder = StateGraph(AlfoState)