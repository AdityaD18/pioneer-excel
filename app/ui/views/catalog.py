import pandas as pd
import streamlit as st
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService
from app.ui.styles import render_html, trigger_toast

def render_catalog_tab():
    render_html('<div class="section-head"><i class="fa-solid fa-boxes-stacked"></i> Master Product Catalog (STATIC PRICE LIST)</div>')
    st.caption("Exact representation of STATIC PRICE LIST.xlsx as-is (Price in \" Per 100pcs).")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        search_kw = st.text_input("🔍 Search Item Code or Series", placeholder="e.g. 206-118 or 206", key="cat_search")
    with col_c2:
        series_list = ProductRepository.get_distinct_series()
        series_opts = ["All Series"] + [str(s) for s in series_list if s]
        sel_series = st.selectbox("🏷️ Filter by Series", series_opts, key="cat_series_filter")
    with col_c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Clear Filter / Refresh Grid", use_container_width=True):
            st.rerun()

    # Retrieve Catalog Rows matching STATIC PRICE LIST structure
    cat_items = ProductRepository.get_catalog(search_kw=search_kw, series=sel_series)
    if not cat_items:
        st.info("No catalog items found matching your search criteria.")
        return
        
    df_cat = pd.DataFrame(cat_items)
    price_col_name = 'Price in " Per 100pcs'
    
    # Display Data Editor
    st.caption("Double-click any price cell to update rates directly inline.")
    edited_df = st.data_editor(
        df_cat,
        key="cat_data_editor",
        disabled=["product_id", "Series", "Item Code"],
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("💾 Save Price Updates", type="primary", key="btn_save_catalog"):
        updated_cnt = 0
        for idx, row in edited_df.iterrows():
            orig = df_cat.iloc[idx]
            p_id = row['product_id']
            
            # Check price change
            new_p100 = float(row[price_col_name])
            orig_p100 = float(orig[price_col_name])
            if new_p100 != orig_p100:
                ProductService.update_product_cost_price(p_id, new_p100)
                updated_cnt += 1
                
            # Check packing qty change
            new_pack = int(row['Packing Quantity PCS'])
            orig_pack = int(orig['Packing Quantity PCS'])
            if new_pack != orig_pack:
                ProductRepository.update_packing_and_series(p_id, new_pack, str(row['Series']))
                updated_cnt += 1
                
        if updated_cnt > 0:
            trigger_toast(f"Successfully saved {updated_cnt} catalog updates!", icon="💾")
            st.rerun()
        else:
            st.info("No modifications detected.")
