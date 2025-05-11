from fastapi import APIRouter
from fastapi.responses import JSONResponse
from bson import ObjectId

from models.article_model import Article

from services.chunk_article_service import *
from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision
from ai_service.agents.upload_handle_agent_langraph import upload_article_pipeline_with_langraph


router = APIRouter()

from fastapi import Query


from services.article_service import get_all_articles_service

@router.get("/all_articles")
async def get_all_articles(tag: str = Query(...)):
    try:
        articles = await get_all_articles_service(tag)
        return JSONResponse(content={"articles": articles})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


from services.article_service import get_single_article_service

@router.get("/single_article")
async def get_single_article(article_id: str, tag: str = Query(...)):
    try:
        article = await get_single_article_service(article_id, tag)
        return JSONResponse(content={"article": article})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


from services.article_service import delete_article_and_related

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



@router.post("/upload_article_service")
async def handle_upload_article(article: Article):
    article_id = await upload_article_pipeline_with_langraph(article, article.tag)
    return {"article_id": str(article_id)}

