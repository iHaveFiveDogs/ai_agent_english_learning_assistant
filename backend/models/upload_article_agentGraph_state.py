from langgraph.graph import StateGraph
from typing_extensions import TypedDict, Annotated
from typing import List, Optional
from bson import ObjectId

# === 1. Common Chunk-Level State ===
class BaseChunkState(TypedDict, total=False):
    chunk_id: str
    chunk_text: str
    chunked_collection: str
    tag: str

# === 2. Summarizer State ===
class SummarizerState(BaseChunkState):
    summarize: bool
    summary_update: dict

# === 3. Word Explainer State ===
class WordExplainerState(BaseChunkState):
    explain_words: bool
    word_list: List[str]
    word_update: dict
   

# === 4. Expressions Explainer State ===
class ExpressionsState(BaseChunkState):
    extract_expressions: bool
    expressions: List[str]
    expression_update: dict

# === 5. Key Sentences State ===
class SentenceKeyState(BaseChunkState):
    extract_key_sentences: bool
    key_sentences: List[str]
    key_sentence_update: dict

# === 6. Persona State (requires article_id) ===
class PersonaState(BaseChunkState):
    article_id: Annotated[ObjectId, "static"]
    personas: List[str]
    persona_update: dict

# === 7. Final Merge State (optional aggregate state) ===
class MergeState(BaseChunkState):
    article_id: ObjectId
    raw_collection: str
    chunked_collection: str
    summary_updates: List[dict]
    word_updates: List[dict]
    expression_updates: List[dict]
    persona_updates: List[dict]
    key_sentence_updates: List[dict]

# === 8. Graph Builders ===
summarizerBuilder = StateGraph(SummarizerState)
wordexplainerBuilder = StateGraph(WordExplainerState)
expressionsBuilder = StateGraph(ExpressionsState)
sentenceBuilder = StateGraph(SentenceKeyState)
personaBuilder = StateGraph(PersonaState)
mergeBuilder = StateGraph(MergeState)
