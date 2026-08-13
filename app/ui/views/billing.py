import re
import streamlit as st
import pandas as pd
from app.providers import get_data_provider
from app.services.customer_service import CustomerService
from app.services.order_service import OrderService
from app.services.invoice_service import InvoiceService
from app.services.quotation_service import QuotationService
from app.services.product_service import ProductService
from app.core.config import Config
from app.ui.styles import render_html, draw_metric_card, trigger_toast
from app.ui.pdf_preview import render_pdf_preview
from app.core.pdf_generator import generate_invoice_html, generate_quotation_html, generate_pdf_from_html
from app.services.import_service import ImportService

def find_matching_product(p_code_raw, all_prods):
    """Robust matching for part numbers using exact, clean, normalized, and substring lookups."""
    if not p_code_raw or not str(p_code_raw).strip():
        return None
    raw_str = str(p_code_raw).strip()
    clean_str = raw_str.lower()
    norm_str = ImportService.normalize_part_number(raw_str)
    
    # 1. Exact match on clean/raw part_number
    for p in all_prods:
        p_num = str(p['part_number']).strip().lower()
        if p_num == clean_str or p_num == raw_str.lower():
            return p
            
    # 2. Normalized part_number match
    for p in all_prods:
        p_norm = ImportService.normalize_part_number(p['part_number'])
        if p_norm == norm_str:
            return p
            
    # 3. Substring match fallback
    for p in all_prods:
        p_num = str(p['part_number']).strip().lower()
        if clean_str in p_num or p_num in clean_str:
            return p
            
    return None

def parse_pasted_products_text(raw_text, all_prods, default_discount=0.0):
    """
    Parses multi-line pasted product data from Excel/CSV/tables.
    Supports 2-column or 3-column lines: PartNumber [TAB] Quantity [TAB Optional] Discount%
    """
    if not raw_text or not raw_text.strip():
        return [], 0
        
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
            
        part_code = tokens[0]
        matched_prod = find_matching_product(part_code, all_prods)
                    
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

@st.dialog("📜 Review & Confirm Tax Invoice Generation", width="large")
def show_invoice_confirmation_modal(cust_payload, cart_items, calc_res, stock_audit, hide_pricing_details=False):
    st.markdown(f"## Customer: **{cust_payload['name']}**")
    if cust_payload.get('gst_number'):
        st.caption(f"🏢 GSTIN: `{cust_payload['gst_number']}` | Payment Terms: `{cust_payload['payment_terms']}`")
        
    st.markdown("### 📋 Dynamic Stock Status & Order Review Table")
    st.caption("Stock availability is cross-checked live against dynamic `STOCK STATUS.xlsx`.")
    
    audit_map = {item['part_number']: item for item in stock_audit.get('items', [])}
    df_preview = []
    
    for idx, item in enumerate(calc_res['items']):
        audit = audit_map.get(item['part_number'], {})
        shortfall = audit.get('shortfall', 0.0)
        is_bad = audit.get('is_insufficient', False)
        status_str = f"⚠️ Shortfall ({shortfall:,.0f} Pcs)" if is_bad else "✅ In Stock"
        
        df_preview.append({
            "#": idx + 1,
            "Part Number": item['part_number'],
            "Requested Qty": f"{item['quantity']:,.0f} PCS",
            "Available Stock": f"{audit.get('current_stock', 0.0):,.0f} PCS",
            "Stock Status": status_str,
            "Rate / 100 Pcs (INR)": f"Rs. {item['unit_price_100']:,.2f}",
            "Discount %": f"{item['discount_percentage']:.1f}%",
            "Line Total (INR)": f"Rs. {item['line_total']:,.2f}"
        })
        
    st.dataframe(pd.DataFrame(df_preview), width='stretch', hide_index=True)
    
    st.markdown("---")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Taxable Value", f"Rs. {calc_res['subtotal']:,.2f}")
    with col_m2:
        st.metric(f"GST Amount ({calc_res['gst_rate']}%)", f"Rs. {calc_res['gst_amount']:,.2f}")
    with col_m3:
        st.metric("Grand Total Payable", f"Rs. {calc_res['grand_total']:,.2f}")

    if stock_audit.get('has_insufficient_stock'):
        st.warning("⚠️ **Notice**: One or more products have stock shortfalls. Tax Invoice creation will proceed as requested.")

    if hide_pricing_details:
        st.info("🙈 **Simplified pricing mode is ON** for this document: the PDF will hide the list rate and discount % per line, showing only the discounted price, quantity, total, and delivery terms.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Confirm & Generate Tax Invoice PDF", type="primary", width='stretch'):
        o_id = OrderService.create_order(cust_payload, cart_items)
        inv_id = InvoiceService.generate_invoice_for_order(o_id, hide_pricing_details=hide_pricing_details)
        inv_data = InvoiceService.get_invoice_by_id(inv_id)
        inv_html = generate_invoice_html(inv_data)
        inv_pdf = generate_pdf_from_html(inv_html)
        
        st.session_state.created_invoice_pdf = inv_pdf
        st.session_state.created_invoice_number = inv_data['invoice_number']
        trigger_toast(f"Created Invoice {inv_data['invoice_number']}!", icon="📜")
        st.rerun()

