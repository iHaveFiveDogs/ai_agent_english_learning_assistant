from typing import TypedDict, Optional
from langgraph.graph import StateGraph

class PersonaAgentState(TypedDict):
    query: str
    role: Optional[str]
    context: Optional[str]
    answer: Optional[str]