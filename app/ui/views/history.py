import pandas as pd
import streamlit as st
from app.services.invoice_service import InvoiceService
from app.services.quotation_service import QuotationService
from app.ui.styles import render_html
from app.ui.pdf_preview import render_pdf_preview
from app.core.pdf_generator import generate_invoice_html, generate_quotation_html, generate_pdf_from_html

def render_history_tab():
    render_html('<div class="section-head"><i class="fa-solid fa-clock-rotate-left"></i> History Ledger (Invoices & Quotations)</div>')
    
    tab_inv, tab_qtn = st.tabs(["📜 Invoices History", "📄 Quotations History"])
    
    with tab_inv:
        st.caption("View and re-download generated Tax Invoices.")
        inv_search = st.text_input("🔍 Search Invoice Number or Customer", key="inv_hist_search")
        invoices = InvoiceService.get_invoices(search_query=inv_search)
        
        if not invoices:
            st.info("No invoices found matching your query.")
        else:
            df_inv = []
            for i in invoices:
                df_inv.append({
                    "Invoice Number": i['invoice_number'],
                    "Order Ref": i['order_number'],
                    "Customer": i['customer_name_snapshot'],
                    "Invoice Date": i['invoice_date'],
                    "Grand Total": f"Rs. {i['grand_total']:,.2f}",
                    "Created At": i['created_at'][:19]
                })
            st.dataframe(pd.DataFrame(df_inv), width='stretch', hide_index=True)
            
            # PDF Download selector & Preview
            inv_nums = [i['invoice_number'] for i in invoices]
            sel_inv_num = st.selectbox("Select Invoice to Preview & Download PDF", ["-- Select Invoice --"] + inv_nums, key="sel_inv_dl")
            if sel_inv_num != "-- Select Invoice --":
                inv_obj = next(i for i in invoices if i['invoice_number'] == sel_inv_num)
                inv_data = InvoiceService.get_invoice_by_id(inv_obj['id'])
                pdf_bytes = generate_pdf_from_html(generate_invoice_html(inv_data))
                
                col_id1, col_id2 = st.columns([1, 2])
                with col_id1:
                    st.download_button(
                        label=f"📥 Download {sel_inv_num}.pdf",
                        data=pdf_bytes,
                        file_name=f"{sel_inv_num}.pdf",
                        mime="application/pdf",
                        type="primary",
                        width='stretch'
                    )
                
                st.markdown("##### 📄 PDF Document Preview")
                render_pdf_preview(pdf_bytes, height=700)

    with tab_qtn:
        st.caption("View and re-download generated Commercial Quotations.")
        qtn_search = st.text_input("🔍 Search Quotation Number or Customer", key="qtn_hist_search")
        quotations = QuotationService.get_quotations(search_query=qtn_search)
        
        if not quotations:
            st.info("No quotations found matching your query.")
        else:
            df_qtn = []
            for q in quotations:
                df_qtn.append({
                    "Quotation Number": q['quotation_number'],
                    "Customer": q['customer_name_snapshot'],
                    "Grand Total": f"Rs. {q['grand_total']:,.2f}",
                    "Created At": q['created_at'][:19]
                })
            st.dataframe(pd.DataFrame(df_qtn), width='stretch', hide_index=True)
            
            # PDF Download selector & Preview
            qtn_nums = [q['quotation_number'] for q in quotations]
            sel_qtn_num = st.selectbox("Select Quotation to Preview & Download PDF", ["-- Select Quotation --"] + qtn_nums, key="sel_qtn_dl")
            if sel_qtn_num != "-- Select Quotation --":
                qtn_obj = next(q for q in quotations if q['quotation_number'] == sel_qtn_num)
                qtn_data = QuotationService.get_quotation_by_id(qtn_obj['id'])
                pdf_bytes = generate_pdf_from_html(generate_quotation_html(qtn_data))
                
                col_qd1, col_qd2 = st.columns([1, 2])
                with col_qd1:
                    st.download_button(
                        label=f"📥 Download {sel_qtn_num}.pdf",
                        data=pdf_bytes,
                        file_name=f"{sel_qtn_num}.pdf",
                        mime="application/pdf",
                        type="primary",
                        width='stretch'
                    )
                
                st.markdown("##### 📄 PDF Document Preview")
                render_pdf_preview(pdf_bytes, height=700)
