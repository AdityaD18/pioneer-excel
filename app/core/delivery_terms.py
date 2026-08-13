def compute_delivery_term(quantity, current_stock):
    """
    Determines the Delivery Terms text for an invoice/quotation line item by
    comparing the required quantity against the current closing stock.

    Rules:
      - Required qty <= closing stock  -> "EX STOCK PRIOR TO SALE"
      - Required qty >  closing stock, but some stock exists -> closing
        stock quantity is called out as Ex-Stock, with the balance flagged
        as a 4-6 Weeks lead time.
      - No closing stock available (0 or negative) -> "4-6 WEEKS" directly.
    """
    qty = float(quantity or 0)
    stock = float(current_stock or 0)

    if stock <= 0:
        return "4-6 WEEKS"

    if qty <= stock:
        return "EX STOCK PRIOR TO SALE"

    # Required quantity exceeds what's currently in stock
    return f"{stock:,.0f} PCS EX STOCK, REMAINING 4-6 WEEKS"
