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

def parse_pasted_products_text(raw_text, all_prods, default_discount=0.0):
    """
    Parses multi-line pasted product data from Excel/CSV/tables.
    Supports 2-column or 3-column lines: PartNumber [TAB] Quantity [TAB Optional] Discount%
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
        if not line_clean or line_clean.lower().startswith('part') or line_clean.lower().startswith('item') or line_clean.lower().startswith('sr'):
            continue
            
        tokens = [t.strip() for t in re.split(r'[\t,;\s]+', line_clean) if t.strip()]
        if not tokens:
            continue
            
        part_code = tokens[0].lower()
        matched_prod = prod_lookup.get(part_code)
        
        if not matched_prod:
            for k, p_obj in prod_lookup.items():
                if part_code in k or k in part_code:
                    matched_prod = p_obj
                    break
                    
        if matched_prod:
            qty = 100.0
            disc = default_discount
            if len(tokens) >= 2:
                try:
                    qty = float(tokens[1].replace(',', '').replace('%', ''))
                except ValueError:
                    qty = 100.0
            if len(tokens) >= 3:
                try:
                    disc = float(tokens[2].replace(',', '').replace('%', ''))
                except ValueError:
                    disc = default_discount
                    
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

@st.dialog("📜 Confirm Tax Invoice Generation", width="large")
def show_invoice_confirmation_modal(cust_payload, cart_items, calc_res, stock_audit):
    st.markdown(f"## Customer: **{cust_payload['name']}**")
    if cust_payload.get('gst_number'):
        st.caption(f"🏢 GSTIN: `{cust_payload['gst_number']}` | Payment Terms: `{cust_payload['payment_terms']}`")
        
    st.markdown("### 📋 Verification Summary & Product Status Table")
    
    audit_map = {item['part_number']: item for item in stock_audit['items']}
    df_preview = []
    
    for idx, item in enumerate(calc_res['items']):
        audit = audit_map.get(item['part_number'], {})
        shortfall = audit.get('shortfall', 0.0)
        is_bad = audit.get('is_insufficient', False)
        
        status = f"⚠️ Shortfall ({shortfall:,.0f} Pcs)" if is_bad else "✅ In Stock"
        
        df_preview.append({
            "#": idx + 1,
            "Part Number": item['part_number'],
            "Requested Qty": f"{item['quantity']:,.0f} PCS",
            "Available Stock": f"{audit.get('current_stock', 0.0):,.0f} PCS",
            "Stock Status": status,
            "Rate / Pc (INR)": f"Rs. {item['unit_price']:,.2f}",
            "Discount %": f"{item['discount_percentage']:.1f}%",
            "Line Total (INR)": f"Rs. {item['line_total']:,.2f}"
        })
        
    st.dataframe(pd.DataFrame(df_preview), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Taxable Value", f"Rs. {calc_res['subtotal']:,.2f}")
    with col_m2:
        st.metric(f"GST Amount ({calc_res['gst_rate']}%)", f"Rs. {calc_res['gst_amount']:,.2f}")
    with col_m3:
        st.metric("Grand Total Payable", f"Rs. {calc_res['grand_total']:,.2f}")

    if stock_audit['has_insufficient_stock']:
        st.warning("⚠️ **Notice**: One or more products have stock shortfalls. Tax Invoice creation will proceed as requested.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Confirm & Generate Tax Invoice PDF", type="primary", use_container_width=True):
        o_id = OrderService.create_order(cust_payload, cart_items)
        inv_id = InvoiceService.generate_invoice_for_order(o_id)
        inv_data = InvoiceService.get_invoice_by_id(inv_id)
        inv_html = generate_invoice_html(inv_data)
        inv_pdf = generate_pdf_from_html(inv_html)
        
        st.session_state.created_inv_pdf = inv_pdf
        st.session_state.created_inv_number = inv_data['invoice_number']
        trigger_toast(f"Created Invoice {inv_data['invoice_number']}!", icon="📜")
        st.rerun()

@st.dialog("📄 Confirm Commercial Quotation Generation", width="large")
def show_quotation_confirmation_modal(cust_payload, cart_items, calc_res, stock_audit):
    st.markdown(f"## Customer: **{cust_payload['name']}**")
    if cust_payload.get('gst_number'):
        st.caption(f"🏢 GSTIN: `{cust_payload['gst_number']}` | Payment Terms: `{cust_payload['payment_terms']}`")
        
    st.markdown("### 📋 Verification Summary & Product Status Table")
    
    audit_map = {item['part_number']: item for item in stock_audit['items']}
    df_preview = []
    
    for idx, item in enumerate(calc_res['items']):
        audit = audit_map.get(item['part_number'], {})
        shortfall = audit.get('shortfall', 0.0)
        is_bad = audit.get('is_insufficient', False)
        
        status = f"⚠️ Shortfall ({shortfall:,.0f} Pcs)" if is_bad else "✅ In Stock"
        
        df_preview.append({
            "#": idx + 1,
            "Part Number": item['part_number'],
            "Requested Qty": f"{item['quantity']:,.0f} PCS",
            "Available Stock": f"{audit.get('current_stock', 0.0):,.0f} PCS",
            "Stock Status": status,
            "Rate / Pc (INR)": f"Rs. {item['unit_price']:,.2f}",
            "Discount %": f"{item['discount_percentage']:.1f}%",
            "Line Total (INR)": f"Rs. {item['line_total']:,.2f}"
        })
        
    st.dataframe(pd.DataFrame(df_preview), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Taxable Value", f"Rs. {calc_res['subtotal']:,.2f}")
    with col_m2:
        st.metric(f"GST Amount ({calc_res['gst_rate']}%)", f"Rs. {calc_res['gst_amount']:,.2f}")
    with col_m3:
        st.metric("Grand Total Payable", f"Rs. {calc_res['grand_total']:,.2f}")

    if stock_audit['has_insufficient_stock']:
        st.info("ℹ️ **Notice**: Quotation creation will proceed with current stock indicators.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Confirm & Generate Commercial Quotation PDF", type="primary", use_container_width=True):
        q_id = QuotationService.generate_quotation(cust_payload, cart_items)
        q_data = QuotationService.get_quotation_by_id(q_id)
        q_html = generate_quotation_html(q_data)
        q_pdf = generate_pdf_from_html(q_html)
        
        st.session_state.created_qtn_pdf = q_pdf
        st.session_state.created_qtn_number = q_data['quotation_number']
        trigger_toast(f"Created Quotation {q_data['quotation_number']}!", icon="📄")
        st.rerun()

def render_billing_builder(mode="invoice"):
    """
    Unified Document Builder Component for Tax Invoices and Commercial Quotations.
    mode: 'invoice' | 'quotation'
    """
    provider = get_data_provider()
    all_prods = ProductService.get_all_billing_products()
    prod_map = {f"{p['part_number']} - {p['part_name'] or ''}": p for p in all_prods}
    prod_names = ["-- Select Product --"] + list(prod_map.keys())
    
    session_key = f"{mode}_cart_items"
    if session_key not in st.session_state:
        st.session_state[session_key] = []
        
    icon_cls = "fa-solid fa-file-invoice-dollar" if mode == "invoice" else "fa-solid fa-file-lines"
    title_text = "Tax Invoice Builder" if mode == "invoice" else "Commercial Quotation Builder"
    sub_text = "Create GST Tax Invoices with real-time stock verification & instant PDF generation." if mode == "invoice" else "Create Commercial Price Quotations with validity terms & PDF export."
    
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

    # Display Download Button if document was just created
    pdf_key = f"created_{mode}_pdf"
    num_key = f"created_{mode}_number"
    if pdf_key in st.session_state and num_key in st.session_state:
        doc_num = st.session_state[num_key]
        st.success(f"🎉 **{'Invoice' if mode == 'invoice' else 'Quotation'} {doc_num} Generated Successfully!**")
        st.download_button(
            label=f"📥 Download PDF ({doc_num})",
            data=st.session_state[pdf_key],
            file_name=f"{doc_num}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
            key=f"dl_btn_{mode}_{doc_num}"
        )
        st.markdown("<br>", unsafe_allow_html=True)

    # 1. Customer Selection Header
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
    
    # 2. Product Input Section (Left Side: 2-Column Table Grid [Part Number, Quantity] | Right Side: Single-Entry Dropdown)
    render_html('<div class="setting-section"><div class="setting-section-title"><i class="fa-solid fa-cart-flatbed"></i> Product Input Panel</div></div>')
    
    c_left, c_right = st.columns([3, 2])
    
    # --- LEFT SIDE: 2-COLUMN MULTI-ENTRY TABLE GRID (PART NUMBER & QUANTITY ONLY) ---
    with c_left:
        st.markdown("##### 📋 Multi-Entry Table [Part Number & Quantity Only] (Left)")
        st.caption("Enter/paste ONLY Part Number and Quantity. Rates, discounts, and totals are imported & calculated automatically!")
        
        # 2-Column Empty Table Grid
        blank_rows = [{"Part Number": "", "Quantity (PCS)": 100.0} for _ in range(5)]
        grid_key = f"{mode}_paste_grid_2col"
        
        edited_paste_grid = st.data_editor(
            pd.DataFrame(blank_rows),
            column_config={
                "Part Number": st.column_config.TextColumn(help="Type or paste Part Numbers directly into cells"),
                "Quantity (PCS)": st.column_config.NumberColumn(min_value=1.0, step=10.0)
            },
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key=grid_key
        )
        
        if st.button("📋 Add Table Grid Entries to Order", key=f"{mode}_btn_add_grid", use_container_width=True, type="secondary"):
            grid_added = 0
            prod_lookup = {p['part_number'].strip().lower(): p for p in all_prods}
            
            for idx, row in edited_paste_grid.iterrows():
                p_code = str(row.get("Part Number", "")).strip().lower()
                if not p_code:
                    continue
                matched = prod_lookup.get(p_code)
                if not matched:
                    for k, p_obj in prod_lookup.items():
                        if p_code in k or k in p_code:
                            matched = p_obj
                            break
                if matched:
                    q_val = float(row.get("Quantity (PCS)", 100.0) or 100.0)
                    st.session_state[session_key].append({
                        "product_id": matched['id'],
                        "part_number": matched['part_number'],
                        "quantity": q_val,
                        "discount_percentage": disc_val,
                        "unit_price_100": matched['price_100']
                    })
                    grid_added += 1
                    
            if grid_added > 0:
                trigger_toast(f"Added {grid_added} items! Rates & discounts imported automatically.", icon="📋")
                st.rerun()
            else:
                st.warning("No matching part numbers found in filled table rows.")

        with st.expander("📝 Fast Multi-Line Text Area Paste"):
            paste_text = st.text_area(
                "Paste Tabular Text (Format per line: PartNumber [TAB] Quantity)",
                placeholder="206-118\t200\n206-804\t500",
                key=f"{mode}_paste_area",
                height=80
            )
            if st.button("📥 Import Pasted Text Rows", key=f"{mode}_btn_paste_text", use_container_width=True):
                parsed_items, unrec = parse_pasted_products_text(paste_text, all_prods, default_discount=disc_val)
                if parsed_items:
                    st.session_state[session_key].extend(parsed_items)
                    trigger_toast(f"Imported {len(parsed_items)} items from text paste!", icon="📋")
                    if unrec > 0:
                        st.warning(f"Skipped {unrec} unrecognized rows.")
                    st.rerun()
                else:
                    st.error("No valid part numbers identified from pasted text.")

    # --- RIGHT SIDE: SINGLE-ENTRY DROPDOWN (PART NUMBER & QUANTITY ONLY) ---
    with c_right:
        st.markdown("##### ➕ Single-Entry Dropdown (Right)")
        st.caption("Select a single product from catalog dropdown list.")
        
        p_sel = st.selectbox("Select Product", prod_names, key=f"{mode}_add_prod")
        p_qty = st.number_input("Qty (PCS)", min_value=1.0, value=100.0, step=10.0, key=f"{mode}_add_qty")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add Single Item", use_container_width=True, type="primary", key=f"{mode}_btn_add"):
            if p_sel != "-- Select Product --":
                prod_obj = prod_map[p_sel]
                st.session_state[session_key].append({
                    "product_id": prod_obj['id'],
                    "part_number": prod_obj['part_number'],
                    "quantity": p_qty,
                    "discount_percentage": disc_val,
                    "unit_price_100": prod_obj['price_100']
                })
                trigger_toast(f"Added {prod_obj['part_number']} to order list!", icon="🛒")
                st.rerun()

    # 3. Order Line Items Data Editor Grid & Real-time Stock Audit
    cart_items = st.session_state[session_key]
    if not cart_items:
        st.info("No line items added yet. Enter Part Number & Quantity on the left or select a product on the right to build an order.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🛒 Current Order Line Items Table")
    
    # Audit Stock Availability with Safety Buffer
    safety_buf = st.session_state.get("safety_stock_buffer", Config.SAFETY_STOCK_BUFFER)
    stock_audit = InventoryService.verify_stock_availability(cart_items, safety_buffer=safety_buf)
    audit_map = {item['part_number']: item for item in stock_audit['items']}

    # Prepare DataFrame for st.data_editor
    grid_rows = []
    for idx, item in enumerate(cart_items):
        audit = audit_map.get(item['part_number'], {})
        shortfall = audit.get('shortfall', 0.0)
        is_bad = audit.get('is_insufficient', False)
        status_text = f"⚠️ Shortfall ({shortfall:,.0f} Pcs)" if is_bad else "✅ In Stock"
        
        grid_rows.append({
            "#": idx + 1,
            "Part Number": item['part_number'],
            "Quantity (PCS)": float(item['quantity']),
            "Discount %": float(item['discount_percentage']),
            "Rate / 100 Pcs (INR)": float(item['unit_price_100']),
            "Available Stock": float(audit.get('current_stock', 0.0)),
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
            "Stock Status": st.column_config.TextColumn(disabled=True)
        },
        use_container_width=True,
        hide_index=True,
        key=f"{mode}_order_data_editor"
    )

    # Sync edits back to session state
    for idx, row in edited_df.iterrows():
        if idx < len(cart_items):
            cart_items[idx]['quantity'] = float(row['Quantity (PCS)'])
            cart_items[idx]['discount_percentage'] = float(row['Discount %'])

    # Stock Shortfall Warning Banner (non-blocking)
    if stock_audit['has_insufficient_stock']:
        insuff_items = [f"{i['part_number']} (Short: {i['shortfall']:,.0f} Pcs)" for i in stock_audit['items'] if i['is_insufficient']]
        st.warning(f"⚠️ **Stock Shortfall Warning**: `{', '.join(insuff_items)}`. Creation is permitted as requested.")

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
    
    # 5. Open Large Confirmation Modal Dialog Button
    if mode == "invoice":
        if st.button("📜 Proceed to Review & Generate Tax Invoice (INV)", use_container_width=True, type="primary"):
            show_invoice_confirmation_modal(cust_payload, cart_items, calc_res, stock_audit)
    else:
        if st.button("📄 Proceed to Review & Generate Commercial Quotation (QTN)", use_container_width=True, type="primary"):
            show_quotation_confirmation_modal(cust_payload, cart_items, calc_res, stock_audit)

def render_tax_invoice_tab():
    render_billing_builder(mode="invoice")

def render_quotation_tab():
    render_billing_builder(mode="quotation")
