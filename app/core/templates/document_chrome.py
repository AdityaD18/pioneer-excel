from app.core.config import Config
from app.core.templates.number_to_words import amount_to_words


def base_styles():
    """
    Shared CSS for both invoice and quotation PDFs. A single restrained
    navy + brass palette is used for both document types (rather than a
    different color per type) so the two read as the same corporate
    identity - the document label badge is what distinguishes them, not
    the whole color scheme.
    """
    return """
        @page {
            size: A4;
            margin: 1.1cm 1.4cm;
        }
        * { box-sizing: border-box; }
        body {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 9.5pt;
            color: #1A1A1A;
            line-height: 1.45;
        }
        table { border-collapse: collapse; width: 100%; }

        .doc-header-table { margin-bottom: 8px; }
        .company-name {
            font-size: 19pt;
            font-weight: bold;
            color: #0F1E33;
            letter-spacing: -0.3px;
        }
        .company-subtitle {
            font-size: 8.5pt;
            color: #6B7280;
            margin-top: 2px;
        }
        .company-meta {
            font-size: 8pt;
            color: #4B5563;
            margin-top: 4px;
            line-height: 1.45;
        }
        .doc-badge {
            display: block;
            font-size: 16pt;
            font-weight: bold;
            color: #FFFFFF;
            background-color: #0F1E33;
            padding: 6px 16px;
            text-align: center;
            letter-spacing: 1px;
        }
        .doc-meta-table {
            margin-top: 8px;
            font-size: 8.5pt;
        }
        .doc-meta-table td { padding: 1px 0; }
        .doc-meta-label { color: #6B7280; text-align: right; padding-right: 8px; }
        .doc-meta-value { font-weight: bold; text-align: right; color: #1A1A1A; }

        .divider-rule {
            border: none;
            border-top: 2px solid #B8863B;
            margin: 0 0 8px 0;
        }

        .party-table { margin-bottom: 8px; }
        .party-box {
            border: 1px solid #D1D5DB;
            padding: 6px 10px;
            vertical-align: top;
        }
        .party-label {
            font-size: 7.5pt;
            font-weight: bold;
            color: #B8863B;
            letter-spacing: 0.6px;
            margin-bottom: 3px;
        }
        .party-name { font-size: 10.5pt; font-weight: bold; color: #0F1E33; margin-bottom: 2px; }
        .party-detail { font-size: 8.5pt; color: #374151; line-height: 1.5; }

        .transport-box {
            border: 1px solid #D1D5DB;
            border-top: none;
            padding: 6px 10px;
            font-size: 8.5pt;
            color: #374151;
            margin-bottom: 8px;
        }
        .transport-label {
            font-weight: bold;
            color: #B8863B;
            font-size: 7.5pt;
            letter-spacing: 0.6px;
        }

        .items-table { margin-bottom: 0; }
        .items-table thead th {
            background-color: #0F1E33;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 8pt;
            padding: 5px 6px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }
        .items-table tbody td {
            padding: 4px 6px;
            border-bottom: 1px solid #E5E7EB;
            font-size: 8.5pt;
            vertical-align: top;
        }
        .items-table tbody tr.alt-row { background-color: #F7F8FA; }

        .bottom-section-table { margin-top: 8px; }

        .summary-box { vertical-align: top; }
        .summary-table td { padding: 2px 0; font-size: 9pt; }
        .summary-label { color: #4B5563; text-align: right; padding-right: 14px; }
        .summary-value { text-align: right; font-weight: bold; width: 110px; }
        .summary-total-row td {
            border-top: 2px solid #0F1E33;
            padding-top: 4px;
            font-size: 11pt;
            font-weight: bold;
            color: #0F1E33;
        }

        .amount-words-box {
            border: 1px solid #D1D5DB;
            background-color: #F7F8FA;
            padding: 5px 10px;
            font-size: 8.5pt;
            margin-top: 6px;
        }
        .amount-words-label {
            font-weight: bold;
            color: #B8863B;
            font-size: 7.5pt;
            letter-spacing: 0.5px;
        }

        .terms-section { margin-top: 8px; }
        .terms-title {
            font-size: 8.5pt;
            font-weight: bold;
            color: #0F1E33;
            margin-bottom: 3px;
            letter-spacing: 0.3px;
        }
        .terms-list {
            font-size: 7.8pt;
            color: #4B5563;
            margin: 0;
            padding-left: 14px;
        }
        .terms-list li { margin-bottom: 1px; }

        .signature-table { margin-top: 10px; }
        .signature-box { text-align: center; font-size: 8.5pt; color: #374151; }
        .signature-for { font-weight: bold; color: #0F1E33; margin-bottom: 20px; }
        .signature-line {
            border-top: 1px solid #1A1A1A;
            padding-top: 4px;
            width: 180px;
            margin: 0 auto;
        }

        .footer {
            margin-top: 10px;
            border-top: 1px solid #D1D5DB;
            padding-top: 5px;
            font-size: 7.5pt;
            color: #9CA3AF;
            text-align: center;
        }
    """


