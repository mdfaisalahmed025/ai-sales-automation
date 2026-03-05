from database.db import get_db_connection


def get_products():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return products


def create_order(customer_name, product_name, price):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO orders (customer_name, product_name, price)
    VALUES (%s,%s,%s)
    """

    cursor.execute(query, (customer_name, product_name, price))

    conn.commit()

    cursor.close()
    conn.close()