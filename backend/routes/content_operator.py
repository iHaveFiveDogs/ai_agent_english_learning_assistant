from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Query
from models.article_model import Article

from services.chunk_article_service import *
from ai_service.agents.upload_handle_agent_langraph import run_merge_pipeline
from services.article_service import delete_article_and_related
from services.article_service import get_all_articles_service, handle_edit_article_service
from services.article_service import get_single_article_service
from services.chunk_article_service import upload_article_to_db

router = APIRouter()

@router.post("/upload_article_service")
async def handle_upload_article(article: Article):
    print("tag:", article.tag)
    article_id = await upload_article_to_db(article, article.tag)
    await chunk_article(article_id , article.tag)
    await run_merge_pipeline(article_id, article.tag)
    return {"article_id": str(article_id)}

@router.delete("/delete_article")
async def delete_article(article_id: str, tag: str = Query(...)):
    try:
        result = await delete_article_and_related(article_id, tag)
        if result["success"]:
            result["message"] = "Article deleted."
        else:
            result["message"] = "Article not found."
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.put("/edit_article")
async def edit_article(article_id: str = Query(...), article: Article = ...):
    try:
        result = await handle_edit_article_service(article_id, article)
        return JSONResponse(content=result)
    except Exception as e:
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/all_articles")
async def get_all_articles(tag: str = Query(...)):
    try:
        articles = await get_all_articles_service(tag)
        return JSONResponse(content={"articles": articles})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@router.get("/single_article")
async def get_single_article(article_id: str, tag: str = Query(...)):
    try:
        article = await get_single_article_service(article_id, tag)
        return JSONResponse(content={"article": article})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)





