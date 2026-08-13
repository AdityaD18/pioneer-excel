import streamlit as st

def inject_custom_css():
    """Injects the Pioneer Technology design system: a clean, professional
    steel-navy and copper palette built for a mechanical parts ERP, applied
    consistently across every native Streamlit widget and custom component."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');

    :root {
        /* Palette: steel-navy + copper, grounded in mechanical/industrial parts */
        --pt-navy-900: #0F1E33;
        --pt-navy-800: #16304F;
        --pt-navy-700: #1E3F66;
        --pt-navy-600: #2C5282;
        --pt-copper-600: #B5622D;
        --pt-copper-500: #C2703D;
        --pt-copper-100: #FBEEE4;
        --pt-success: #157347;
        --pt-success-bg: #E7F5EC;
        --pt-warning: #B45309;
        --pt-warning-bg: #FEF3E2;
        --pt-danger: #B91C1C;
        --pt-danger-bg: #FDEDED;
        --pt-info: #0369A1;
        --pt-info-bg: #E8F4FB;

        --pt-bg: #F4F6F9;
        --pt-surface: #FFFFFF;
        --pt-border: #E2E8F0;
        --pt-border-strong: #CBD5E1;

        --pt-text-primary: #101828;
        --pt-text-secondary: #5B6472;
        --pt-text-muted: #8D97A5;

        --pt-radius-sm: 8px;
        --pt-radius-md: 10px;
        --pt-radius-lg: 14px;
        --pt-shadow-sm: 0 1px 2px rgba(16, 24, 40, 0.05);
        --pt-shadow-md: 0 4px 10px -2px rgba(16, 24, 40, 0.08), 0 2px 4px -2px rgba(16, 24, 40, 0.04);
    }

    @media (prefers-reduced-motion: reduce) {
        * { transition: none !important; animation: none !important; }
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--pt-text-primary);
    }

    /* ---------- App shell ---------- */
    .stApp {
        background: var(--pt-bg);
    }

    div.block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Hide default Streamlit chrome for a clean, custom-branded surface */
    #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; height: 0; }

    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--pt-border-strong); border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

    /* ---------- Header banner ---------- */
    .header-banner {
        background: linear-gradient(120deg, var(--pt-navy-900) 0%, var(--pt-navy-700) 100%);
        padding: 24px 30px;
        border-radius: var(--pt-radius-lg);
        color: #F8FAFC;
        margin-bottom: 22px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: var(--pt-shadow-md);
        position: relative;
        border-left: 4px solid var(--pt-copper-500);
    }

    .header-title {
        font-size: 24px;
        font-weight: 700;
        margin: 0;
        color: #F8FAFC;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.2px;
    }

    .header-title i { color: var(--pt-copper-500); font-size: 20px; }

    .header-subtitle {
        font-size: 13.5px;
        color: #AEBAC9;
        margin-top: 5px;
        font-weight: 400;
    }

    /* ---------- Metric cards (custom) ---------- */
    .metric-card {
        background: var(--pt-surface);
        border: 1px solid var(--pt-border);
        border-radius: var(--pt-radius-md);
        padding: 18px 20px;
        box-shadow: var(--pt-shadow-sm);
        transition: box-shadow 0.15s ease, border-color 0.15s ease;
    }

    .metric-card:hover {
        box-shadow: var(--pt-shadow-md);
        border-color: var(--pt-border-strong);
    }

    .metric-title {
        font-size: 11.5px;
        font-weight: 700;
        color: var(--pt-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--pt-text-primary);
        margin: 8px 0 3px 0;
        letter-spacing: -0.3px;
        font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace;
    }

    .metric-sub {
        font-size: 12px;
        font-weight: 500;
        color: var(--pt-text-muted);
    }

    .metric-icon-blue { color: var(--pt-info); background: var(--pt-info-bg); padding: 9px; border-radius: var(--pt-radius-sm); font-size: 14px; }
    .metric-icon-green { color: var(--pt-success); background: var(--pt-success-bg); padding: 9px; border-radius: var(--pt-radius-sm); font-size: 14px; }
    .metric-icon-amber { color: var(--pt-warning); background: var(--pt-warning-bg); padding: 9px; border-radius: var(--pt-radius-sm); font-size: 14px; }
    .metric-icon-purple { color: var(--pt-navy-700); background: #E9EEF5; padding: 9px; border-radius: var(--pt-radius-sm); font-size: 14px; }
    .metric-icon-cyan { color: var(--pt-info); background: var(--pt-info-bg); padding: 9px; border-radius: var(--pt-radius-sm); font-size: 14px; }
    .metric-icon-red { color: var(--pt-danger); background: var(--pt-danger-bg); padding: 9px; border-radius: var(--pt-radius-sm); font-size: 14px; }

    /* Native st.metric widget, styled to match the custom cards */
    div[data-testid="stMetric"] {
        background: var(--pt-surface);
        border: 1px solid var(--pt-border);
        border-radius: var(--pt-radius-md);
        padding: 14px 18px;
        box-shadow: var(--pt-shadow-sm);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11.5px;
        font-weight: 700;
        color: var(--pt-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace;
        color: var(--pt-text-primary);
        font-weight: 700;
    }

    /* ---------- Section headers ---------- */
    .section-head {
        font-size: 19px;
        font-weight: 700;
        color: var(--pt-text-primary);
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.2px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--pt-border);
    }
    .section-head i { color: var(--pt-copper-600); font-size: 17px; }

    div[data-testid="stCaptionContainer"] { color: var(--pt-text-secondary); margin-bottom: 14px; }

    /* ---------- Setting / grouped panels ---------- */
    .setting-section {
        background: var(--pt-surface);
        border: 1px solid var(--pt-border);
        border-left: 3px solid var(--pt-navy-700);
        border-radius: var(--pt-radius-md);
        padding: 14px 18px;
        margin-bottom: 14px;
        box-shadow: var(--pt-shadow-sm);
    }

    .setting-section-title {
        font-size: 14.5px;
        font-weight: 700;
        color: var(--pt-text-primary);
        margin-bottom: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .setting-section-title i { color: var(--pt-navy-700); }

    /* ---------- Tabs ---------- */
    /* Verified against the installed Streamlit frontend bundle: tabs use
       data-testid="stTabs" / "stTab" with role="tablist" / role="tab",
       and react-aria-components marks the active tab with data-selected
       (aria-selected is also present, kept as a fallback). */
    div[data-testid="stTabs"] [role="tablist"] {
        gap: 4px;
        background: var(--pt-surface);
        padding: 6px;
        border-radius: var(--pt-radius-md);
        border: 1px solid var(--pt-border);
        box-shadow: var(--pt-shadow-sm);
        margin-bottom: 20px;
    }

    div[data-testid="stTab"] {
        height: 42px;
        border-radius: var(--pt-radius-sm);
        color: var(--pt-text-secondary);
        font-weight: 600;
        font-size: 13.5px;
        padding: 0 16px;
        transition: background 0.15s ease, color 0.15s ease;
    }

    div[data-testid="stTab"]:hover {
        background: var(--pt-bg);
        color: var(--pt-text-primary);
    }

    div[data-testid="stTab"][data-selected],
    div[data-testid="stTab"][aria-selected="true"] {
        background: var(--pt-navy-900) !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stTab"][data-selected] p,
    div[data-testid="stTab"][aria-selected="true"] p {
        color: #FFFFFF !important;
    }

    /* ---------- Buttons ---------- */
    div.stButton > button {
        border-radius: var(--pt-radius-sm);
        font-weight: 600;
        font-size: 13.5px;
        padding: 9px 18px;
        border: 1px solid var(--pt-border-strong);
        color: var(--pt-text-primary);
        background: var(--pt-surface);
        transition: all 0.15s ease;
    }

    div.stButton > button:hover {
        border-color: var(--pt-navy-600);
        color: var(--pt-navy-700);
        background: #F8FAFC;
    }

    div.stButton > button[kind="primary"] {
        background: var(--pt-navy-800);
        border: 1px solid var(--pt-navy-800);
        color: #FFFFFF;
        box-shadow: var(--pt-shadow-sm);
    }

    div.stButton > button[kind="primary"]:hover {
        background: var(--pt-navy-900);
        border-color: var(--pt-navy-900);
        box-shadow: var(--pt-shadow-md);
    }

    div.stDownloadButton > button {
        border-radius: var(--pt-radius-sm);
        font-weight: 600;
        background: var(--pt-copper-500);
        border: 1px solid var(--pt-copper-600);
        color: #FFFFFF;
    }
    div.stDownloadButton > button:hover {
        background: var(--pt-copper-600);
    }

    /* ---------- Inputs ---------- */
    /* Backgrounds/text colors are forced explicitly (not just inherited
       from the theme) so the app renders identically regardless of the
       visitor's browser/OS dark-mode preference. */
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stTextArea textarea, div[data-baseweb="select"] > div {
        background-color: var(--pt-surface) !important;
        color: var(--pt-text-primary) !important;
        border-radius: var(--pt-radius-sm) !important;
        border: 1px solid var(--pt-border-strong) !important;
        font-size: 13.5px;
    }

    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--pt-navy-600) !important;
        box-shadow: 0 0 0 3px rgba(44, 82, 130, 0.12) !important;
    }

    /* The dropdown option list renders in a separate floating popover,
       not inside the select element itself - style it explicitly too. */
    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="menu"] {
        background-color: var(--pt-surface) !important;
        border: 1px solid var(--pt-border) !important;
        border-radius: var(--pt-radius-sm) !important;
        box-shadow: var(--pt-shadow-md) !important;
    }
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] li {
        background-color: var(--pt-surface) !important;
        color: var(--pt-text-primary) !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] li:hover {
        background-color: var(--pt-bg) !important;
    }

    div[data-testid="stWidgetLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: var(--pt-text-secondary) !important;
        opacity: 1 !important;
    }

    /* ---------- Expanders ---------- */
    /* stExpander is a fully custom React component (no native
       <details>/<summary>), so style the label text directly. */
    div[data-testid="stExpander"] {
        border: 1px solid var(--pt-border);
        border-radius: var(--pt-radius-md);
        box-shadow: var(--pt-shadow-sm);
        background: var(--pt-surface);
        overflow: hidden;
    }
    div[data-testid="stExpander"] p {
        font-weight: 600;
        font-size: 13.5px;
        color: var(--pt-text-primary);
    }

    /* ---------- Table & Data Editor ---------- */
    /* st.dataframe and st.data_editor both render through the same
       DataFrame component and share the stDataFrame testid. */
    div[data-testid="stDataFrame"] {
        border-radius: var(--pt-radius-md);
        overflow: hidden;
        border: 1px solid var(--pt-border);
        box-shadow: var(--pt-shadow-sm);
    }

    /* ---------- Alerts ---------- */
    div[data-testid="stAlertContentInfo"] { color: var(--pt-info); }
    div[data-testid="stAlertContentSuccess"] { color: var(--pt-success); }
    div[data-testid="stAlertContentError"] { color: var(--pt-danger); }
    div[data-testid="stAlertContentWarning"] { color: var(--pt-warning); }

    /* ---------- Badge pills ---------- */
    .custom-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 11px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background: var(--pt-bg);
        color: var(--pt-text-secondary);
        border: 1px solid var(--pt-border);
    }

    .custom-badge-active {
        background: var(--pt-success-bg);
        color: var(--pt-success);
        border-color: #BEE3C9;
    }

    /* ---------- Dividers ---------- */
    hr { border-color: var(--pt-border); }
    </style>
    """, unsafe_allow_html=True)

def render_html(html_code):
    st.markdown(html_code, unsafe_allow_html=True)

def draw_metric_card(title, value, subtext, icon_class, color_theme="blue"):
    html = f"""
    <div class="metric-card">
        <div class="metric-title">
            <span>{title}</span>
            <i class="{icon_class} metric-icon-{color_theme}"></i>
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def trigger_toast(msg, icon="✅"):
    st.toast(msg, icon=icon)

