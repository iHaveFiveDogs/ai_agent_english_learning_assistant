import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# No direct collection imports; use get_collections_for_tag from article_service

from datetime import datetime
from fastapi import HTTPException
from services.utiles.print_function_name import log_with_func_name
from services.utiles.collection_utils import get_collections_for_tag

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import TokenTextSplitter
from services.utiles.json_clean import *

async def upload_article_to_db(article, tag):
    raw_collection, _ , _= get_collections_for_tag(tag)
    try:
        result = await raw_collection.insert_one({
            "title": article.title,
            "source": article.source,
            "upload_date": datetime.utcnow(),
            "content": article.content
        })
        log_with_func_name("✅ Article uploaded successfully!")
        return result.inserted_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def chunk_article(article_id, tag):
    raw_collection, chunked_collection, _ = get_collections_for_tag(tag)
    splitter = TokenTextSplitter(
        chunk_size=500,       # use token count if you're tokenizing
        chunk_overlap=100
    )

    article = await raw_collection.find_one({"_id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # Clean the article content
    content = article.get("content", "")
    cleaned_content = clean_html(content)
    cleaned_content = clean_content(cleaned_content)

    chunks = splitter.split_text(cleaned_content)

    # Store to MongoDB
    for index, chunk in enumerate(chunks):
        await chunked_collection.insert_one({
            "chunk_id": f"{article_id}_{index}",
            "article_id": article_id,
            "chunk_index": index,
            "chunk_text": chunk,
            "status": {
                "summarized": False,
                "word_explained": False,
                "personas": False
            }
        })

async def fetch_chunked_articles(article_id, tag):
    _, chunked_collection, _ = get_collections_for_tag(tag)
    # Query the MongoDB collection for the chunked articles
    query = {
        "article_id": article_id,
        "$or": [
            {"status.summarized": False},
            {"status.word_explained": False}
        ]
    }
    chunked_articles_cursor = chunked_collection.find(query)
    chunks = []
    async for chunk in chunked_articles_cursor:
        chunk_text = chunk["chunk_text"]
        chunk_id = chunk["chunk_id"]
        chunks.append({"chunk_text": chunk_text, "chunk_id": chunk_id})
    return chunks

async def fetch_chunks_by_id(article_id, tag):
    _, chunked_collection, _ = get_collections_for_tag(tag)
    # Query the MongoDB collection for the chunked articles
    query = {
        "article_id": article_id
    }
    chunked_articles_cursor = chunked_collection.find(query)
    chunks = []
    async for chunk in chunked_articles_cursor:
        chunk_text = chunk["chunk_text"]
        chunk_id = chunk["chunk_id"]
        chunks.append({"chunk_text": chunk_text, "chunk_id": chunk_id})
    return chunks