def render_document_header(doc_label, doc_number_label, doc_number, doc_date_label, doc_date, extra_meta_rows=None):
    """Company identity block (left) + document type badge and reference
    numbers (right). extra_meta_rows: list of (label, value) tuples for
    additional lines under the doc number/date (e.g. quotation validity)."""
    meta_rows_html = ""
    if extra_meta_rows:
        for label, value in extra_meta_rows:
            meta_rows_html += f"""
                <tr>
                    <td class="doc-meta-label">{label}:</td>
                    <td class="doc-meta-value">{value}</td>
                </tr>
            """

    return f"""
    <table class="doc-header-table">
        <tr>
            <td width="58%" style="vertical-align: top;">
                <div class="company-name">{Config.COMPANY_NAME}</div>
                <div class="company-subtitle">{Config.COMPANY_SUBTITLE}</div>
                <div class="company-meta">
                    {Config.COMPANY_ADDRESS}<br>
                    GSTIN: {Config.COMPANY_GSTIN} &nbsp;|&nbsp; PAN: {Config.COMPANY_PAN}<br>
                    {Config.COMPANY_PHONE} &nbsp;|&nbsp; {Config.COMPANY_EMAIL} &nbsp;|&nbsp; {Config.COMPANY_WEBSITE}
                </div>
            </td>
            <td width="42%" style="vertical-align: top;">
                <div class="doc-badge">{doc_label}</div>
                <table class="doc-meta-table">
                    <tr>
                        <td class="doc-meta-label">{doc_number_label}:</td>
                        <td class="doc-meta-value">{doc_number}</td>
                    </tr>
                    <tr>
                        <td class="doc-meta-label">{doc_date_label}:</td>
                        <td class="doc-meta-value">{doc_date}</td>
                    </tr>
                    {meta_rows_html}
                </table>
            </td>
        </tr>
    </table>
    <hr class="divider-rule">
    """


def render_party_and_transport_block(party_label, customer_name, customer_gst, terms_label, terms_value, right_box_title, ref_label, ref_value, created_label, created_value, transport_insurance_terms=None):
    """Customer / order-reference two-column info block, with an optional
    full-width Transport & Insurance Terms row directly beneath it.

    Each box's detail lines are joined with <br> inside a single <div>
    rather than several separate <div class="party-detail"> blocks -
    xhtml2pdf renders each block-level element as its own Paragraph with
    extra implicit spacing, which is what caused the noticeably sparse,
    gappy look between lines in a box with only 2-3 short lines."""
    transport_html = ""
    if transport_insurance_terms:
        transport_html = f"""
        <div class="transport-box">
            <span class="transport-label">TRANSPORT &amp; INSURANCE TERMS:</span>
            {transport_insurance_terms}
        </div>
        """

    return f"""
    <table class="party-table">
        <tr>
            <td width="50%" class="party-box">
                <div class="party-label">{party_label}</div>
                <div class="party-name">{customer_name}</div>
                <div class="party-detail">
                    GSTIN: {customer_gst or 'N/A'}<br>
                    {terms_label}: {terms_value}
                </div>
            </td>
            <td width="50%" class="party-box" style="border-left: none;">
                <div class="party-label">{right_box_title}</div>
                <div class="party-detail">
                    {ref_label}: <strong>{ref_value}</strong><br>
                    {created_label}: {created_value}
                </div>
            </td>
        </tr>
    </table>
    {transport_html}
    """


def render_summary(subtotal, gst_rate, gst_amount, grand_total):
    """Right-aligned subtotal/GST/total summary, followed by the Amount
    in Words line."""
    return f"""
    <table class="bottom-section-table">
        <tr>
            <td width="55%"></td>
            <td width="45%" class="summary-box">
                <table class="summary-table">
                    <tr>
                        <td class="summary-label">Subtotal</td>
                        <td class="summary-value">Rs. {subtotal:,.2f}</td>
                    </tr>
                    <tr>
                        <td class="summary-label">GST ({gst_rate}%)</td>
                        <td class="summary-value">Rs. {gst_amount:,.2f}</td>
                    </tr>
                    <tr class="summary-total-row">
                        <td class="summary-label">Grand Total</td>
                        <td class="summary-value">Rs. {grand_total:,.2f}</td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    <div class="amount-words-box">
        <span class="amount-words-label">AMOUNT IN WORDS:</span>
        {amount_to_words(grand_total)}
    </div>
    """


def render_terms_and_signature(terms_pipe_delimited):
    """Numbered Terms & Conditions list plus an authorized-signatory block,
    laid out side by side."""
    terms_items = [t.strip() for t in (terms_pipe_delimited or "").split("|") if t.strip()]
    terms_html = "".join(f"<li>{t}</li>" for t in terms_items)

    return f"""
    <table class="signature-table">
        <tr>
            <td width="60%" style="vertical-align: top;">
                <div class="terms-section">
                    <div class="terms-title">TERMS &amp; CONDITIONS</div>
                    <ol class="terms-list">
                        {terms_html}
                    </ol>
                </div>
            </td>
            <td width="40%" class="signature-box">
                <div class="signature-for">For {Config.COMPANY_NAME}</div>
                <div class="signature-line">Authorized Signatory</div>
            </td>
        </tr>
    </table>
    """


def render_footer(text):
    return f'<div class="footer">{text}</div>'
