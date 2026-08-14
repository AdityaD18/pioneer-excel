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
        if st.button("🔄 Clear Filter / Refresh Grid", width='stretch'):
            st.rerun()

    # Retrieve Catalog Rows matching STATIC PRICE LIST structure
    cat_items = ProductRepository.get_catalog(search_kw=search_kw, series=sel_series)
    if not cat_items:
        st.info("No catalog items found matching your search criteria.")
        return
        
    df_cat = pd.DataFrame(cat_items)
    df_cat["Packing Quantity PCS"] = df_cat["Packing Quantity PCS"].astype(str)
    df_cat["Description"] = df_cat["Description"].fillna("")
    price_col_name = 'Price in " Per 100pcs'
    per_piece_col_name = 'Price per Piece'
    
    # Display Data Editor
    st.caption("Double-click any price or description cell to update inline. \"Price per Piece\" is auto-calculated from \"Price in \\\" Per 100pcs\" and cannot be edited directly.")
    edited_df = st.data_editor(
        df_cat,
        column_config={
            "product_id": None,
            "Series": st.column_config.TextColumn(disabled=True),
            "Item Code": st.column_config.TextColumn(disabled=True),
            "Description": st.column_config.TextColumn(),
            "Packing Quantity PCS": st.column_config.TextColumn(),
            price_col_name: st.column_config.NumberColumn(
                label='Price in " Per 100pcs (₹)',
                format="₹ %,.2f"
            ),
            per_piece_col_name: st.column_config.NumberColumn(
                label='Price per Piece (₹)',
                format="₹ %,.2f",
                disabled=True
            )
        },
        key="cat_data_editor",
        width='stretch',
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

            # Check description change
            new_desc = str(row['Description'] or '').strip()
            orig_desc = str(orig['Description'] or '').strip()
            if new_desc != orig_desc:
                ProductRepository.update_description(p_id, new_desc)
                updated_cnt += 1
                
        if updated_cnt > 0:
            trigger_toast(f"Successfully saved {updated_cnt} catalog updates!", icon="💾")
            st.rerun()
        else:
            st.info("No modifications detected.")
