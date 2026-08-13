import pandas as pd
import streamlit as st
from app.services.customer_service import CustomerService
from app.ui.styles import render_html, trigger_toast

def render_customers_tab():
    render_html('<div class="section-head"><i class="fa-solid fa-users"></i> Customer Directory & Discounts</div>')
    st.caption("Manage customer profiles, default discount percentages, GST numbers, payment terms, and transport & insurance terms.")
    
    # Persisted in session_state (not a plain st.button return value) because
    # a plain button's True result only lasts for the single script run
    # immediately after the click. st.form_submit_button triggers its own
    # rerun on save, and on that rerun the plain button re-evaluates to
    # False - which previously closed this whole block (including the
    # form's submit handler) before CustomerService.create_customer ever
    # ran, so "Add New Customer" silently failed to save anything.
    if "show_add_customer_form" not in st.session_state:
        st.session_state.show_add_customer_form = False

    col_cu1, col_cu2 = st.columns([2, 1])
    with col_cu1:
        c_search = st.text_input("🔍 Search Customer Name or GSTIN", key="cust_dir_search")
    with col_cu2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add New Customer", width='stretch', type="primary"):
            st.session_state.show_add_customer_form = True

    if st.session_state.show_add_customer_form:
        with st.expander("📝 Create New Customer Profile", expanded=True):
            with st.form("form_add_cust"):
                new_name = st.text_input("Customer Name *")
                new_disc = st.number_input("Default Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
                new_gst = st.text_input("GSTIN Number")
                new_terms = st.text_input("Payment Terms", value="Net 30 Days")
                new_transport_insurance = st.text_area(
                    "Transport & Insurance Terms",
                    placeholder="e.g. Ex-Works, freight & transit insurance to be arranged and borne by the customer",
                    help="Printed/referenced wherever this customer's shipping and insurance responsibility needs to be stated."
                )
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    submitted = st.form_submit_button("💾 Save Customer", type="primary", width='stretch')
                with col_f2:
                    cancelled = st.form_submit_button("Cancel", width='stretch')

                if submitted:
                    try:
                        CustomerService.create_customer(
                            name=new_name,
                            discount_percentage=new_disc,
                            gst_number=new_gst,
                            payment_terms=new_terms,
                            transport_insurance_terms=new_transport_insurance
                        )
                        trigger_toast(f"Created customer '{new_name}'!", icon="👤")
                        st.session_state.show_add_customer_form = False
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))

                if cancelled:
                    st.session_state.show_add_customer_form = False
                    st.rerun()

    customers = CustomerService.get_customers(search_query=c_search)
    if not customers:
        st.info("No customers found in directory.")
        return

    df_cust = []
    for c in customers:
        df_cust.append({
            "ID": c['id'],
            "Customer Name": c['name'],
            "Discount %": f"{c['discount_percentage']:.1f}%",
            "GSTIN": c['gst_number'] or "N/A",
            "Payment Terms": c['payment_terms'] or "Net 30 Days",
            "Transport & Insurance Terms": c.get('transport_insurance_terms') or "N/A",
            "Updated At": c['updated_at'][:10]
        })

    st.dataframe(pd.DataFrame(df_cust), width='stretch', hide_index=True)
