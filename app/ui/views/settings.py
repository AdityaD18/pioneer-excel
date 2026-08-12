import os
import streamlit as st
import pandas as pd
from app.providers import get_data_provider
from app.services.order_service import OrderService
from app.core.config import Config
from app.ui.styles import render_html, trigger_toast

def render_settings_tab():
    render_html('<div class="section-head"><i class="fa-solid fa-sliders"></i> System Settings & Data Importers</div>')
    st.caption("Manage Excel Price Lists, Google Sheets live stock integration, safety stock buffers, and default system settings.")
    
    provider = get_data_provider()
    
    # 1. Google Sheets Live Integration & Safety Stock Settings
    render_html('<div class="setting-section"><div class="setting-section-title"><i class="fa-solid fa-cloud-arrow-down"></i> Live Google Sheets & Safety Stock Buffer</div></div>')
    
    if "google_sheets_url" not in st.session_state:
        st.session_state.google_sheets_url = Config.GOOGLE_SHEETS_STOCK_URL
    if "safety_stock_buffer" not in st.session_state:
        st.session_state.safety_stock_buffer = Config.SAFETY_STOCK_BUFFER
        
    c_gs1, c_gs2 = st.columns([3, 1])
    with c_gs1:
        gs_url_input = st.text_input(
            "🌐 Google Sheets Live Stock URL",
            value=st.session_state.google_sheets_url,
            placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit",
            help="Public or shared Google Sheets link for real-time stock list synchronization.",
            key="set_gs_url"
        )
    with c_gs2:
        safety_buf_input = st.number_input(
            "🛡️ Safety Stock Buffer (PCS)",
            min_value=0.0,
            value=float(st.session_state.safety_stock_buffer),
            step=5.0,
            help="Fixed safety stock margin required before confirming item availability.",
            key="set_safety_buffer"
        )
        
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("💾 Save Settings", use_container_width=True):
            st.session_state.google_sheets_url = gs_url_input
            st.session_state.safety_stock_buffer = safety_buf_input
            Config.GOOGLE_SHEETS_STOCK_URL = gs_url_input
            Config.SAFETY_STOCK_BUFFER = safety_buf_input
            trigger_toast("Saved Google Sheets & Safety Buffer configuration!", icon="⚙️")
            st.rerun()
    with c_btn2:
        if st.button("⚡ Sync Live Stock From Google Sheets Now", use_container_width=True, type="primary"):
            target_url = gs_url_input or st.session_state.google_sheets_url
            if not target_url:
                st.error("Please enter a valid Google Sheets URL first.")
            else:
                with st.spinner("Downloading live stock data from Google Sheets..."):
                    res = provider.sync_from_web_url(target_url, imported_by="Manual Google Sync")
                    if res['status'] in ('success', 'partial_success'):
                        st.session_state.google_sheets_url = target_url
                        trigger_toast(f"Successfully synced {res['successful_records']:,} stock items live!", icon="⚡")
                        st.rerun()
                    else:
                        st.error(f"Google Sheets sync failed: {', '.join(res['errors'])}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Tax & Operational Configuration
    render_html('<div class="setting-section"><div class="setting-section-title"><i class="fa-solid fa-gear"></i> Operational & Tax Defaults</div></div>')
    
    gst_val = OrderService.get_gst_rate()
    
    c_set1, c_set2 = st.columns([2, 1])
    with c_set1:
        new_gst_val = st.number_input("Default GST Rate (%)", min_value=0.0, max_value=50.0, value=gst_val, step=0.5, key="set_gst_rate")
    with c_set2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Update GST Rate", use_container_width=True):
            OrderService.update_gst_rate(new_gst_val)
            trigger_toast(f"GST Rate updated to {new_gst_val}%!", icon="⚙️")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Static Price List Excel Import
    render_html('<div class="setting-section"><div class="setting-section-title"><i class="fa-solid fa-file-excel"></i> Static Price List Import (Excel)</div></div>')
    
    st.caption("Upload static 'PRICE LIST.xlsx' to update product cost price rates and packing quantities.")
    up_cost = st.file_uploader("Choose Price List Excel File", type=["xlsx", "xls"], key="file_up_cost")
    if up_cost and st.button("🚀 Process Price List Import", type="primary", key="btn_imp_cost"):
        with st.spinner("Parsing cost list price sheet..."):
            res = provider.import_costs(up_cost, filename=up_cost.name, imported_by="Streamlit Admin")
            if res['status'] in ('success', 'partial_success'):
                trigger_toast(f"Imported {res['successful_records']:,} cost rates!", icon="✅")
                st.rerun()
            else:
                st.error(f"Import failed: {', '.join(res['errors'])}")

    st.markdown("<br>", unsafe_allow_html=True)
    render_html('<div class="setting-section"><div class="setting-section-title"><i class="fa-solid fa-arrows-rotate"></i> Reseed & Update Catalog</div></div>')
    st.caption("Re-import all cost price rates and inventory stock levels cleanly from 'group order status.xlsx'.")
    if st.button("🔄 Force Reseed & Update Catalog from Excel", key="btn_reseed_db", type="secondary", use_container_width=True):
        with st.spinner("Clearing stale rows and re-importing fresh costs and stock..."):
            from app.models.database import reseed_database_from_excel
            ok = reseed_database_from_excel()
            if ok:
                trigger_toast("Successfully re-seeded database with clean cost prices & stock!", icon="🔄")
                st.rerun()
            else:
                st.error("Failed to locate 'group order status.xlsx' or re-seed catalog.")
