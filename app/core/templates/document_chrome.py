import os
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
        .doc-meta-table td { padding: 3px 0; }
        .doc-meta-label { color: #6B7280; text-align: left; width: 50%; }
        .doc-meta-value { font-weight: bold; text-align: right; color: #1A1A1A; width: 50%; }

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

        .bank-box {
            border: 1px solid #D1D5DB;
            padding: 6px 10px;
            font-size: 8pt;
            color: #374151;
            vertical-align: top;
        }
        .bank-title {
            font-size: 8pt;
            font-weight: bold;
            color: #0F1E33;
            margin-bottom: 2px;
            letter-spacing: 0.3px;
        }
        .bank-box table td { padding: 1px 0; font-size: 8pt; }
        .bank-label { color: #6B7280; width: 40%; }
        .bank-value { font-weight: bold; color: #1A1A1A; }

        .summary-box { vertical-align: top; }
        .summary-table td { padding: 2px 0; font-size: 9pt; }
        .summary-label { color: #4B5563; text-align: right; padding-right: 14px; }
        .summary-value { text-align: right; font-weight: bold; width: 110px; }
        .summary-divider-row td {
            border-top: 2px solid #0F1E33;
            line-height: 1px;
            font-size: 1px;
            padding: 0;
        }
        .summary-total-row td {
            padding-top: 8px;
            padding-bottom: 2px;
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
    additional lines under the doc number/date (e.g. quotation validity).

    If a logo file exists at Config.COMPANY_LOGO_PATH it's shown at a
    prominent size in place of the plain-text company name (this
    customer's logo already includes the company name as part of the
    artwork, so showing both would just duplicate the name) - the
    subtitle and address block still render underneath either way.
    If no logo file exists, this falls back to the plain text heading,
    with no broken-image icon or empty placeholder box."""
    meta_rows_html = ""
    if extra_meta_rows:
        for label, value in extra_meta_rows:
            meta_rows_html += f"""
                <tr>
                    <td class="doc-meta-label">{label}:</td>
                    <td class="doc-meta-value">{value}</td>
                </tr>
            """

    logo_full_path = os.path.join(Config.BASE_DIR, Config.COMPANY_LOGO_PATH)
    if os.path.isfile(logo_full_path):
        # xhtml2pdf does not reliably honor CSS max-width/max-height on
        # <img> - it needs explicit width/height HTML attributes, or it
        # renders the image at full native resolution (this was verified
        # directly: a 635x710px source logo blew out to ~500px wide in the
        # actual PDF despite max-height:72px in the style attribute).
        # Compute the correct pixel size from the real image dimensions so
        # it renders at the intended compact header size.
        target_height = 60
        try:
            from PIL import Image as _PILImage
            with _PILImage.open(logo_full_path) as _img:
                _w, _h = _img.size
            target_width = max(1, round(target_height * _w / _h))
        except Exception:
            target_width = target_height
        company_identity_html = f'<img src="{logo_full_path}" width="{target_width}" height="{target_height}" style="margin-bottom: 4px;">'
    else:
        company_identity_html = f'<div class="company-name">{Config.COMPANY_NAME}</div>'

    return f"""
    <table class="doc-header-table">
        <tr>
            <td width="58%" style="vertical-align: top;">
                {company_identity_html}
                <div class="company-meta">
                    {Config.COMPANY_ADDRESS}<br>
                    GSTIN/UIN: {Config.COMPANY_GSTIN}<br>
                    State Name : {Config.COMPANY_STATE_NAME}, Code : {Config.COMPANY_STATE_CODE}<br>
                    E-Mail : {Config.COMPANY_EMAIL}
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


def render_party_and_transport_block(party_label, customer_name, customer_gst, payment_value, transport_insurance_terms=None, right_box_title=None, ref_label=None, ref_value=None):
    """Customer info box (left), with Payment and (if set) Transport &
    Insurance shown as consecutive lines in the same box - not a
    separate full-width section. An optional right-hand reference box
    (right_box_title/ref_label/ref_value) is only rendered when given;
    when omitted the left box takes the full width instead of leaving a
    redundant/empty column, since callers only pass this when there's
    genuinely non-duplicate information to show (e.g. an Order Ref that
    differs from the Invoice # already shown in the header) - for
    quotations, where the reference number and date were identical to
    what's already in the header, callers simply don't pass a right box
    at all rather than repeating the same numbers a second time.

    Each box's detail lines are joined with <br> inside a single <div>
    rather than several separate <div class="party-detail"> blocks -
    xhtml2pdf renders each block-level element as its own Paragraph with
    extra implicit spacing, which is what caused a noticeably sparse,
    gappy look between lines in a box with only 2-3 short lines."""
    transport_line = ""
    if transport_insurance_terms:
        transport_line = f"<br>Transport &amp; Insurance: {transport_insurance_terms}"

    left_box_html = f"""
                <div class="party-label">{party_label}</div>
                <div class="party-name">{customer_name}</div>
                <div class="party-detail">
                    GSTIN: {customer_gst or 'N/A'}<br>
                    Payment: {payment_value}{transport_line}
                </div>
    """

    if right_box_title:
        return f"""
    <table class="party-table">
        <tr>
            <td width="50%" class="party-box">
                {left_box_html}
            </td>
            <td width="50%" class="party-box" style="border-left: none;">
                <div class="party-label">{right_box_title}</div>
                <div class="party-detail">
                    {ref_label}: <strong>{ref_value}</strong>
                </div>
            </td>
        </tr>
    </table>
        """

    return f"""
    <table class="party-table">
        <tr>
            <td width="100%" class="party-box">
                {left_box_html}
            </td>
        </tr>
    </table>
    """


def render_bank_and_summary(subtotal, gst_rate, gst_amount, grand_total):
    """Bank/payment details (left) alongside the subtotal/GST/total summary
    (right), followed by the Amount in Words line. Bank fields are pulled
    from Config/.env - placeholders until updated with real account
    details, but presented as a normal payment details box rather than
    anything visibly marked 'demo'."""
    return f"""
    <table class="bottom-section-table">
        <tr>
            <td width="55%" class="bank-box">
                <div class="bank-title">PAYMENT / BANK DETAILS</div>
                <table>
                    <tr><td class="bank-label">Account Name</td><td class="bank-value">{Config.BANK_ACCOUNT_NAME}</td></tr>
                    <tr><td class="bank-label">Bank</td><td class="bank-value">{Config.BANK_NAME}</td></tr>
                    <tr><td class="bank-label">Account Type</td><td class="bank-value">{Config.BANK_ACCOUNT_TYPE}</td></tr>
                    <tr><td class="bank-label">Account Number</td><td class="bank-value">{Config.BANK_ACCOUNT_NUMBER}</td></tr>
                    <tr><td class="bank-label">IFSC / NEFT / RTGS</td><td class="bank-value">{Config.BANK_IFSC}</td></tr>
                    <tr><td class="bank-label">Branch</td><td class="bank-value">{Config.BANK_BRANCH}</td></tr>
                </table>
            </td>
            <td width="5%"></td>
            <td width="40%" class="summary-box">
                <table class="summary-table">
                    <tr>
                        <td class="summary-label">Subtotal</td>
                        <td class="summary-value">Rs. {subtotal:,.2f}</td>
                    </tr>
                    <tr>
                        <td class="summary-label">GST ({gst_rate}%)</td>
                        <td class="summary-value">Rs. {gst_amount:,.2f}</td>
                    </tr>
                    <tr class="summary-divider-row">
                        <td colspan="2">&nbsp;</td>
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
