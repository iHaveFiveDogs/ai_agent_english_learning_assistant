import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.mongodb import articles_chunks, articles_raw

from datetime import datetime
from fastapi import HTTPException
from services.utiles.print_function_name import log_with_func_name

from langchain.text_splitter import RecursiveCharacterTextSplitter

from services.utiles.json_clean import *

async def upload_article_to_db(article):
    try:
        cleaned_content = clean_html(article.content)
        word_count = len(cleaned_content.split())
        

        # Check if word count exceeds 1000
        if word_count > 2000:
            raise HTTPException(status_code=400, detail="Article content exceeds 1000 words")
        result = await articles_raw.insert_one({
            "title": article.title,
            "source": article.source,
            "upload_date": datetime.utcnow(),
            "content": cleaned_content
        })
        log_with_func_name("✅ Article uploaded successfully!")
        return result.inserted_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def chunk_article(article_id):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # use token count if you're tokenizing
        chunk_overlap=100
    )

    article = await articles_raw.find_one({"_id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Clean the article content
    content = article.get("content", "")
    cleaned_content = clean_html(content)
    cleaned_content = clean_content(cleaned_content)

    chunks = splitter.split_text(cleaned_content)

    # Store to MongoDB
    for index, chunk in enumerate(chunks):
        await articles_chunks.insert_one({
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

async def fetch_chunked_articles(article_id):
    # Query the MongoDB collection for the chunked articles
    #article_id = ObjectId(object_id_str)
    query = {
        "article_id": article_id,
        "$or": [
            {"status.summarized": False},
            {"status.word_explained": False}
        ]
    }
    chunked_articles_cursor = articles_chunks.find(query)
    
    chunks = []
    async for chunk in chunked_articles_cursor:
        chunk_text = chunk["chunk_text"]
        chunk_id = chunk["chunk_id"]
        chunks.append({"chunk_text": chunk_text, "chunk_id": chunk_id})
    
    return chunks

async def fetch_all_articles():
    """
    Fetch all articles from the articles_raw MongoDB collection that have etymology, contextual_meaning, and example_sentences fields.
    Returns a list of articles (as dicts), converting ObjectId and datetime for frontend compatibility.
    """
    try:
        cursor = articles_raw.find({})
        articles = []
        async for article in cursor:
            article["_id"] = str(article["_id"])
            print("article",article)
            for k, v in article.items():
                if hasattr(v, 'isoformat'):
                    article[k] = v.isoformat()
            articles.append(article)
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
