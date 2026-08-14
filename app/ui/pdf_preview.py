import streamlit as st
from app.core.logger import app_logger


def render_pdf_preview(pdf_bytes, height=700):
    """
    Renders an inline PDF preview by converting each page to a PNG image
    server-side and displaying it with st.image.

    Third attempt at this feature - two earlier techniques each failed
    for different environment-specific reasons:
      1. `<iframe src="data:application/pdf;base64,...">` - blocked by
         Brave and other browsers/content-blockers.
      2. `st.iframe(pathlib.Path(...))` via Streamlit's own MediaFileManager
         - structurally correct, but hung with an endless loading spinner
         in the actual deployed environment.
      3. PyMuPDF page-to-image rendering - this is the right general
         approach (no iframe/viewer plugin to fail), but PyMuPDF itself
         crashed the ENTIRE app on Streamlit Cloud, not just the preview:
         it was imported at module level, so app startup itself failed
         with the import, and PyMuPDF has a documented history of exactly
         this kind of Streamlit Cloud deployment failure (it needs a
         system-level libgl1 library that Cloud's minimal container
         doesn't have by default). It's also AGPL-3.0 licensed, which is
         a real concern for a company's commercial billing software
         regardless of the crash.

    This version:
      - Uses pypdfium2 instead of PyMuPDF: it has no mandatory system
        dependencies at all (confirmed via its own documentation and
        multiple Streamlit Cloud deployment reports), and is
        Apache-2.0/BSD-3 licensed rather than AGPL.
      - Imports pypdfium2 INSIDE this function, not at module level, so
        even in the worst case where it somehow fails to import in a
        given environment, that failure is caught and only disables this
        one feature - it can never again take down the whole app at
        startup the way the PyMuPDF attempt did.
      - Wraps the actual rendering in a broad try/except for the same
        reason: any failure here degrades to a clear message and the
        existing download button, never a crash or an infinite spinner.
    """
    try:
        import pypdfium2 as pdfium
    except Exception as e:
        app_logger.warning(f"PDF preview unavailable - pypdfium2 import failed: {e}")
        st.info("📄 Inline preview isn't available right now. Please use the Download button to view the PDF.")
        return

    try:
        pdf = pdfium.PdfDocument(pdf_bytes)
        try:
            page_count = len(pdf)
            for page_num in range(page_count):
                page = pdf[page_num]
                bitmap = page.render(scale=150 / 72)  # ~150 DPI
                pil_image = bitmap.to_pil()
                st.image(pil_image, width='stretch')
                if page_count > 1 and page_num < page_count - 1:
                    st.caption(f"Page {page_num + 1} of {page_count}")
        finally:
            pdf.close()
    except Exception as e:
        app_logger.warning(f"PDF preview rendering failed: {e}", exc_info=True)
        st.info("📄 Inline preview isn't available for this document. Please use the Download button to view the PDF.")