@st.dialog("📄 Review & Confirm Commercial Quotation Generation", width="large")
def show_quotation_confirmation_modal(cust_payload, cart_items, calc_res, stock_audit, hide_pricing_details=False):
    st.markdown(f"## Customer: **{cust_payload['name']}**")
    if cust_payload.get('gst_number'):
        st.caption(f"🏢 GSTIN: `{cust_payload['gst_number']}` | Payment Terms: `{cust_payload['payment_terms']}`")
        
    st.markdown("### 📋 Dynamic Stock Status & Order Review Table")
    st.caption("Stock availability is cross-checked live against dynamic `STOCK STATUS.xlsx`.")
    
    audit_map = {item['part_number']: item for item in stock_audit.get('items', [])}
    df_preview = []
    
    for idx, item in enumerate(calc_res['items']):
        audit = audit_map.get(item['part_number'], {})
        shortfall = audit.get('shortfall', 0.0)
        is_bad = audit.get('is_insufficient', False)
        status_str = f"⚠️ Shortfall ({shortfall:,.0f} Pcs)" if is_bad else "✅ In Stock"
        
        df_preview.append({
            "#": idx + 1,
            "Part Number": item['part_number'],
            "Requested Qty": f"{item['quantity']:,.0f} PCS",
            "Available Stock": f"{audit.get('current_stock', 0.0):,.0f} PCS",
            "Stock Status": status_str,
            "Rate / 100 Pcs (INR)": f"Rs. {item['unit_price_100']:,.2f}",
            "Discount %": f"{item['discount_percentage']:.1f}%",
            "Line Total (INR)": f"Rs. {item['line_total']:,.2f}"
        })
        
    st.dataframe(pd.DataFrame(df_preview), width='stretch', hide_index=True)
    
    st.markdown("---")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Taxable Value", f"Rs. {calc_res['subtotal']:,.2f}")
    with col_m2:
        st.metric(f"GST Amount ({calc_res['gst_rate']}%)", f"Rs. {calc_res['gst_amount']:,.2f}")
    with col_m3:
        st.metric("Grand Total Payable", f"Rs. {calc_res['grand_total']:,.2f}")

    if stock_audit.get('has_insufficient_stock'):
        st.info("ℹ️ **Notice**: Commercial Quotation creation will proceed with current stock status indicators.")

    if hide_pricing_details:
        st.info("🙈 **Simplified pricing mode is ON** for this document: the PDF will hide the list rate and discount % per line, showing only the discounted price, quantity, total, and delivery terms.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Confirm & Generate Commercial Quotation PDF", type="primary", width='stretch'):
        q_id = QuotationService.generate_quotation(cust_payload, cart_items, hide_pricing_details=hide_pricing_details)
        q_data = QuotationService.get_quotation_by_id(q_id)
        q_html = generate_quotation_html(q_data)
        q_pdf = generate_pdf_from_html(q_html)
        
        st.session_state.created_quotation_pdf = q_pdf
        st.session_state.created_quotation_number = q_data['quotation_number']
        trigger_toast(f"Created Quotation {q_data['quotation_number']}!", icon="📄")
        st.rerun()

