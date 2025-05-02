import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unicodedata

from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize

from db.mongodb import articles_chunks, articles_raw
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException

import re

def clean_html(content):
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()

def clean_content(text):
    # Remove invisible characters
    text = re.sub(r'[\u200b-\u200f\u2028\u2029]', '', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Replace smart quotes
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('‘', "'").replace('’', "'")

    # Remove any strange tabs or carriage returns
    text = text.replace('\t', ' ').replace('\r', '')

    # Optional: remove weird unicode (like emoji) if you want
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = text.encode('utf-8', 'ignore').decode('utf-8')
    
    return text

### upload article service ###
async def upload_article_to_db(article):
    try:
        cleaned_content = clean_content(article["content"])
        word_count = len(cleaned_content.split())
        

        # Check if word count exceeds 1000
        if word_count > 2000:
            raise HTTPException(status_code=400, detail="Article content exceeds 1000 words")
        result = await articles_raw.insert_one({
            "title": article["title"],
            "source": article["source"],
            "upload_date": datetime.utcnow(),
            "content": cleaned_content
        })
        print("✅ Article uploaded successfully!:",result.inserted_id)
        return result.inserted_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
### upload article service ###

#####  chunk article service ######
async def chunk_article(article_id):
    # Fetch the article from the articles_raw collection
    article = await articles_raw.find_one({"_id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Clean the article content
    content = article.get("content", "")
    cleaned_content = clean_html(content)
    cleaned_content = clean_content(cleaned_content)
    
    # Tokenize into sentences
    sentences = sent_tokenize(cleaned_content)
    
    # Chunk sentences into manageable pieces
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > 200:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_length
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    # Store chunks in MongoDB
    for index, chunk in enumerate(chunks):
        await articles_chunks.insert_one({
            "chunk_id": f"{article_id}_{index}",
            "article_id": article_id,
            "chunk_index": index,
            "chunk_text": chunk,
            "status": {"summarized": False, "word_explained": False, "personas": False}
        })
#####  chunk article service ######


#####  fetch chunked articles service ######
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
#####  fetch chunked articles service ######




# Example usage
if __name__ == "__main__":
    import asyncio
    asyncio.run(chunk_article())