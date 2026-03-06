# vector_store/embeddings.py
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
from utils.logger import logger

_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def embed_texts(texts: list[str]) -> list:
    model = get_embedding_model()
    return model.encode(texts, convert_to_numpy=True)