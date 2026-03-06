# automation/discount_engine.py

def calculate_discount(
    original_price: float,
    min_price: float,
    quantity: int = 1,
    is_returning: bool = False
) -> dict:
    discount_pct = 0.0

    if quantity >= 3:
        discount_pct += 0.15
    else:
        discount_pct += 0.10

    if is_returning:
        discount_pct += 0.05

    discounted = round(original_price * (1 - discount_pct), 2)
    final_price = max(discounted, min_price)
    actual_pct  = round((1 - final_price / original_price) * 100, 1)

    return {
        "original_price":  original_price,
        "final_price":     final_price,
        "discount_percent": actual_pct,
        "savings":         round(original_price - final_price, 2)
    }
