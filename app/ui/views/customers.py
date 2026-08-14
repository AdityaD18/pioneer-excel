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
    # ran, so "Add New Customer" silently failed to save anything. Same
    # pattern applied to the Edit form below.
    if "show_add_customer_form" not in st.session_state:
        st.session_state.show_add_customer_form = False
    if "show_edit_customer_form" not in st.session_state:
        st.session_state.show_edit_customer_form = False

    col_cu1, col_cu2, col_cu3 = st.columns([2, 1, 1])
    with col_cu1:
        c_search = st.text_input("🔍 Search Customer Name or GSTIN", key="cust_dir_search")
    with col_cu2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Add New Customer", width='stretch', type="primary"):
            st.session_state.show_add_customer_form = True
            st.session_state.show_edit_customer_form = False
    with col_cu3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ Edit Customer", width='stretch'):
            st.session_state.show_edit_customer_form = True
            st.session_state.show_add_customer_form = False

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

    if st.session_state.show_edit_customer_form:
        with st.expander("✏️ Edit Existing Customer", expanded=True):
            all_customers = CustomerService.get_customers()
            if not all_customers:
                st.info("No customers exist yet to edit.")
            else:
                cust_options = {f"{c['name']} (ID {c['id']})": c['id'] for c in all_customers}
                # Selectbox lives OUTSIDE the form so picking a different
                # customer immediately reruns and refreshes the form's
                # pre-filled defaults below - inside a form it wouldn't
                # update until submit, showing stale values for a
                # selection the user hasn't saved yet.
                selected_label = st.selectbox("Select Customer to Edit", list(cust_options.keys()), key="edit_cust_select")
                selected_id = cust_options[selected_label]
                selected_cust = next(c for c in all_customers if c['id'] == selected_id)

                with st.form(f"form_edit_cust_{selected_id}"):
                    edit_name = st.text_input("Customer Name *", value=selected_cust['name'])
                    edit_disc = st.number_input("Default Discount (%)", min_value=0.0, max_value=100.0, value=float(selected_cust['discount_percentage']), step=0.5)
                    edit_gst = st.text_input("GSTIN Number", value=selected_cust['gst_number'] or "")
                    edit_terms = st.text_input("Payment Terms", value=selected_cust['payment_terms'] or "Net 30 Days")
                    edit_transport_insurance = st.text_area(
                        "Transport & Insurance Terms",
                        value=selected_cust.get('transport_insurance_terms') or "",
                        placeholder="e.g. Ex-Works, freight & transit insurance to be arranged and borne by the customer",
                        help="Printed/referenced wherever this customer's shipping and insurance responsibility needs to be stated."
                    )

                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        saved = st.form_submit_button("💾 Save Changes", type="primary", width='stretch')
                    with col_e2:
                        edit_cancelled = st.form_submit_button("Cancel", width='stretch')

                    if saved:
                        try:
                            CustomerService.update_customer(
                                selected_id,
                                name=edit_name,
                                discount_percentage=edit_disc,
                                gst_number=edit_gst,
                                payment_terms=edit_terms,
                                transport_insurance_terms=edit_transport_insurance
                            )
                            trigger_toast(f"Updated customer '{edit_name}'!", icon="✏️")
                            st.session_state.show_edit_customer_form = False
                            st.rerun()
                        except Exception as ex:
                            st.error(str(ex))

                    if edit_cancelled:
                        st.session_state.show_edit_customer_form = False
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