def render_billing_builder(mode="invoice"):
    """
    Unified Document Builder Component for Tax Invoices and Commercial Quotations.
    mode: 'invoice' | 'quotation'
    """
    all_prods = ProductService.get_all_billing_products()
    prod_map = {f"{p['part_number']} - {p['part_name'] or ''}": p for p in all_prods}
    prod_names = ["-- Select Product --"] + list(prod_map.keys())
    
    session_key = f"{mode}_cart_items"
    if session_key not in st.session_state:
        st.session_state[session_key] = []
        
    icon_cls = "fa-solid fa-file-invoice-dollar" if mode == "invoice" else "fa-solid fa-file-lines"
    title_text = "Tax Invoice Builder" if mode == "invoice" else "Commercial Quotation Builder"
    sub_text = "Create GST Tax Invoices with real-time stock status verification & instant PDF generation." if mode == "invoice" else "Create Commercial Price Quotations with dynamic stock review & PDF export."
    
    render_html(f'<div class="section-head"><i class="{icon_cls}"></i> {title_text}</div>')
    st.caption(sub_text)

    # Top Toolbar: Dynamic Stock Status Uploader Expander
    with st.expander("⚡ Upload / Refresh Dynamic Stock Status (.xlsx)"):
        st.caption("Upload updated dynamic `STOCK STATUS.xlsx` to instantly update inventory levels across the system.")
        up_stock = st.file_uploader("Choose STOCK STATUS.xlsx", type=["xlsx", "xls"], key=f"up_stock_{mode}")
        if up_stock is not None:
            if st.button("📥 Import Stock Status File", key=f"btn_import_stock_{mode}"):
                with st.spinner("Importing dynamic stock status..."):
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                        tmp.write(up_stock.getvalue())
                        tmp_path = tmp.name
                    res = ImportService.import_inventory(tmp_path, imported_by=f"UI Uploader ({mode})")
                    if res['status'] in ('success', 'partial_success'):
                        trigger_toast(f"Successfully updated {res['successful_records']:,} stock records!", icon="⚡")
                        st.rerun()
                    else:
                        st.error(f"Stock import failed: {', '.join(res['errors'])}")

    # Display Download Button & PDF Preview Below if document was just created
    pdf_key = f"created_{mode}_pdf"
    num_key = f"created_{mode}_number"
    if pdf_key in st.session_state and num_key in st.session_state:
        doc_num = st.session_state[num_key]
        pdf_bytes = st.session_state[pdf_key]
        
        st.success(f"🎉 **{'Invoice' if mode == 'invoice' else 'Quotation'} {doc_num} Generated Successfully!**")
        st.download_button(
            label=f"📥 Download PDF ({doc_num})",
            data=pdf_bytes,
            file_name=f"{doc_num}.pdf",
            mime="application/pdf",
            type="primary",
            width='stretch',
            key=f"dl_btn_{mode}_{doc_num}"
        )
        
        # Embedded PDF Preview
        st.markdown("##### 📄 PDF Document Preview")
        render_pdf_preview(pdf_bytes, height=750)
        st.markdown("<br>", unsafe_allow_html=True)

    # 1. Customer Selection Header
    def on_customer_change():
        sel_val = st.session_state.get(f"{mode}_cust_select")
        if sel_val and sel_val != "-- Select Customer --":
            try:
                c_id = int(sel_val.split("ID: ")[1].replace(")", ""))
                c_obj = CustomerService.get_customer_by_id(c_id)
                if c_obj:
                    st.session_state[f"{mode}_cust_discount"] = float(c_obj.get('discount_percentage', 0.0) or 0.0)
                    st.session_state[f"{mode}_gstin"] = str(c_obj.get('gst_number', '') or '')
                    st.session_state[f"{mode}_terms"] = str(c_obj.get('payment_terms', 'Net 30 Days') or 'Net 30 Days')
            except Exception:
                pass

    col_b1, col_b2, col_b3 = st.columns(3)
    customers = CustomerService.get_customers()
    cust_opts = ["-- Select Customer --"] + [f"{c['name']} (ID: {c['id']})" for c in customers]
    
    with col_b1:
        sel_cust_str = st.selectbox(
            "👤 Select Customer", 
            cust_opts, 
            key=f"{mode}_cust_select",
            on_change=on_customer_change
        )
        
    selected_cust = None
    if sel_cust_str != "-- Select Customer --":
        try:
            c_id = int(sel_cust_str.split("ID: ")[1].replace(")", ""))
            selected_cust = CustomerService.get_customer_by_id(c_id)
        except Exception:
            pass

    # Ensure session keys exist for immediate reactive autofill
    if f"{mode}_cust_discount" not in st.session_state:
        st.session_state[f"{mode}_cust_discount"] = float(selected_cust['discount_percentage']) if selected_cust else 0.0
    if f"{mode}_gstin" not in st.session_state:
        st.session_state[f"{mode}_gstin"] = selected_cust['gst_number'] if selected_cust and selected_cust['gst_number'] else ""
    if f"{mode}_terms" not in st.session_state:
        st.session_state[f"{mode}_terms"] = selected_cust['payment_terms'] if selected_cust and selected_cust['payment_terms'] else "Net 30 Days"

    with col_b2:
        disc_val = st.number_input(
            "🏷️ Customer Discount (%)", 
            min_value=0.0, max_value=100.0, 
            step=0.5,
            key=f"{mode}_cust_discount"
        )
    with col_b3:
        gst_no = st.text_input(
            "🏢 GSTIN Number", 
            key=f"{mode}_gstin"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Product Input Section (Left Side: 2-Column Table Grid | Right Side: Single-Entry Dropdown)
    render_html('<div class="setting-section"><div class="setting-section-title"><i class="fa-solid fa-cart-flatbed"></i> Product Input Panel</div></div>')
    
    c_left, c_right = st.columns([3, 2])
    
    # --- LEFT SIDE: 2-COLUMN MULTI-ENTRY TABLE GRID (PART NUMBER & QUANTITY ONLY) ---
    with c_left:
        st.markdown("##### 📋 Multi-Entry Table [Part Number & Quantity Only] (Left)")
        st.caption("Enter/paste ONLY Part Number and Quantity. Costs are pulled from `STATIC PRICE LIST.xlsx` automatically!")
        
        # 2-Column Empty Table Grid with Versioned Key for Instant Reset
        ver_key = f"{mode}_grid_version"
        if ver_key not in st.session_state:
            st.session_state[ver_key] = 0
            
        grid_key = f"{mode}_paste_grid_2col_v{st.session_state[ver_key]}"
        blank_rows = [{"Part Number": "", "Quantity (PCS)": 100.0} for _ in range(5)]
        
        edited_paste_grid = st.data_editor(
            pd.DataFrame(blank_rows),
            column_config={
                "Part Number": st.column_config.TextColumn(help="Type or paste Part Numbers directly into cells"),
                "Quantity (PCS)": st.column_config.NumberColumn(min_value=1.0, step=10.0)
            },
            num_rows="dynamic",
            width='stretch',
            hide_index=True,
            key=grid_key
        )
        
        col_gbtn1, col_gbtn2 = st.columns(2)
        with col_gbtn1:
            if st.button("📋 Add Grid Entries to Order", key=f"{mode}_btn_add_grid", width='stretch', type="secondary"):
                grid_added = 0
                
                for idx, row in edited_paste_grid.iterrows():
                    p_code = str(row.get("Part Number", "")).strip()
                    if not p_code:
                        continue
                    matched = find_matching_product(p_code, all_prods)
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
                    trigger_toast(f"Added {grid_added} items! Static rates imported automatically.", icon="📋")
                    st.rerun()
                else:
                    st.warning("No matching part numbers found in filled table rows.")
        with col_gbtn2:
            if st.button("🗑️ Clear Input Grid", key=f"{mode}_btn_clear_grid", width='stretch'):
                st.session_state[ver_key] += 1
                trigger_toast("Cleared input grid table!", icon="🗑️")
                st.rerun()

        with st.expander("📝 Fast Multi-Line Text Area Paste"):
            paste_text = st.text_area(
                "Paste Tabular Text (Format per line: PartNumber [TAB] Quantity)",
                placeholder="206-118\t200\n206-804\t500",
                key=f"{mode}_paste_area",
                height=80
            )
            if st.button("📥 Import Pasted Text Rows", key=f"{mode}_btn_paste_text", width='stretch'):
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
        if st.button("➕ Add Single Item", width='stretch', type="primary", key=f"{mode}_btn_add"):
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

    # 3. Order Line Items Data Editor Grid & Real-time Stock Verification
    cart_items = st.session_state[session_key]
    if not cart_items:
        st.info("No line items added yet. Enter Part Number & Quantity on the left or select a product on the right to build an order.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    col_oh1, col_oh2 = st.columns([3, 1])
    with col_oh1:
        st.markdown("#### 🛒 Current Order Line Items Table")
    with col_oh2:
        if st.button("🗑️ Clear All Order Items", key=f"{mode}_btn_clear_order", width='stretch'):
            st.session_state[session_key] = []
            trigger_toast("Cleared all order items!", icon="🗑️")
            st.rerun()

    # Verify Stock Availability against dynamic STOCK STATUS
    from app.services.inventory_service import InventoryService
    stock_audit = InventoryService.verify_stock_availability(cart_items)
    audit_map = {item['part_number']: item for item in stock_audit.get('items', [])}

    # Prepare DataFrame for st.data_editor with Stock Review Status
    grid_rows = []
    for idx, item in enumerate(cart_items):
        audit = audit_map.get(item['part_number'], {})
        shortfall = audit.get('shortfall', 0.0)
        is_bad = audit.get('is_insufficient', False)
        status_str = f"⚠️ Shortfall ({shortfall:,.0f} Pcs)" if is_bad else "✅ In Stock"

        grid_rows.append({
            "#": idx + 1,
            "Part Number": item['part_number'],
            "Quantity (PCS)": float(item['quantity']),
            "Available Stock": float(audit.get('current_stock', 0.0)),
            "Stock Status": status_str,
            "Discount %": float(item['discount_percentage']),
            "Rate / 100 Pcs (INR)": float(item['unit_price_100'])
        })

    df_grid = pd.DataFrame(grid_rows)
    
    edited_df = st.data_editor(
        df_grid,
        column_config={
            "#": st.column_config.NumberColumn(disabled=True),
            "Part Number": st.column_config.TextColumn(disabled=True),
            "Quantity (PCS)": st.column_config.NumberColumn(min_value=1.0, step=10.0),
            "Available Stock": st.column_config.NumberColumn(disabled=True),
            "Stock Status": st.column_config.TextColumn(disabled=True),
            "Discount %": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, step=0.5),
            "Rate / 100 Pcs (INR)": st.column_config.NumberColumn(disabled=True)
        },
        width='stretch',
        hide_index=True,
        key=f"{mode}_order_data_editor"
    )

    # Sync edits back to session state
    for idx, row in edited_df.iterrows():
        if idx < len(cart_items):
            cart_items[idx]['quantity'] = float(row['Quantity (PCS)'])
            cart_items[idx]['discount_percentage'] = float(row['Discount %'])

    # Non-blocking Stock Shortfall Notice
    if stock_audit.get('has_insufficient_stock'):
        insuff_items = [f"{i['part_number']} (Short: {i['shortfall']:,.0f} Pcs)" for i in stock_audit['items'] if i['is_insufficient']]
        st.warning(f"⚠️ **Dynamic Stock Shortfall Notice**: `{', '.join(insuff_items)}`. Creation will proceed as requested.")

    # 4. Calculation Summary
    cust_payload = {
        "id": selected_cust['id'] if selected_cust else None,
        "name": selected_cust['name'] if selected_cust else "Guest Customer",
        "discount_percentage": disc_val,
        "gst_number": gst_no,
        "payment_terms": st.session_state.get(f"{mode}_terms", "Net 30 Days")
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
        if st.button("🗑️ Clear Billing List", width='stretch', key=f"{mode}_btn_clear"):
            st.session_state[session_key] = []
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        hide_pricing_details = st.checkbox(
            "🙈 Hide List Price & Discount % on PDF — show only Discounted Price, Quantity & Delivery Terms",
            key=f"{mode}_hide_pricing_details",
            help="When enabled, the generated PDF omits the Rate (per pc) and Discount % columns entirely. Only the final discounted price, quantity, line total, and delivery terms are shown to the customer."
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 5. Open Large Confirmation Modal Dialog Button with Stock Audit Review
    if mode == "invoice":
        if st.button("📜 Proceed to Review & Generate Tax Invoice (INV)", width='stretch', type="primary"):
            show_invoice_confirmation_modal(cust_payload, cart_items, calc_res, stock_audit, hide_pricing_details=hide_pricing_details)
    else:
        if st.button("📄 Proceed to Review & Generate Commercial Quotation (QTN)", width='stretch', type="primary"):
            show_quotation_confirmation_modal(cust_payload, cart_items, calc_res, stock_audit, hide_pricing_details=hide_pricing_details)

def render_tax_invoice_tab():
    render_billing_builder(mode="invoice")

def render_quotation_tab():
    render_billing_builder(mode="quotation")
