from database.models import create_order

def create_customer_order(name, product, price):

    create_order(name, product, price)

    return "Order placed successfully"