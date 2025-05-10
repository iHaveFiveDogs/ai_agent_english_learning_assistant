
from bson import ObjectId
from fastapi import APIRouter
from models.article_model import Article
from services.chunk_article_service import chunk_article, upload_article_to_db
from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision
from ai_service.agents.upload_handle_agent_langraph import alfo_article_graph




router = APIRouter()

async def full_article_pipeline(article: Article):
    article_id = await upload_article_to_db(article)
    await chunk_article(article_id)
    await alfo_handle_chunked_article_decision(article_id)
    return article_id

async def full_article_pipeline_with_langraph(article: Article):
    article_id = await upload_article_to_db(article)
    await chunk_article(article_id)
    await alfo_article_graph.ainvoke({
        "article_id": ObjectId(article_id),
        "chunks": [],
        "summary_updates": [],
        "word_updates": [],
        "persona_updates": [],
        "combined_summary": "",
        # Optional per-chunk context — initialized as None or empty
        "chunk_id": "",
        "chunk_text": "",
        "decision": {},
        "summarize": False,
        "explain_words": False,
        "word_list": [],
        "personas": [],
        "summary_update": {},
        "word_update": {},
        "persona_update": {},
    })
    return article_id



@router.post("/upload_article_service")
async def handle_upload_article(article: Article):
    # Start the full pipeline in background, but do not return the Task object
    article_id  = await full_article_pipeline_with_langraph(article)
    return {"article_id": str(article_id)}
