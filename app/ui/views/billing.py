import re
import streamlit as st
import pandas as pd
from app.providers import get_data_provider
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService
from app.services.invoice_service import InvoiceService
from app.services.quotation_service import QuotationService
from app.services.product_service import ProductService
from app.services.inventory_service import InventoryService
from app.core.config import Config
from app.ui.styles import render_html, draw_metric_card, trigger_toast
from app.core.pdf_generator import generate_invoice_html, generate_quotation_html, generate_pdf_from_html

def parse_pasted_products_text(raw_text, all_prods):
    """
    Parses multi-line pasted product data from Excel/CSV/tables.
    Supports tab, comma, or space separated lines: PartNumber [TAB] Quantity [TAB] Discount%
    """
    if not raw_text or not raw_text.strip():
        return [], 0
        
    prod_lookup = {}
    for p in all_prods:
        part_clean = p['part_number'].strip().lower()
        prod_lookup[part_clean] = p
        
    parsed_items = []
    unrecognized_count = 0
    
    lines = raw_text.strip().split('\n')
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.lower().startswith('part') or line_clean.lower().startswith('item'):
            continue
            
        # Split by tab, comma, or multiple spaces
        tokens = [t.strip() for t in re.split(r'[\t,;\s]+', line_clean) if t.strip()]
        if not tokens:
            continue
            
        part_code = tokens[0].lower()
        matched_prod = prod_lookup.get(part_code)
        
        # Try substring search if exact match not found
        if not matched_prod:
            for k, p_obj in prod_lookup.items():
                if part_code in k or k in part_code:
                    matched_prod = p_obj
                    break
                    
        if matched_prod:
            qty = 100.0
            disc = 0.0
            if len(tokens) >= 2:
                try:
                    qty = float(tokens[1].replace(',', '').replace('%', ''))
                except ValueError:
                    qty = 100.0
            if len(tokens) >= 3:
                try:
                    disc = float(tokens[2].replace(',', '').replace('%', ''))
                except ValueError:
                    disc = 0.0
                    
            parsed_items.append({
                "product_id": matched_prod['id'],
                "part_number": matched_prod['part_number'],
                "quantity": qty,
                "discount_percentage": disc,
                "unit_price_100": matched_prod['price_100']
            })
        else:
            unrecognized_count += 1
            
    return parsed_items, unrecognized_count

