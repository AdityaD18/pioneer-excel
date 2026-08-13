import base64
import streamlit as st


def render_pdf_preview(pdf_bytes, height=700):
    """
    Renders an inline PDF preview without ever putting a data: URI directly
    in an <iframe src="...">. Brave (and increasingly other browsers/ad
    blockers) blocks that pattern outright - it resembles a common
    malvertising delivery mechanism - which is why the old approach showed
    'This page has been blocked by Brave' instead of the PDF.

    Instead, the base64 PDF bytes are decoded into a Blob and turned into a
    blob: URL entirely client-side, inside a properly sandboxed iframe (via
    st.iframe, which executes embedded <script> tags - st.markdown's HTML
    injection does not). Blob URLs are not treated as a network navigation
    the way data: URIs are, so this is not blocked by content blockers.
    """
    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    html = f"""
    <div style="width: 100%; height: {height}px;">
        <iframe id="pdf-frame" width="100%" height="{height}"
                style="border: 1px solid #3D4757; border-radius: 8px;"></iframe>
    </div>
    <script>
        const base64 = "{b64_pdf}";
        const byteChars = atob(base64);
        const byteNumbers = new Array(byteChars.length);
        for (let i = 0; i < byteChars.length; i++) {{
            byteNumbers[i] = byteChars.charCodeAt(i);
        }}
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], {{ type: 'application/pdf' }});
        const blobUrl = URL.createObjectURL(blob);
        document.getElementById('pdf-frame').src = blobUrl;
    </script>
    """
    st.iframe(html, height=height + 20)
