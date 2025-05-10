from typing import TypedDict, Optional
from langgraph.graph import StateGraph
from bson import ObjectId 

class PersonaAgentState(TypedDict):
    query: str
    role: Optional[str]
    context: Optional[str]
    answer: Optional[str]
    article_id: ObjectId

# 4. Build the graph
personaAgentBuilder = StateGraph(PersonaAgentState)

class LogAgentState(TypedDict):
    query: str
    role: Optional[str]
    context: Optional[str]
    answer: Optional[str]
    article_id: ObjectId

logAgentBuilder = StateGraph(LogAgentState)