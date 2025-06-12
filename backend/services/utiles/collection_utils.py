from db.mongodb import db

# Explicit tag-to-collection mapping
TAG_COLLECTION_MAP = {
    "news": {
        "raw": "articles_raw",
        "chunks": "articles_chunks",
        "persona":"personas"
    },
    "novels": {
        "raw":"novels_raw",
        "chunks":"novels_chunks",
        "persona":"personas"
    },
    "dramas": {
        "raw": "dramas_raw",
        "chunks": "dramas_chunks",
        "persona": "personas"
    }, 
    "nonfiction": {
        "raw" : "nonfiction_raw",
        "chunks": "nonfiction_chunks",
        "persona": "personas"
    }
}

def get_collections_for_tag(tag: str):
    mapping = TAG_COLLECTION_MAP.get(tag)
    if not mapping:
        raise ValueError(f"Unknown tag: {tag}")
    # For standard tags
    if "raw" in mapping and "chunks" in mapping and "persona" in mapping:
        raw_collection = db[mapping["raw"]]
        chunk_collection = db[mapping["chunks"]]
        persona_collection = db[mapping["persona"]]
        return raw_collection, chunk_collection, persona_collection
    raise ValueError(f"Tag {tag} does not support raw/chunks/persona collections")

# Mapping from base tag to questions_answer collection name
BASE_TAG_TO_QA_COLLECTION = {
    "news": "questions_answer_articles",
    "novels": "questions_answer_novels",
    "dramas": "questions_answer_dramas",
    "nonfiction": "questions_answer_nonfiction"
}

def get_questions_answer_collection_by_base_tag(tag: str):
    qa_tag = BASE_TAG_TO_QA_COLLECTION.get(tag)
    if not qa_tag:
        raise ValueError(f"No questions_answer collection for tag: {tag}")
    return db[qa_tag]
