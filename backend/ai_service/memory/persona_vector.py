import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from langchain.embeddings import OllamaEmbeddings  # or OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from services.persona_service import *
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib,json

embedding_fn = OllamaEmbeddings(model="nomic-embed-text")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)




vectorstore = Chroma(
    collection_name="persona_memory",
    embedding_function=embedding_fn,
    persist_directory="./chroma_db"  # ✅ persists to disk
)

# Store hash for last loaded data
_last_vectorstore_hash = None

def compute_data_hash(data: list[dict]) -> str:
    """
    Deterministically hash input data.
    """
    cleaned = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()

async def build_vector_store_from_text_sources(raw_inputs: list[dict]):
    """
    Input format: [{ "content": "full text or chunk", "metadata": {...} }, ...]
    """

    global _last_vectorstore_hash
    current_hash = compute_data_hash(raw_inputs)

    if _last_vectorstore_hash == current_hash:
        print("✅ Vector store already up to date.")
        return
    
    documents = []

    for item in raw_inputs:
        text = item["content"]
        metadata = item.get("metadata", {})

        # Skip empty input
        if not text.strip():
            continue

        chunks = splitter.split_text(text)
        for chunk in chunks:
            documents.append(Document(page_content=chunk, metadata=metadata))

    if documents:
        vectorstore.add_documents(documents)
        _last_vectorstore_hash = current_hash
        print("vectorstore embed.")
        # vectorstore.persist() automated persisted
    else:
        print("⚠️ No valid documents to embed.")

async def get_retriever(raw_inputs):
    await build_vector_store_from_text_sources(raw_inputs)
    return vectorstore.as_retriever(search_kwargs={"k": 5})

async def get_relevant_docs_by_role(role: str, query: str) -> list[Document]:
    raw_docs = await gather_single_persona_docs(role)
    if not raw_docs:
        print(f"⚠️ No raw docs found for role: {role}")
        return []
    retriever = await get_retriever(raw_docs)
    return await retriever.ainvoke(query)