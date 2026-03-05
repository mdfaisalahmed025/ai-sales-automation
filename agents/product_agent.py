from vector_store.vector_search import search_products


def product_agent(query):

    results = search_products(query)

    if not results:
        return "No product found"

    response = "Here are some products:\n"

    for p in results:

        response += f"""
        {p['name']}
        Price: {p['price']}
        Description: {p['description']}
        """

    return response