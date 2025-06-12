from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from models.explain_request import ExplainRequest

from ai_service.agents.chat_agent_langraph_simple import agent_langraph_chat
from ai_service.intelligence.word_explainer import word_explainer_handle_word_sentences
from ai_service.intelligence.chosen_text_explainer import context_explainer_handle_article
from ai_service.intelligence.generate_question_graph import handle_question_generation
from ai_service.intelligence.generate_question import chunk_question_feedback

router = APIRouter()

@router.post("/agent_langraph_answer")
async def agent_langraph_endpoint(request: Request):
    data = await request.json()
    # Call the async function from agent_langraph
    tag = data.get("tag") or request.query_params.get("tag")
    print("[agent_langraph_endpoint] tag:", tag)
    if not tag:
        print("[agent_langraph_endpoint] tag is missing in both body and query params!")
    answer = await agent_langraph_chat(data, tag)
    return JSONResponse(content=answer)

@router.post("/dictionary")
async def dictionary_endpoint(request: Request):
    data = await request.json()
    # Extract chunk_id, chunk, word_list from data
    article_id = data.get("article_id", "dummy")
    article = data.get("article", "")
    words = data.get("words", [])
    if not words or not article:
        return JSONResponse(content={"error": "Missing 'words' or 'article' in request."}, status_code=400)
    explained_words = await word_explainer_handle_word_sentences(article_id, article, words)
    if explained_words:
        return JSONResponse(content=explained_words)
    else:
        return JSONResponse(content={"error": "No explanation found."}, status_code=404)

@router.post('/explain')
async def explain_article(request: ExplainRequest):
    print("---------------------------------------------------")
    print("[explain_article] text:", request.text)
    print("-----------------------------------------------------")
    ai_explanation = await context_explainer_handle_article(request.text)
    
    if not ai_explanation or "explanation" not in ai_explanation:
        return JSONResponse(content={"error": "Failed to generate explanation."}, status_code=500)
    explanation = ai_explanation["explanation"]

    return JSONResponse(content={"explanation": explanation})

@router.post('/generate_question')
async def generate_chunk_questions(request: Request):
    data = await request.json()
    article_id = data.get("article_id", "dummy")
    tag = data.get("tag")
    if not tag:
        return JSONResponse(content={"error": "Missing 'tag' in request."}, status_code=400)
    raw_chunk_questions_list = await handle_question_generation(article_id, tag)
    
    # Utility to convert ObjectId to str recursively
    def convert_objectid_to_str(obj):
        from bson import ObjectId
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, list):
            return [convert_objectid_to_str(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: convert_objectid_to_str(v) for k, v in obj.items()}
        else:
            return obj

    chunk_questions_list = convert_objectid_to_str(raw_chunk_questions_list)
    return JSONResponse(content=chunk_questions_list)

@router.post('/answer_question_feedback')
async def answer_question_feedback(request: Request):
    data = await request.json()
    chunk = data.get("chunk", "")
    question = data.get("question", "")
    answer = data.get("answer", "")
    feedback = await chunk_question_feedback(chunk, question, answer)
    return JSONResponse(content=feedback)