import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.mongodb import articles_raw
import asyncio
async def deduplicate_word_explanations_in_articles_raw():
    cursor = articles_raw.find({}, {"_id": 1, "word_explanations": 1})
    async for doc in cursor:
        word_packs = doc.get("word_explanations", [])
        seen = set()
        cleaned = []
        for pack in word_packs:
            word = pack.get("word", "").lower().strip()
            if word and word not in seen:
                seen.add(word)
                cleaned.append(pack)

        await articles_raw.update_one(
            {"_id": doc["_id"]},
            {"$set": {"word_explanations": cleaned}}
        )
        print(f"🧼 Cleaned duplicates for article: {doc['_id']}")

if __name__ == "__main__":
    asyncio.run(deduplicate_word_explanations_in_articles_raw()) 
