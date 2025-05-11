import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bson import ObjectId
import asyncio

from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision
from ai_service.agents.upload_handle_agent_langraph import alfo_article_graph
from db.mongodb import articles_raw, articles_chunks

async def full_article_pipeline(article_id, raw_collection , chunked_collection):
    
    await alfo_handle_chunked_article_decision(article_id, raw_collection , chunked_collection)
    return article_id

async def full_article_pipeline_with_langraph(article_id, raw_collection , chunked_collection):
    
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
        "raw_collection": raw_collection,
        "chunked_collection": chunked_collection,
    })
    return article_id
if __name__ == '__main__':    
    asyncio.run(full_article_pipeline_with_langraph(ObjectId('68200f79f3773b6476450d13'), articles_raw, articles_chunks))