import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.mongodb import personas_collection
from bson import ObjectId
from models.article_model import Article
from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision
from services.chunk_article_service import upload_article_to_db,chunk_article
from services.utiles.collection_utils import get_collections_for_tag
from fastapi import HTTPException

async def fetch_all_articles(tag):
    """
    Fetch all articles from the specified MongoDB collection that have etymology, contextual_meaning, and example_sentences fields.
    Returns a list of articles (as dicts), converting ObjectId and datetime for frontend compatibility.
    """
    try:
        raw_collection, _ ,_= get_collections_for_tag(tag)
        cursor = raw_collection.find({})
        articles = []
        async for article in cursor:
            article["_id"] = str(article["_id"])
            # print("article",article)
            for k, v in article.items():
                if hasattr(v, 'isoformat'):
                    article[k] = v.isoformat()
            articles.append(article)
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from bson import ObjectId

async def fetch_single_article(article_id, tag):
    """
    Fetch a single article by its ObjectId from the specified MongoDB collection.
    Converts ObjectId and datetime fields for frontend compatibility.
    """
    try:
        raw_collection, _ ,_= get_collections_for_tag(tag)
        article = await raw_collection.find_one({"_id": ObjectId(article_id)})
        if article:
            article["_id"] = str(article["_id"])
            for k, v in article.items():
                if hasattr(v, 'isoformat'):
                    article[k] = v.isoformat()
        return article
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

async def handle_edit_article_service(article_id: str, article: Article):
    """
    Edit an article's title, source, and content in the {tag}_raw collection.
    Args:
        article_id (str): The ObjectId of the article as a string.
        article (Article): The new article data (title, source, content, tag).
    Returns:
        dict: Result of the update operation.
    """
    try:
        raw_collection, _, _ = get_collections_for_tag(article.tag)
        from services.utiles.json_clean import clean_html
        cleaned_content = clean_html(article.content)
        update_result = await raw_collection.update_one(
            {"_id": ObjectId(article_id)},
            {"$set": {
                "title": article.title,
                "source": article.source,
                "content": cleaned_content,
            }}
        )
        if update_result.matched_count == 0:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Article not found.")
        return {"success": True, "modified_count": update_result.modified_count}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

from datetime import datetime, timedelta

from db.mongodb import db  # Ensure db is imported

async def cleanup_articles_and_chunks():
    from pymongo.errors import OperationFailure
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    fourteen_days_ago = now - timedelta(days=14)

    collection_names = await db.list_collection_names()
    raw_collections = [name for name in collection_names if name.endswith('_raw')]
    chunk_collections = [name for name in collection_names if name.endswith('_chunks')]
    handled_collections = set(raw_collections + chunk_collections)

    # Define 7-day and 14-day collections
    seven_day_raw = {'articles_raw'}
    seven_day_chunks = {'articles_chunks'}
    fourteen_day_raw = set([name for name in raw_collections if name not in seven_day_raw])
    fourteen_day_chunks = set([name for name in chunk_collections if name not in seven_day_chunks])

    # Add novels/dramas to 14-day sets explicitly if not already present
    fourteen_day_raw.update({'novels_raw', 'dramas_raw'})
    fourteen_day_chunks.update({'novels_chunks', 'dramas_chunks'})

    # --- 7 days cleanup ---
    for raw_name in seven_day_raw:
        if raw_name in collection_names:
            raw_collection = db[raw_name]
            try:
                cursor = raw_collection.find({"upload_date": {"$lt": seven_days_ago}})
                async for article in cursor:
                    article_id = article["_id"]
                    await raw_collection.update_one(
                        {"_id": article_id},
                        {"$set": {"content": "Content removed due to IP, the content has been deleted. See source: {}".format(article.get("source", ""))}}
                    )
            except OperationFailure:
                continue
    for chunk_name in seven_day_chunks:
        if chunk_name in collection_names:
            chunked_collection = db[chunk_name]
            try:
                cursor = chunked_collection.find({"upload_date": {"$lt": seven_days_ago}})
                async for chunk in cursor:
                    await chunked_collection.update_one(
                        {"_id": chunk["_id"]},
                        {"$set": {"chunk_text": "Due to IP, the content has been deleted."}}
                    )
            except OperationFailure:
                continue

    # --- 14 days cleanup ---
    for raw_name in fourteen_day_raw:
        if raw_name in collection_names:
            raw_collection = db[raw_name]
            try:
                cursor = raw_collection.find({"upload_date": {"$lt": fourteen_days_ago}})
                async for article in cursor:
                    article_id = article["_id"]
                    await raw_collection.update_one(
                        {"_id": article_id},
                        {"$set": {"content": "Content removed due to IP, the content has been deleted. See source: {}".format(article.get("source", ""))}}
                    )
            except OperationFailure:
                continue
    for chunk_name in fourteen_day_chunks:
        if chunk_name in collection_names:
            chunked_collection = db[chunk_name]
            try:
                cursor = chunked_collection.find({"upload_date": {"$lt": fourteen_days_ago}})
                async for chunk in cursor:
                    await chunked_collection.update_one(
                        {"_id": chunk["_id"]},
                        {"$set": {"chunk_text": "Due to IP, the content has been deleted."}}
                    )
            except OperationFailure:
                continue


if __name__ == "__main__":
    import asyncio
    asyncio.run(cleanup_articles_and_chunks())