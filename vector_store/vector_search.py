import faiss
import numpy as np
from vector_store.embeddings import create_embedding
from database.models import get_products

index = faiss.read_index("products.index")

products = get_products()


def search_products(query):

    query_embedding = create_embedding(query)

    D, I = index.search(
        np.array([query_embedding]),
        k=3
    )

    results = []

    for idx in I[0]:
        results.append(products[idx])

    return results