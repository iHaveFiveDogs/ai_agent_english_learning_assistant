
from fastapi import APIRouter
from models.article_model import Article
from services.chunk_article_service import chunk_article, upload_article_to_db
from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision
from uuid import uuid4
import asyncio
from services.utiles.upload_process_track import update_progress

router = APIRouter()
async def full_article_pipeline(article: Article, job_id: str):
    article_id = await upload_article_to_db(article)
    await chunk_article(article_id)
    await alfo_handle_chunked_article_decision(article_id, job_id)


@router.post("/upload_article_service")
async def handle_upload_article(article: Article):
    job_id = str(uuid4())
    update_progress(job_id, 0)

    # Start the full pipeline in background
    asyncio.create_task(full_article_pipeline(article, job_id))

    return {"job_id": job_id}
