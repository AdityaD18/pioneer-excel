from app.core.delivery_terms import compute_delivery_term


def build_items_table_html(items, hide_pricing_details=False):
    """
    Builds the <thead> row and <tbody> rows for the line-items table shared
    by the invoice and quotation PDF templates. Returns (header_html, rows_html).

    Every line's discount is applied per-item (Part A can carry a different
    discount % than Part B), so the discounted price is computed per row:
        discounted_rate_per_pc = rate_per_pc * (1 - discount_pct / 100)

    hide_pricing_details=False (default):
        Shows RATE, DISC %, and DISCOUNTED PRICE as plain columns - the
        Rate and Disc % columns already make the calculation visible, so
        Discounted Price is just the clean final number rather than a
        restated formula.

    hide_pricing_details=True:
        Omits RATE and DISC % entirely. DISCOUNTED PRICE still shows just
        the final per-piece rate. Quantity, Total, and Delivery Terms are
        unchanged either way.
    """
    if hide_pricing_details:
        header_html = """
                <tr>
                    <th width="6%">#</th>
                    <th width="30%" style="text-align: left;">PART NO. / DESCRIPTION</th>
                    <th width="10%" style="text-align: right;">QTY</th>
                    <th width="16%" style="text-align: right;">DISCOUNTED PRICE</th>
                    <th width="12%" style="text-align: right;">TOTAL</th>
                    <th width="26%" style="text-align: center;">DELIVERY TERMS</th>
                </tr>
        """
    else:
        header_html = """
                <tr>
                    <th width="5%">#</th>
                    <th width="23%" style="text-align: left;">PART NO. / DESCRIPTION</th>
                    <th width="7%" style="text-align: right;">QTY</th>
                    <th width="11%" style="text-align: right;">RATE</th>
                    <th width="7%" style="text-align: right;">DISC</th>
                    <th width="13%" style="text-align: right;">DISCOUNTED PRICE</th>
                    <th width="11%" style="text-align: right;">TOTAL</th>
                    <th width="23%" style="text-align: center;">DELIVERY TERMS</th>
                </tr>
        """

    rows_html = ""
    for idx, item in enumerate(items, 1):
        price_per_100 = float(item['unit_price'])
        rate_per_pc = price_per_100 / 100.0
        discount_pct = float(item['discount_percentage'] or 0)
        discounted_rate_per_pc = rate_per_pc * (1 - discount_pct / 100.0)
        delivery_term = compute_delivery_term(item['quantity'], item.get('current_stock', 0))
        alt_class = ' class="alt-row"' if idx % 2 == 0 else ''

        if hide_pricing_details:
            rows_html += f"""
        <tr{alt_class}>
            <td style="text-align: center;">{idx}</td>
            <td><strong>{item['part_number_snapshot']}</strong><br><span style="font-size: 7.8pt; color: #6B7280;">{item['part_name_snapshot'] or ''}</span></td>
            <td style="text-align: right;">{item['quantity']:,.0f}</td>
            <td style="text-align: right;"><strong>Rs. {discounted_rate_per_pc:,.2f}</strong></td>
            <td style="text-align: right;">Rs. {item['line_total']:,.2f}</td>
            <td style="text-align: center; font-size: 8pt;">{delivery_term}</td>
        </tr>
            """
        else:
            rows_html += f"""
        <tr{alt_class}>
            <td style="text-align: center;">{idx}</td>
            <td><strong>{item['part_number_snapshot']}</strong><br><span style="font-size: 7.8pt; color: #6B7280;">{item['part_name_snapshot'] or ''}</span></td>
            <td style="text-align: right;">{item['quantity']:,.0f}</td>
            <td style="text-align: right;">Rs. {rate_per_pc:,.2f}</td>
            <td style="text-align: right;">{discount_pct:.1f}%</td>
            <td style="text-align: right;"><strong>Rs. {discounted_rate_per_pc:,.2f}</strong></td>
            <td style="text-align: right;">Rs. {item['line_total']:,.2f}</td>
            <td style="text-align: center; font-size: 8pt;">{delivery_term}</td>
        </tr>
            """

    return header_html, rows_html
