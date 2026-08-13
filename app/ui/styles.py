import streamlit as st

def inject_custom_css():
    """Injects the Pioneer Technology dark design system: a classical,
    library-and-brass dark theme (deep charcoal surfaces, warm ivory
    text, brass/copper accents, a serif display face for headers) built
    for a mechanical parts ERP, applied consistently across every native
    Streamlit widget and custom component."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');

    :root {
        /* Palette: a dark, classical library-and-brass study - deep
           charcoal surfaces, warm ivory text, brass/copper accents. */
        --pt-bg: #12161C;
        --pt-surface: #1A1F27;
        --pt-surface-raised: #222834;
        --pt-border: #2B323F;
        --pt-border-strong: #3D4757;

        --pt-brass-500: #C48A3F;
        --pt-brass-400: #D9A25C;
        --pt-brass-600: #A87231;
        --pt-brass-bg: #2C2417;

        --pt-navy-deep: #0B0F16;
        --pt-navy-800: #141B26;

        --pt-success: #4ADE80;
        --pt-success-bg: #16281E;
        --pt-warning: #F5B860;
        --pt-warning-bg: #2E2415;
        --pt-danger: #F0796F;
        --pt-danger-bg: #2E1917;
        --pt-info: #67C3EE;
        --pt-info-bg: #142430;

        --pt-text-primary: #EDEAE3;
        --pt-text-secondary: #A6ACB8;
        --pt-text-muted: #6E7684;

        --pt-radius-sm: 8px;
        --pt-radius-md: 10px;
        --pt-radius-lg: 14px;
        --pt-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.35);
        --pt-shadow-md: 0 8px 20px -4px rgba(0, 0, 0, 0.45), 0 2px 6px -2px rgba(0, 0, 0, 0.3);
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
    ::-webkit-scrollbar-thumb:hover { background: #4C586C; }

    /* ---------- Header banner ---------- */
    .header-banner {
        background: linear-gradient(120deg, var(--pt-navy-deep) 0%, var(--pt-navy-800) 100%);
        padding: 26px 30px;
        border-radius: var(--pt-radius-lg);
        color: var(--pt-text-primary);
        margin-bottom: 22px;
        border: 1px solid var(--pt-border);
        box-shadow: var(--pt-shadow-md);
        position: relative;
        border-left: 4px solid var(--pt-brass-500);
    }

    .header-title {
        font-family: 'Fraunces', 'Plus Jakarta Sans', serif;
        font-size: 27px;
        font-weight: 600;
        margin: 0;
        color: #F7F4EE;
        display: flex;
        align-items: center;
        gap: 13px;
        letter-spacing: -0.2px;
    }

    .header-title i { color: var(--pt-brass-500); font-size: 20px; }

    .header-subtitle {
        font-size: 13.5px;
        color: var(--pt-text-secondary);
        margin-top: 6px;
        font-weight: 400;
        letter-spacing: 0.2px;
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
        font-size: 25px;
        font-weight: 700;
        color: var(--pt-text-primary);
        margin: 9px 0 3px 0;
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
    .metric-icon-purple { color: var(--pt-brass-400); background: var(--pt-brass-bg); padding: 9px; border-radius: var(--pt-radius-sm); font-size: 14px; }
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
        font-family: 'Fraunces', 'Plus Jakarta Sans', serif;
        font-size: 21px;
        font-weight: 600;
        color: var(--pt-text-primary);
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.1px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--pt-border);
    }
    .section-head i { color: var(--pt-brass-500); font-size: 18px; }

    div[data-testid="stCaptionContainer"] { color: var(--pt-text-secondary); margin-bottom: 14px; }

    /* ---------- Setting / grouped panels ---------- */
    .setting-section {
        background: var(--pt-surface);
        border: 1px solid var(--pt-border);
        border-left: 3px solid var(--pt-brass-500);
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
    .setting-section-title i { color: var(--pt-brass-400); }

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
        background: var(--pt-surface-raised);
        color: var(--pt-text-primary);
    }

    div[data-testid="stTab"][data-selected],
    div[data-testid="stTab"][aria-selected="true"] {
        background: var(--pt-brass-500) !important;
        color: var(--pt-navy-deep) !important;
    }

    div[data-testid="stTab"][data-selected] p,
    div[data-testid="stTab"][aria-selected="true"] p {
        color: var(--pt-navy-deep) !important;
        font-weight: 700;
    }

    /* ---------- Buttons ---------- */
    div.stButton > button {
        border-radius: var(--pt-radius-sm);
        font-weight: 600;
        font-size: 13.5px;
        padding: 9px 18px;
        border: 1px solid var(--pt-border-strong);
        color: var(--pt-text-primary);
        background: var(--pt-surface-raised);
        transition: all 0.15s ease;
    }

    div.stButton > button:hover {
        border-color: var(--pt-brass-500);
        color: var(--pt-brass-400);
        background: var(--pt-surface);
    }

    div.stButton > button[kind="primary"] {
        background: var(--pt-brass-500);
        border: 1px solid var(--pt-brass-500);
        color: var(--pt-navy-deep);
        font-weight: 700;
        box-shadow: var(--pt-shadow-sm);
    }

    div.stButton > button[kind="primary"]:hover {
        background: var(--pt-brass-400);
        border-color: var(--pt-brass-400);
        box-shadow: var(--pt-shadow-md);
    }

    div.stDownloadButton > button {
        border-radius: var(--pt-radius-sm);
        font-weight: 700;
        background: var(--pt-brass-500);
        border: 1px solid var(--pt-brass-500);
        color: var(--pt-navy-deep);
    }
    div.stDownloadButton > button:hover {
        background: var(--pt-brass-400);
        border-color: var(--pt-brass-400);
    }

    /* ---------- Inputs ---------- */
    /* Backgrounds/text colors are forced explicitly (not just inherited
       from the theme) so the app renders identically regardless of the
       visitor's browser/OS dark-mode preference. */
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stTextArea textarea, div[data-baseweb="select"] > div {
        background-color: var(--pt-surface-raised) !important;
        color: var(--pt-text-primary) !important;
        border-radius: var(--pt-radius-sm) !important;
        border: 1px solid var(--pt-border-strong) !important;
        font-size: 13.5px;
    }

    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--pt-brass-500) !important;
        box-shadow: 0 0 0 3px rgba(196, 138, 63, 0.18) !important;
    }

    /* The dropdown option list renders in a separate floating popover,
       not inside the select element itself - style it explicitly too. */
    div[data-baseweb="popover"] ul[role="listbox"],
    div[data-baseweb="menu"] {
        background-color: var(--pt-surface-raised) !important;
        border: 1px solid var(--pt-border-strong) !important;
        border-radius: var(--pt-radius-sm) !important;
        box-shadow: var(--pt-shadow-md) !important;
    }
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] li {
        background-color: var(--pt-surface-raised) !important;
        color: var(--pt-text-primary) !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] li:hover {
        background-color: var(--pt-brass-bg) !important;
        color: var(--pt-brass-400) !important;
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
       DataFrame component and share the stDataFrame testid. The grid
       cells themselves are canvas-rendered (glide-data-grid) and read
       the Streamlit theme tokens directly - only .streamlit/config.toml
       controls their color, this CSS only frames the container. */
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
        background: var(--pt-surface-raised);
        color: var(--pt-text-secondary);
        border: 1px solid var(--pt-border);
    }

    .custom-badge-active {
        background: var(--pt-success-bg);
        color: var(--pt-success);
        border-color: #245A38;
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

