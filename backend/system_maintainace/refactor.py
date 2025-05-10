import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bson import ObjectId
import asyncio

from ai_service.intelligence.alfo import alfo_handle_chunked_article_decision
from ai_service.agents.upload_handle_agent_langraph import alfo_article_graph


async def full_article_pipeline(article_id):
    
    await alfo_handle_chunked_article_decision(article_id)
    return article_id

async def full_article_pipeline_with_langraph(article_id):
    
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

if __name__ == '__main__':
    
    asyncio.run(full_article_pipeline_with_langraph((ObjectId('681d7a2a41cb4b8f22b1dc9b'))))