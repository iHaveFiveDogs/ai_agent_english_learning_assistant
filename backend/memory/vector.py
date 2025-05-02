from langchain.embeddings import OllamaEmbeddings  # or OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

embedding_fn = OllamaEmbeddings(model="nomic-embed-text")

vectorstore = Chroma(
    collection_name="persona_memory",
    embedding_function=embedding_fn,
    persist_directory="./chroma_db"  # ✅ persists to disk
)
