import faiss
import numpy as np
from vector_store.embeddings import create_embedding
from database.models import get_products


def build_vector_store():

    print("Loading products...")

    products = get_products()

    print("Products found:", len(products))

    texts = [
        f"{p['name']} {p['description']}"
        for p in products
    ]

    print("Generating embeddings...")

    embeddings = [create_embedding(t) for t in texts]

    print("Embeddings created")

    dim = len(embeddings[0])

    index = faiss.IndexFlatL2(dim)

    index.add(np.array(embeddings))

    print("Writing FAISS index...")

    faiss.write_index(index, "products.index")

    print("Vector store created")


if __name__ == "__main__":
    build_vector_store()