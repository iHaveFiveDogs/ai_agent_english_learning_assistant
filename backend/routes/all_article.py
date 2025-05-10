from fastapi import APIRouter
from services.chunk_article_service import fetch_all_articles
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/all_articles")
async def get_all_articles():
    articles = await fetch_all_articles()
    return JSONResponse(content={"articles": articles})
