from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from models.explain_request import ExplainRequest

from ai_service.agents.chat_agent_langraph_simple import agent_langraph_chat
from ai_service.intelligence.word_explainer import word_explainer_handle_word_sentences
from ai_service.intelligence.chosen_text_explainer import context_explainer_handle_article

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
    
    ai_explanation = await context_explainer_handle_article(request.text)
    
    if not ai_explanation or "explanation" not in ai_explanation:
        return JSONResponse(content={"error": "Failed to generate explanation."}, status_code=500)
    explanation = ai_explanation["explanation"]

    return JSONResponse(content={"explanation": explanation})
