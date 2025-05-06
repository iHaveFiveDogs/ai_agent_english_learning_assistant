import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from db.mongodb import articles_raw, articles_chunks, personas_collection
from bson import ObjectId


def get_duplicate_articles_key(article):
    # Only use title to determine duplicates
    return article.get("title")

async def find_and_delete_duplicates():
    # 1. Find all articles
    cursor = articles_raw.find({})
    articles = []
    async for article in cursor:
        articles.append(article)

    # 2. Identify duplicates (keep first occurrence)
    seen = {}
    duplicates = []
    for article in articles:
        key = get_duplicate_articles_key(article)
        if key in seen:
            duplicates.append(article)
        else:
            seen[key] = article

    # 3. Delete duplicates in articles_raw, articles_chunks, and personas_collection
    for dup in duplicates:
        article_id = dup["_id"]
        print(f"Deleting duplicate article: {article_id}")
        await articles_raw.delete_one({"_id": article_id})
        # Delete related chunks
        chunk_cursor = articles_chunks.find({"article_id": article_id})
        chunk_ids = []
        async for chunk in chunk_cursor:
            chunk_ids.append(chunk["chunk_id"])
        await articles_chunks.delete_many({"article_id": article_id})
        # Delete related personas by article_id and chunk_id
        if chunk_ids:
            await personas_collection.delete_many({"chunk_id": {"$in": chunk_ids}})
        await personas_collection.delete_many({"article_id": article_id})
    print(f"Deleted {len(duplicates)} duplicate articles and related data.")

if __name__ == "__main__":
    asyncio.run(find_and_delete_duplicates())