def render_billing_builder(mode="invoice"):
    """
    Shared Document Builder Component for Tax Invoices and Commercial Quotations.
    mode: 'invoice' | 'quotation'
    """
    provider = get_data_provider()
    all_prods = ProductService.get_all_billing_products()
    prod_map = {f"{p['part_number']} - {p['part_name'] or ''}": p for p in all_prods}
    prod_names = ["-- Select Product --"] + list(prod_map.keys())
    
    session_key = f"{mode}_cart_items"
    if session_key not in st.session_state:
        st.session_state[session_key] = []
        
    # Title & Subtitle Header
    icon_cls = "fa-solid fa-file-invoice-dollar" if mode == "invoice" else "fa-solid fa-file-lines"
    title_text = "Tax Invoice Builder" if mode == "invoice" else "Commercial Quotation Builder"
    sub_text = "Generate GST Tax Invoices with strict stock deduction & PDF export." if mode == "invoice" else "Create Commercial Price Quotations with validity terms & PDF download."
    
    render_html(f'<div class="section-head"><i class="{icon_cls}"></i> {title_text}</div>')
    st.caption(sub_text)

    # Top Toolbar: Live Google Sheets Sync & Safety Buffer Banner
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        buf_val = st.session_state.get("safety_stock_buffer", Config.SAFETY_STOCK_BUFFER)
        gs_url = st.session_state.get("google_sheets_url", Config.GOOGLE_SHEETS_STOCK_URL)
        gs_status = "Connected" if gs_url else "Not Configured"
        st.info(f"🛡️ **Safety Stock Buffer**: `{buf_val} PCS` | 🌐 **Live Google Stock Sync**: `{gs_status}`")
    with col_t2:
        if st.button("⚡ Sync Live Stock", use_container_width=True, key=f"btn_sync_live_{mode}"):
            if not gs_url:
                st.error("Configure Google Sheets URL in Settings first.")
            else:
                with st.spinner("Syncing live stock from Google Sheets..."):
                    res = provider.sync_from_web_url(gs_url, imported_by=f"Live Sync ({mode.title()})")
                    if res['status'] in ('success', 'partial_success'):
                        trigger_toast(f"Synced {res['successful_records']:,} items live!", icon="⚡")
                        st.rerun()
                    else:
                        st.error(f"Sync failed: {', '.join(res['errors'])}")

    # 1. Customer Selection
    col_b1, col_b2, col_b3 = st.columns(3)
    customers = CustomerService.get_customers()
    cust_opts = ["-- Select Customer --"] + [f"{c['name']} (ID: {c['id']})" for c in customers]
    
    with col_b1:
        sel_cust_str = st.selectbox("👤 Select Customer", cust_opts, key=f"{mode}_cust_select")
        
    selected_cust = None
    if sel_cust_str != "-- Select Customer --":
        c_id = int(sel_cust_str.split("ID: ")[1].replace(")", ""))
        selected_cust = CustomerService.get_customer_by_id(c_id)
        
    with col_b2:
        disc_val = st.number_input(
            "🏷️ Customer Discount (%)", 
            min_value=0.0, max_value=100.0, 
            value=float(selected_cust['discount_percentage']) if selected_cust else 0.0, 
            step=0.5,
            key=f"{mode}_cust_discount"
        )
    with col_b3:
        gst_no = st.text_input("🏢 GSTIN Number", value=selected_cust['gst_number'] if selected_cust and selected_cust['gst_number'] else "", key=f"{mode}_gstin")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Line Items Section (Dropdown Add + Multi-Product Clipboard Paste)
    render_html('<div class="setting-section"><div class="setting-section-title"><i class="fa-solid fa-cart-flatbed"></i> Line Items Builder</div></div>')
    
    tab_single, tab_multi = st.tabs(["➕ Single Item Dropdown", "📋 Multi-Product Clipboard Paste"])
    
    with tab_single:
        c_add1, c_add2, c_add3, c_add4 = st.columns([3, 1, 1, 1])
        with c_add1:
            p_sel = st.selectbox("Select Product Part Number", prod_names, key=f"{mode}_add_prod")
        with c_add2:
            p_qty = st.number_input("Quantity (PCS)", min_value=1.0, value=100.0, step=10.0, key=f"{mode}_add_qty")
        with c_add3:
            p_disc = st.number_input("Disc %", min_value=0.0, max_value=100.0, value=disc_val, step=0.5, key=f"{mode}_add_disc")
        with c_add4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add Item", use_container_width=True, type="primary", key=f"{mode}_btn_add"):
                if p_sel != "-- Select Product --":
                    prod_obj = prod_map[p_sel]
                    st.session_state[session_key].append({
                        "product_id": prod_obj['id'],
                        "part_number": prod_obj['part_number'],
                        "quantity": p_qty,
                        "discount_percentage": p_disc,
                        "unit_price_100": prod_obj['price_100']
                    })
                    trigger_toast(f"Added {prod_obj['part_number']} to list!", icon="🛒")
                    st.rerun()

    with tab_multi:
        st.caption("Paste multiple rows from Excel/CSV (Format per line: `PartNumber [TAB] Quantity [TAB] Discount%`).")
        paste_text = st.text_area(
            "Paste Tabular Product Rows",
            placeholder="0249-0116\t200\t5\n0981-0008\t500\t10",
            key=f"{mode}_paste_area",
            height=100
        )
        if st.button("📥 Import Pasted Rows", key=f"{mode}_btn_paste", type="secondary"):
            parsed_items, unrec = parse_pasted_products_text(paste_text, all_prods)
            if parsed_items:
                st.session_state[session_key].extend(parsed_items)
                trigger_toast(f"Imported {len(parsed_items)} items from clipboard paste!", icon="📋")
                if unrec > 0:
                    st.warning(f"Skipped {unrec} unrecognized part number rows.")
                st.rerun()
            else:
                st.error("No valid part numbers identified from pasted text.")

    # 3. Interactive Data Editor Grid & Real-time Stock Verification
    cart_items = st.session_state[session_key]
    if not cart_items:
        st.info(f"No line items added yet. Use the single dropdown or clipboard paste tab above to build a {mode}.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### ✏️ Interactive Line Items Table")
    
    # Audit Stock Availability with Safety Buffer
    safety_buf = st.session_state.get("safety_stock_buffer", Config.SAFETY_STOCK_BUFFER)
    stock_audit = InventoryService.verify_stock_availability(cart_items, safety_buffer=safety_buf)
    audit_map = {item['part_number']: item for item in stock_audit['items']}

    # Prepare DataFrame for st.data_editor
    grid_rows = []
    for idx, item in enumerate(cart_items):
        audit = audit_map.get(item['part_number'], {})
        is_bad = audit.get('is_insufficient', False)
        status_text = "❌ Shortfall" if is_bad else "✅ In Stock"
        
        grid_rows.append({
            "#": idx + 1,
            "Part Number": item['part_number'],
            "Quantity (PCS)": float(item['quantity']),
            "Discount %": float(item['discount_percentage']),
            "Rate / 100 Pcs (INR)": float(item['unit_price_100']),
            "Available Stock": float(audit.get('current_stock', 0.0)),
            "Effective (Stock-Buffer)": float(audit.get('effective_available', 0.0)),
            "Stock Status": status_text
        })

    df_grid = pd.DataFrame(grid_rows)
    
    edited_df = st.data_editor(
        df_grid,
        column_config={
            "#": st.column_config.NumberColumn(disabled=True),
            "Part Number": st.column_config.TextColumn(disabled=True),
            "Quantity (PCS)": st.column_config.NumberColumn(min_value=1.0, step=10.0),
            "Discount %": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.5),
            "Rate / 100 Pcs (INR)": st.column_config.NumberColumn(disabled=True),
            "Available Stock": st.column_config.NumberColumn(disabled=True),
            "Effective (Stock-Buffer)": st.column_config.NumberColumn(disabled=True),
            "Stock Status": st.column_config.TextColumn(disabled=True)
        },
        use_container_width=True,
        hide_index=True,
        key=f"{mode}_data_editor"
    )

    # Sync edits back to session state
    for idx, row in edited_df.iterrows():
        if idx < len(cart_items):
            cart_items[idx]['quantity'] = float(row['Quantity (PCS)'])
            cart_items[idx]['discount_percentage'] = float(row['Discount %'])

    # Stock Warning Banner
    if stock_audit['has_insufficient_stock']:
        insuff_items = [i['part_number'] for i in stock_audit['items'] if i['is_insufficient']]
        err_msg = f"⚠️ **Stock Shortfall Detected** for: `{', '.join(insuff_items)}` (after deducting {safety_buf} PCS safety buffer)."
        if mode == "invoice":
            st.error(f"{err_msg} Tax Invoices cannot be generated until stock is available.")
        else:
            st.warning(f"{err_msg} Quotations can still be created with stock warnings.")

    # 4. Calculation Summary
    cust_payload = {
        "id": selected_cust['id'] if selected_cust else None,
        "name": selected_cust['name'] if selected_cust else "Guest Customer",
        "discount_percentage": disc_val,
        "gst_number": gst_no,
        "payment_terms": "Net 30 Days"
    }
    
    calc_res = OrderService.calculate_order(cust_payload, cart_items)
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        draw_metric_card("Subtotal", f"Rs. {calc_res['subtotal']:,.2f}", "Taxable Value", "fa-solid fa-calculator", "blue")
    with col_s2:
        draw_metric_card(f"GST ({calc_res['gst_rate']}%)", f"Rs. {calc_res['gst_amount']:,.2f}", "Calculated Tax", "fa-solid fa-percent", "amber")
    with col_s3:
        draw_metric_card("Grand Total", f"Rs. {calc_res['grand_total']:,.2f}", "Final Payable", "fa-solid fa-money-bill-wave", "green")
    with col_s4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Billing List", use_container_width=True, key=f"{mode}_btn_clear"):
            st.session_state[session_key] = []
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 5. Document Action & PDF Generation
    if mode == "invoice":
        block_create = stock_audit['has_insufficient_stock']
        if st.button("📜 Generate & Save Tax Invoice (INV)", use_container_width=True, type="primary", disabled=block_create):
            o_id = OrderService.create_order(cust_payload, cart_items)
            inv_id = InvoiceService.generate_invoice_for_order(o_id)
            inv_data = InvoiceService.get_invoice_by_id(inv_id)
            inv_html = generate_invoice_html(inv_data)
            inv_pdf = generate_pdf_from_html(inv_html)
            
            st.success(f"Tax Invoice Created Successfully! Number: **{inv_data['invoice_number']}**")
            st.download_button(
                label=f"📥 Download Invoice PDF ({inv_data['invoice_number']})",
                data=inv_pdf,
                file_name=f"{inv_data['invoice_number']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        if st.button("📄 Generate & Save Commercial Quotation (QTN)", use_container_width=True, type="primary"):
            q_id = QuotationService.generate_quotation(cust_payload, cart_items)
            q_data = QuotationService.get_quotation_by_id(q_id)
            q_html = generate_quotation_html(q_data)
            q_pdf = generate_pdf_from_html(q_html)
            
            st.success(f"Quotation Created Successfully! Number: **{q_data['quotation_number']}**")
            st.download_button(
                label=f"📥 Download Quotation PDF ({q_data['quotation_number']})",
                data=q_pdf,
                file_name=f"{q_data['quotation_number']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

def render_tax_invoice_tab():
    render_billing_builder(mode="invoice")

def render_quotation_tab():
    render_billing_builder(mode="quotation")
