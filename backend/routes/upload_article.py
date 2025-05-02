from fastapi import APIRouter
from models.article_model import Article
from services.chunk_article_service import chunk_article, upload_article_to_db
from agents.alfo import alfo_handle_chunked_article_decision

router = APIRouter()



@router.post("/upload_article_service/")
async def handle_upload_article(article: Article):
    article_id = await upload_article_to_db(article)
    await chunk_article(article_id)
    await alfo_handle_chunked_article_decision(article_id)
    return {"article_id": str(article_id)}
