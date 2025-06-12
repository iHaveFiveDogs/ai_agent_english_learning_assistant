from langgraph.graph import StateGraph
from typing_extensions import TypedDict, Annotated
from typing import List
from bson import ObjectId

# === 1. Common Chunk-Level State ===
class BaseChunkState(TypedDict, total=False):
    chunk_id: str
    chunk_text: str
    
    

# === 2. Question State ===
class QuestionState(BaseChunkState):
    article_id: ObjectId
    tag: str
    chunk_questions_list: dict
    chunks: list

# === 8. Graph Builders ===
questionBuilder = StateGraph(QuestionState)

