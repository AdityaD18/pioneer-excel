import streamlit as st

def inject_custom_css():
    """Injects ultra-premium, modern CSS styling with dark glassmorphic themes, glowing gradients, and fluid micro-animations."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Header Gradient Banner */
    .header-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%);
        padding: 26px 30px;
        border-radius: 16px;
        color: #F8FAFC;
        margin-bottom: 24px;
        border: 1px solid rgba(99, 102, 241, 0.25);
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.4), 0 0 20px rgba(99, 102, 241, 0.15);
        position: relative;
        overflow: hidden;
    }

    .header-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.1) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .header-title {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 14px;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: #94A3B8;
        margin-top: 6px;
        font-weight: 400;
    }
    
    /* Futuristic Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::top-bar {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px -8px rgba(99, 102, 241, 0.15), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: #C7D2FE;
    }
    
    .metric-title {
        font-size: 12px;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
        margin: 10px 0 4px 0;
        letter-spacing: -0.5px;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .metric-sub {
        font-size: 12px;
        font-weight: 500;
        color: #94A3B8;
    }
    
    /* Styled Metric Icons */
    .metric-icon-blue { color: #0284C7; background: #E0F2FE; padding: 10px; border-radius: 10px; font-size: 16px; }
    .metric-icon-green { color: #16A34A; background: #DCFCE7; padding: 10px; border-radius: 10px; font-size: 16px; }
    .metric-icon-amber { color: #D97706; background: #FEF3C7; padding: 10px; border-radius: 10px; font-size: 16px; }
    .metric-icon-purple { color: #9333EA; background: #F3E8FF; padding: 10px; border-radius: 10px; font-size: 16px; }
    .metric-icon-cyan { color: #0891B2; background: #CFFAFE; padding: 10px; border-radius: 10px; font-size: 16px; }
    .metric-icon-red { color: #DC2626; background: #FEE2E2; padding: 10px; border-radius: 10px; font-size: 16px; }

    /* Section Headers */
    .section-head {
        font-size: 20px;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.3px;
    }
    
    /* Styled Containers & Cards */
    .setting-section {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    .setting-section-title {
        font-size: 15px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Table & Data Editor Enhancements */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #CBD5E1;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }

    /* Styled Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        border: none;
        color: #FFFFFF;
        font-weight: 700;
        border-radius: 10px;
        padding: 10px 20px;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
        transition: all 0.2s ease;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4338CA 0%, #2563EB 100%);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
        transform: translateY(-1px);
    }

    /* Badge Pills */
    .custom-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background: #F1F5F9;
        color: #475569;
        border: 1px solid #E2E8F0;
    }

    .custom-badge-active {
        background: #ECFDF5;
        color: #047857;
        border-color: #A7F3D0;
    }
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

