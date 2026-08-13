from app.core.delivery_terms import compute_delivery_term


def build_items_table_html(items, hide_pricing_details=False):
    """
    Builds the <thead> row and <tbody> rows for the line-items table shared
    by the invoice and quotation PDF templates. Returns (header_html, rows_html).

    Every line's discount is applied per-item (Part A can carry a different
    discount % than Part B), so the discounted price is computed per row:
        discounted_rate_per_pc = rate_per_pc * (1 - discount_pct / 100)

    hide_pricing_details=False (default):
        Shows RATE (PER PC), DISC %, and a DISCOUNTED PRICE column that
        spells out the calculation, e.g. "Rs. 900.00 - 10% = Rs. 810.00".

    hide_pricing_details=True:
        Omits RATE (PER PC) and DISC % entirely. DISCOUNTED PRICE shows
        only the final per-piece rate (no breakdown, since showing the
        calculation would reveal the hidden discount %). Quantity,
        Total, and Delivery Terms are unchanged either way.
    """
    if hide_pricing_details:
        header_html = """
                <tr>
                    <th width="7%">SR NO</th>
                    <th width="33%">PART NUMBER / DESCRIPTION</th>
                    <th width="11%" style="text-align: right;">QTY (PCS)</th>
                    <th width="16%" style="text-align: right;">DISCOUNTED PRICE (PER PC)</th>
                    <th width="10%" style="text-align: right;">TOTAL</th>
                    <th width="23%" style="text-align: center;">DELIVERY TERMS</th>
                </tr>
        """
    else:
        header_html = """
                <tr>
                    <th width="5%">SR NO</th>
                    <th width="21%">PART NUMBER / DESCRIPTION</th>
                    <th width="7%" style="text-align: right;">QTY (PCS)</th>
                    <th width="10%" style="text-align: right;">RATE (PER PC)</th>
                    <th width="6%" style="text-align: right;">DISC %</th>
                    <th width="18%" style="text-align: right;">DISCOUNTED PRICE</th>
                    <th width="9%" style="text-align: right;">TOTAL</th>
                    <th width="18%" style="text-align: center;">DELIVERY TERMS</th>
                </tr>
        """

    rows_html = ""
    for idx, item in enumerate(items, 1):
        price_per_100 = float(item['unit_price'])
        rate_per_pc = price_per_100 / 100.0
        discount_pct = float(item['discount_percentage'] or 0)
        discounted_rate_per_pc = rate_per_pc * (1 - discount_pct / 100.0)
        delivery_term = compute_delivery_term(item['quantity'], item.get('current_stock', 0))

        if hide_pricing_details:
            rows_html += f"""
        <tr>
            <td style="text-align: center;">{idx}</td>
            <td><strong>{item['part_number_snapshot']}</strong><br><small>{item['part_name_snapshot'] or ''}</small></td>
            <td style="text-align: right;">{item['quantity']:,.0f}</td>
            <td style="text-align: right;"><strong>Rs. {discounted_rate_per_pc:,.2f}</strong></td>
            <td style="text-align: right;">Rs. {item['line_total']:,.2f}</td>
            <td style="text-align: center; font-size: 9pt;">{delivery_term}</td>
        </tr>
            """
        else:
            rows_html += f"""
        <tr>
            <td style="text-align: center;">{idx}</td>
            <td><strong>{item['part_number_snapshot']}</strong><br><small>{item['part_name_snapshot'] or ''}</small></td>
            <td style="text-align: right;">{item['quantity']:,.0f}</td>
            <td style="text-align: right;">Rs. {rate_per_pc:,.2f}</td>
            <td style="text-align: right;">{discount_pct:.1f}%</td>
            <td style="text-align: right; font-size: 9pt;">Rs. {rate_per_pc:,.2f} &minus; {discount_pct:.1f}% = <strong>Rs. {discounted_rate_per_pc:,.2f}</strong></td>
            <td style="text-align: right;">Rs. {item['line_total']:,.2f}</td>
            <td style="text-align: center; font-size: 9pt;">{delivery_term}</td>
        </tr>
            """

    return header_html, rows_html
