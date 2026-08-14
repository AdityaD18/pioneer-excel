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

def generate_quotation_html(quotation_data):
    """Generates print-ready HTML for Quotation documents."""
    q = quotation_data
    items = q['items']
    hide_pricing_details = bool(q.get('hide_pricing_details'))

    header_html, rows_html = build_items_table_html(items, hide_pricing_details=hide_pricing_details)

    doc_header = render_document_header(
        doc_label="QUOTATION",
        doc_number_label="Quotation #",
        doc_number=q['quotation_number'],
        doc_date_label="Date",
        doc_date=q['created_at'][:10],
        extra_meta_rows=[("Valid For", "30 Days")],
    )

    party_block = render_party_and_transport_block(
        party_label="PREPARED FOR",
        customer_name=q['customer_name_snapshot'],
        customer_gst=q['customer_gst_snapshot'],
        payment_value=q['customer_terms_snapshot'] or Config.DEFAULT_PAYMENT_TERMS,
        transport_insurance_terms=q.get('customer_transport_insurance_snapshot'),
    )

    summary_block = render_bank_and_summary(
        subtotal=q['subtotal'],
        gst_rate=q['gst_rate'],
        gst_amount=q['gst_amount'],
        grand_total=q['grand_total'],
    )

    terms_and_signature = render_terms_and_signature(Config.QUOTATION_TERMS_AND_CONDITIONS)

    footer = render_footer(
        f"Thank you for considering {Config.COMPANY_NAME}. &nbsp;|&nbsp; {Config.COMPANY_EMAIL}<br>"
        "This is a computer generated quotation. Prices are subject to final confirmation."
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
