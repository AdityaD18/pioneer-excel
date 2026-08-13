import tempfile
import uuid
from pathlib import Path
import streamlit as st


def render_pdf_preview(pdf_bytes, height=700):
    """
    Renders an inline PDF preview via Streamlit's own media file storage,
    which is the actual root-cause fix for browsers/ad-blockers (Brave
    etc.) blocking the preview.

    Two earlier approaches were tried and both failed for the same
    underlying reason - they each ultimately produced a data: or blob:
    URI, which several browsers/content-blockers refuse to render because
    that pattern is commonly abused for malvertising:
      1. `<iframe src="data:application/pdf;base64,...">` directly.
      2. A hand-built blob: URL constructed client-side via JavaScript.

    Passing a pathlib.Path pointing at a real PDF file to st.iframe takes
    a completely different code path: Streamlit uploads the file to its
    own MediaFileManager and serves it from a genuine first-party URL
    under the app's own origin, rendered by the browser's native PDF
    viewer - not a data:/blob: URI at all, so there is nothing for a
    content blocker to flag.
    """
    tmp_path = Path(tempfile.gettempdir()) / f"pdf_preview_{uuid.uuid4().hex}.pdf"
    tmp_path.write_bytes(pdf_bytes)
    st.iframe(tmp_path, height=height)
