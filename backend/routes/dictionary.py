from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ai_service.intelligence.word_explainer import word_explainer_handle_word_sentences

router = APIRouter()

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
