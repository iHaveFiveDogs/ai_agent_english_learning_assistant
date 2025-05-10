import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.mongodb import articles_chunks, articles_raw, personas_collection
from pymongo import UpdateOne
from bson import ObjectId
from services.utiles.print_function_name import log_with_func_name

async def if_there_are_persona(chunk_id):
    
    doc = await articles_chunks.find_one({"chunk_id": chunk_id})
    if doc.get("status", {}).get("personas") == True:
        log_with_func_name("✅ Personas already done, skipping.")
        return True
    else:
        return False
    result = await articles_chunks.update_one(
        {"chunk_id": chunk_id},
        {"$push": {
        "personas": {"$each": persona_list}
        },
        "$set": {
            "status.personas": True
        }}
    )
    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            print("✅ chunked Personas Update succeeded!")
        else:
            print("⚠️ Document found, but no changes were made (maybe duplicates or same data).")
    else:
        print("❌ No matching chunk found (chunk_id might be wrong).")

async def store_combined_persona_to_mongodb(article_id):

    log_with_func_name("Storing combined Personas...")
    cursor = await articles_chunks.find({"article_id": article_id}).to_list(None)

    all_personas = []

    for chunk in cursor:
        persona_list = chunk.get("personas", [])
        all_personas.extend([p for p in persona_list if p not in all_personas])
        
    result = await articles_raw.update_one(
        {"_id": article_id},
        {"$set": {"personas": all_personas}},
        upsert=True
    )
    

    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            log_with_func_name("✅ persona Update succeeded!")
        else:
            log_with_func_name("⚠️ persona service talking : Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ persona service talking : No matching article found (article_id might be wrong).")

async def merge_persona_documents(persona_name, collection):
    # Step 1: Find all docs for this persona
    docs = await collection.find({"persona": persona_name}).to_list(length=None)

    if len(docs) <= 1:
        return

    merged_articles = {}

    for doc in docs:
        for article in doc.get("articles", []):
            art_id = str(article["article_id"])
            if art_id not in merged_articles:
                merged_articles[art_id] = set()
            merged_articles[art_id].update(article.get("chunk_ids", []))

    # Step 2: Build final merged structure
    final_articles = [
        {
            "article_id": ObjectId(art_id),
            "chunk_ids": list(chunk_ids)
        }
        for art_id, chunk_ids in merged_articles.items()
    ]

    # Step 3: Keep the first doc, delete others
    main_id = docs[0]["_id"]
    other_ids = [doc["_id"] for doc in docs[1:]]

    await collection.delete_many({"_id": {"$in": other_ids}})
    await collection.update_one(
        {"_id": main_id},
        {"$set": {"articles": final_articles}}
    )

    log_with_func_name(f"✅ Merged {len(docs)} entries into one for persona '{persona_name}'")

async def merge_all_personas():
    distinct_names = await personas_collection.distinct("persona")
    for name in distinct_names:
        await merge_persona_documents(name, personas_collection)

async def upsert_persona_entries(article_id, chunk_id, persona_list):
    """
    For each persona, ensure:
    - Only one document per persona_name.
    - Inside it, only one article entry per article_id.
    - Each article entry has a unique chunk_ids list.
    """
    bulk_operations = []

    for persona in persona_list:
        # Ensure persona is not included in word_explanations
        if isinstance(persona, dict):
            continue

        # Add chunk_id to the correct article entry, or create it if needed
        update = UpdateOne(
            {"persona": persona, "articles.article_id": article_id},
            {"$addToSet": {"articles.$.chunk_ids": chunk_id}}
        )

        # If the persona or article_id entry doesn't exist at all, create both
        fallback_upsert = UpdateOne(
            {"persona": persona, "articles.article_id": {"$ne": article_id}},
            {
                "$setOnInsert": {"persona": persona},
                "$addToSet": {
                    "articles": {
                        "article_id": article_id,
                        "chunk_ids": [chunk_id]
                    }
                }
            },
            upsert=True
        )

        bulk_operations.append(update)
        bulk_operations.append(fallback_upsert)

    if bulk_operations:
        await personas_collection.bulk_write(bulk_operations)
        log_with_func_name("✅ Persona entries updated")

async def make_persona_update(chunk_id, persona_list):
    """
    
    """
    return UpdateOne(
        {"chunk_id": chunk_id},
        {"$set": {"personas": persona_list, "status.personas": True}}
    )

async def gather_all_persona_docs():
    all_docs = []
    async for persona_doc in personas_collection.find({}):
        persona = persona_doc["persona"]
        for article in persona_doc["articles"]:
            article_id = article["article_id"]
            for chunk_id in article["chunk_ids"]:
                chunk = await articles_chunks.find_one({"chunk_id": chunk_id})
                if chunk and "summary" in chunk:
                    all_docs.append({
                        "content": chunk["summary"],
                        "metadata": {
                            "persona": persona,
                            "chunk_id": chunk_id,
                            "article_id": article_id
                        }
                    })
    return all_docs

async def gather_single_persona_docs(persona_name: str):
    """
    Gather all summary documents related to a specific persona.
    Each document includes content (summary) and metadata.
    """
    all_docs = []

    persona_doc = await personas_collection.find_one({"persona": persona_name})
    if not persona_doc:
        print(f"⚠️ No persona found for '{persona_name}'")
        return []
    

    for article in persona_doc.get("articles", []):
        
        article_id = article["article_id"]
        for chunk_id in article.get("chunk_ids", []):
            chunk = await articles_chunks.find_one({"chunk_id": chunk_id})
            if chunk and "summary" in chunk:
                all_docs.append({
                    "content": chunk["summary"]["summary"] if isinstance(chunk["summary"], dict) else chunk["summary"],
                    "metadata": {
                        "persona": persona_name,
                        "chunk_id": chunk_id,
                        "article_id": str(article_id)
                    }
                })
    print(f"✅ prepared article for persona: {persona_name}")

    return all_docs

async def fetch_all_persona_names() -> list[str]:
    """
    Fetch all distinct persona names from the personas collection.
    """
    persona_names = await personas_collection.distinct("persona")
    return sorted(name.lower() for name in persona_names)

async def fetch_all_persona_names_through_article(article_id) -> list[str]:
    """
    Fetch all distinct persona names from the article.
    """
    doc = await articles_raw.find_one({"_id": article_id})
    if doc is None:
        print(f"[⚠️ WARNING] No article found with id: {article_id}")
        return []
    return sorted(name.lower() for name in doc.get("personas", []))