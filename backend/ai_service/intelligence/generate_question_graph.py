import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.chunk_article_service import fetch_chunks_by_id
from ai_service.intelligence.generate_question import generate_chunk_questions
from services.generate_question_service import store_question_to_mongo

from langchain_core.runnables import RunnableLambda
from models.generate_quesion_agentGraph_state import questionBuilder, QuestionState
from services.utiles.json_clean import *
from services.utiles.print_function_name import log_with_func_name
from bson.objectid import ObjectId

async def fetch_chunks_node(state: QuestionState):
    chunks = await fetch_chunks_by_id(state["article_id"], state["tag"])
    return {**state, "chunks": chunks}

async def generate_question_node(state: QuestionState):
    chunk_questions = []
    for chunk in state["chunks"]:
        questions = await generate_chunk_questions(state["article_id"], chunk["chunk_id"], chunk["chunk_text"], state["tag"])
        if questions:
            chunk_questions.append({
                "chunk_id": chunk["chunk_id"],
                "questions": questions["questions"]
            })
    
    return {**state, "chunk_questions_list": chunk_questions}
    

questionBuilder.add_node("fetch_chunks", RunnableLambda(fetch_chunks_node))
questionBuilder.add_node("generate_question", RunnableLambda(generate_question_node))

questionBuilder.set_entry_point("fetch_chunks")
questionBuilder.add_edge("fetch_chunks", "generate_question")
questionBuilder.set_finish_point("generate_question")

question_graph = questionBuilder.compile()

async def handle_question_generation(article_id, tag):
    articleId = ObjectId(article_id)
    chunk_questions_list = await question_graph.ainvoke({"article_id": articleId, "tag": tag})

    return chunk_questions_list