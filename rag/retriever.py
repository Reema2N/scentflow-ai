from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from rag.reranker import rerank_by_note_matches

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_PATH = PROJECT_ROOT / "data" / "processed" / "chroma_db"

COLLECTION_NAME = "perfumes"

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"


def get_vector_store():
    """Load the existing perfume Chroma vector database."""

    embeddings = HuggingFaceEmbeddings( model_name=EMBEDDING_MODEL )

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_PATH),
        embedding_function=embeddings,
    )

    return vector_store


def retrieve_similar_perfumes(query: str, query_notes: list[str], fetch_k: int = 10, top_k: int = 5,):
    """Retrieve semantic candidates and rerank them by fragrance-note matches."""

    vector_store = get_vector_store()

    candidates = vector_store.similarity_search(query=query, k=fetch_k,)

    reranked = rerank_by_note_matches(documents=candidates, query_notes=query_notes,)

    return reranked[:top_k]