from app.core.config import Config
from app.core.templates.items_table import build_items_table_html
from app.core.templates.document_chrome import (
    base_styles,
    render_document_header,
    render_party_and_transport_block,
    render_bank_and_summary,
    render_terms_and_signature,
    render_footer,
)

def generate_invoice_html(invoice_data):
    """Generates print-ready HTML for Invoice documents."""
    inv = invoice_data
    order = inv['order']
    items = inv['items']
    hide_pricing_details = bool(inv.get('hide_pricing_details'))

    header_html, rows_html = build_items_table_html(items, hide_pricing_details=hide_pricing_details)

    doc_header = render_document_header(
        doc_label="TAX INVOICE",
        doc_number_label="Invoice #",
        doc_number=inv['invoice_number'],
        doc_date_label="Invoice Date",
        doc_date=inv['invoice_date'],
    )

    party_block = render_party_and_transport_block(
        party_label="BILLED TO",
        customer_name=order['customer_name_snapshot'],
        customer_gst=order['customer_gst_snapshot'],
        terms_label="Payment Terms",
        terms_value=order['customer_terms_snapshot'] or Config.DEFAULT_PAYMENT_TERMS,
        right_box_title="ORDER DETAILS",
        ref_label="Order Ref",
        ref_value=order['order_number'],
        created_label="Order Date",
        created_value=inv['created_at'][:10],
        transport_insurance_terms=order.get('customer_transport_insurance_snapshot'),
    )

    summary_block = render_bank_and_summary(
        subtotal=order['subtotal'],
        gst_rate=order['gst_rate'],
        gst_amount=order['gst_amount'],
        grand_total=order['grand_total'],
    )

    terms_and_signature = render_terms_and_signature(Config.INVOICE_TERMS_AND_CONDITIONS)

    footer = render_footer(
        f"{Config.COMPANY_NAME} &nbsp;|&nbsp; {Config.COMPANY_ADDRESS} &nbsp;|&nbsp; "
        f"{Config.COMPANY_EMAIL}<br>"
        "This is a computer generated invoice."
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            {base_styles()}
        </style>
    </head>
    <body>
        {doc_header}
        {party_block}

        <table class="items-table">
            <thead>
                {header_html}
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        {summary_block}
        {terms_and_signature}
        {footer}
    </body>
    </html>
    """
    return html
