from db.mongodb import db

# Explicit tag-to-collection mapping
TAG_COLLECTION_MAP = {
    "news": {
        "raw": "articles_raw",
        "chunks": "articles_chunks",
        "persona":"personas"
    },
    # Add more tag mappings here as needed
    # "science": {"raw": "science_articles_raw", "chunks": "science_articles_chunks"},
    "novels": {
        "raw":"novels_raw",
        "chunks":"novels_chunks",
        "persona":"personas"
    }
}

def get_collections_for_tag(tag: str):
    mapping = TAG_COLLECTION_MAP.get(tag)
    if not mapping:
        raise ValueError(f"Unknown tag: {tag}")
    raw_collection = db[mapping["raw"]]
    chunk_collection = db[mapping["chunks"]]
    persona_collection = db[mapping["persona"]]
    return raw_collection, chunk_collection, persona_collection
