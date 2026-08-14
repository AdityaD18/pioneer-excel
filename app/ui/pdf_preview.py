import pymupdf
import streamlit as st


def render_pdf_preview(pdf_bytes, height=700):
    """
    Renders an inline PDF preview by converting each page to a PNG image
    server-side and displaying it with st.image.

    This is deliberately the simplest possible approach, chosen after two
    other techniques each failed for different environment-specific
    reasons that were hard to fully reproduce/diagnose from this sandbox:
      1. `<iframe src="data:application/pdf;base64,...">` - blocked by
         Brave and other browsers/content-blockers, since that pattern is
         commonly abused for malvertising.
      2. `st.iframe(pathlib.Path(...))` pointing at a real local PDF file,
         which uses Streamlit's own MediaFileManager (a genuine first-party
         URL, not a data:/blob: URI) - structurally correct and verified
         working in this sandbox, but reported as an endless loading
         spinner in the actual deployed environment, for a reason that
         could not be reproduced or diagnosed without direct access to
         that environment's network/proxy setup.

    Rendering to plain images sidesteps browser PDF-viewer embedding
    entirely - no iframe, no MIME-type handling, no viewer plugin, nothing
    for a content blocker or a proxy to interfere with. st.image is one of
    the most basic, heavily-used Streamlit primitives, so it's the most
    likely to just work everywhere. The trade-off: no native
    zoom/text-select/print-from-viewer inside the preview - the download
    button remains the way to get an interactive PDF.
    """
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    try:
        zoom = 150 / 72  # render at ~150 DPI for crisp but not huge images
        matrix = pymupdf.Matrix(zoom, zoom)
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=matrix)
            st.image(pix.tobytes("png"), width='stretch')
            if len(doc) > 1 and page_num < len(doc) - 1:
                st.caption(f"Page {page_num + 1} of {len(doc)}")
    finally:
        doc.close()
