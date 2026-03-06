# vector_store/vector_search.py
import os
import json
import faiss
import numpy as np
from vector_store.embeddings import embed_texts
from config import VECTOR_DB_PATH
from utils.logger import logger

_index    = None
_metadata = None


def _load_index():
    global _index, _metadata
    if _index is None:
        faiss_path = VECTOR_DB_PATH + ".faiss"
        meta_path  = VECTOR_DB_PATH + "_meta.json"

        if not os.path.exists(faiss_path):
            logger.warning("FAISS index not found. Run vector_store/vector_build.py first.")
            return False

        _index = faiss.read_index(faiss_path)
        with open(meta_path, "r") as f:
            _metadata = json.load(f)
        logger.info("✅ FAISS index loaded.")
    return True


def search_products(query: str, top_k: int = 3) -> list[dict]:
    if not _load_index():
        return []
    try:
        query_vec = embed_texts([query])
        query_vec = np.array(query_vec).astype("float32")
        distances, indices = _index.search(query_vec, top_k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(_metadata):
                results.append(_metadata[idx])
        return results
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return []
