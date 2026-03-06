# vector_store/vector_build.py
"""
Run this script once to build the FAISS index from your MySQL products table.
Usage: python -m vector_store.vector_build
"""
import os
import json
import faiss
import numpy as np
from database.db import SessionLocal
from database.models import Product
from vector_store.embeddings import embed_texts
from config import VECTOR_DB_PATH
from utils.logger import logger


def build_index():
    os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)

    db = SessionLocal()
    try:
        products = db.query(Product).all()
        if not products:
            logger.warning("No products found in database. Seed products first.")
            return

        texts = [
            f"{p.name} {p.category} {p.description}"
            for p in products
        ]
        metadata = [
            {
                "id":          p.id,
                "name":        p.name,
                "category":    p.category,
                "description": p.description,
                "price":       float(p.price),
                "stock":       p.stock,
                "min_price":   float(p.min_price) if p.min_price else None,
            }
            for p in products
        ]

        logger.info(f"Embedding {len(texts)} products...")
        embeddings = embed_texts(texts)
        embeddings = np.array(embeddings).astype("float32")

        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        faiss.write_index(index, VECTOR_DB_PATH + ".faiss")
        with open(VECTOR_DB_PATH + "_meta.json", "w") as f:
            json.dump(metadata, f)

        logger.info(f"✅ FAISS index built with {len(texts)} products → {VECTOR_DB_PATH}")
    finally:
        db.close()


if __name__ == "__main__":
    build_index()
