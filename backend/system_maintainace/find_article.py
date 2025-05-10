import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision
import asyncio
from db.mongodb import articles_raw
title_to_find = "Instacart CEO Fidji Simo is joining OpenAI"
async def find_article(collection, article_title):
    cursor = collection.find({"title": {"$regex": article_title, "$options": "i"}})
    results = []
    async for doc in cursor:
        results.append(doc)
    
    return results

if __name__ == 'main':
    result = asyncio.run(find_article(articles_raw, title_to_find))
    print("Found articles:", result)