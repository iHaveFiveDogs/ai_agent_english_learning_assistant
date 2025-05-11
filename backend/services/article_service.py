from db.mongodb import personas_collection
from bson import ObjectId
from models.article_model import Article
from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision
from services.chunk_article_service import fetch_all_articles, fetch_single_article,upload_article_to_db,chunk_article

from services.utiles.collection_utils import get_collections_for_tag

async def delete_article_and_related(article_id: str, tag: str):
    raw_collection, chunk_collection, persona_collection = get_collections_for_tag(tag)
    result_raw = await raw_collection.delete_one({"_id": ObjectId(article_id)})
    result_chunks = await chunk_collection.delete_many({"article_id": ObjectId(article_id)})
    result_personas_pull = await persona_collection.update_many(
        {},
        {"$pull": {"articles": {"article_id": ObjectId(article_id)}}}
    )
    result_personas_delete = await personas_collection.delete_many({"articles": {"$size": 0}})
    return {
        "success": result_raw.deleted_count == 1,
        "chunks_deleted": result_chunks.deleted_count,
        "personas_article_refs_removed": result_personas_pull.modified_count,
        "personas_deleted": result_personas_delete.deleted_count
    }

async def get_all_articles_service(tag: str):
    articles = await fetch_all_articles(tag)
    return articles

async def get_single_article_service(article_id: str, tag: str):
    article = await fetch_single_article(article_id, tag)
    return article

async def handle_upload_article_service(article: Article, tag: str):
    article_id = await upload_article_to_db(article, tag)
    await chunk_article(article_id, tag)
    await alfo_handle_chunked_article_decision(article_id)
    return article_id
