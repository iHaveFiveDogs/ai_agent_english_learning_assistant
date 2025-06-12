import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.utiles.collection_utils import get_questions_answer_collection_by_base_tag
from collections import defaultdict

def group_by_article_id(docs):
    grouped = defaultdict(list)
    for doc in docs:
        # Convert ObjectId to str if needed for comparison/grouping
        article_id = str(doc.get('article_id'))
        # Optionally remove _id for cleaner output
        doc.pop('_id', None)
        grouped[article_id].append(doc)
    return list(grouped.values())



async def store_question_to_mongo(article_id, questions, tag):
    collection = get_questions_answer_collection_by_base_tag(tag)
    # If questions is a list, store each one
    if isinstance(questions, list):
        for q in questions:
            await collection.update_one(
                {"article_id": article_id, "chunk_id": q["chunk_id"]},
                {"$set": {"article_id": article_id, "chunk_id": q["chunk_id"], "questions": q["questions"]}},
                upsert=True
            )
    elif isinstance(questions, dict):
        await collection.update_one(
            {"article_id": article_id, "chunk_id": questions["chunk_id"]},
            {"$set": {"article_id": article_id, "chunk_id": questions["chunk_id"], "questions": questions["questions"]}},
            upsert=True
        )
    else:
        raise ValueError("Questions must be a dict or list of dicts")


async def fetch_chunked_questions(article_id, tag):
    collection = get_questions_answer_collection_by_base_tag(tag)
    cursor = await collection.find({"article_id": article_id}).to_list(None)
    return cursor