import re
import yaml
import streamlit as st
import streamlit.components.v1 as components
from rmb_converter import to_rmb_upper
import streamlit_authenticator as stauth

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Work Space",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Card styling */
    .card {
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-decoration: none !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        min-height: 140px;
        text-align: center;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.3);
        text-decoration: none !important;
    }

    .card-green {
        background: linear-gradient(135deg, #0d7377 0%, #14a085 100%);
    }

    .card-blue {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }

    .card-orange {
        background: linear-gradient(135deg, #8e2de2 0%, #4a00e0 100%);
    }

    .card-title {
        color: white !important;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0.75rem 0 0.25rem 0;
        text-decoration: none !important;
    }

    .card-desc {
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.95rem;
        margin: 0;
        text-decoration: none !important;
    }

    .card-icon {
        font-size: 2.5rem;
    }

    /* Remove link styling inside cards */
    a.card, a.card:hover, a.card:visited, a.card:active {
        text-decoration: none !important;
        color: inherit !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        background: rgba(255,255,255,0.1);
        color: white;
        transition: all 0.3s ease;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255,255,255,0.2);
    }

    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }

    /* Welcome text */
    .welcome-text {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* RMB Result styling */
    .rmb-result {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }

    .rmb-result:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    .rmb-result:active {
        transform: scale(0.98);
    }

    .rmb-result-text {
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0;
        word-break: break-all;
    }

    .rmb-result-hint {
        color: rgba(255,255,255,0.7);
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }

    .copy-success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Load config
with open('config.yaml') as file:
    config = yaml.safe_load(file)

username, password = st.secrets['auth']['username'], st.secrets['auth']['password']
config['credentials']['usernames'][username]['password'] = password

# Load URLs from secrets
receipt_url = st.secrets["general"]["receipt_url"]
contract_url = st.secrets["general"]["contract_url"]
data_url = st.secrets["general"]["data_url"]

# Setup authenticator
authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

# Get auth status
auth_status = st.session_state.get("authentication_status")

# Login page
if not auth_status:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<p class="welcome-text">Welcome Back</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Sign in to access your workspace</p>', unsafe_allow_html=True)
        authenticator.login()
        if auth_status is False:
            st.error("Username or password is incorrect.")

# Main app
elif auth_status:
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Hi, {st.session_state['name']}")
        st.markdown("---")
        authenticator.logout("🚪 Logout", "main")
        st.markdown("---")
        st.caption("Work Documentation System v1.0")

    # Dashboard
    st.markdown('<p class="welcome-text">Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Quick access to your documents and tools</p>', unsafe_allow_html=True)

    # Document Cards
    st.markdown('<div class="section-header">📁 Documents</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'''
            <a href="{receipt_url}" target="_blank" class="card card-green">
                <span class="card-icon">🧾</span>
                <span class="card-title">Receipts</span>
                <span class="card-desc">View & manage receipts</span>
            </a>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown(f'''
            <a href="{contract_url}" target="_blank" class="card card-blue">
                <span class="card-icon">📝</span>
                <span class="card-title">Contracts</span>
                <span class="card-desc">View & manage contracts</span>
            </a>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown('''
            <div class="card card-orange">
                <span class="card-icon">🔢</span>
                <span class="card-title">RMB Converter</span>
                <span class="card-desc">Convert to Chinese numerals</span>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two column layout for Rules and Converter
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="section-header">📋 Rules & Guidelines</div>', unsafe_allow_html=True)
        st.markdown(
            f'''<iframe src="{data_url}" width="100%" height="500px"
                style="border: none; border-radius: 12px; background: white;"></iframe>''',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown('<div class="section-header">🔢 RMB Converter</div>', unsafe_allow_html=True)
        number = st.text_input("Enter amount", "", placeholder="e.g., 12345")
        if st.button("Convert to Chinese", use_container_width=True, type="primary"):
            if number.isdigit():
                chinese_result = to_rmb_upper(int(number))
                components.html(f'''
                    <style>
                        .rmb-result {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius: 12px;
                            padding: 1.5rem;
                            text-align: center;
                            cursor: pointer;
                            transition: all 0.3s ease;
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        }}
                        .rmb-result:hover {{
                            transform: scale(1.02);
                            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
                        }}
                        .rmb-result:active {{
                            transform: scale(0.98);
                        }}
                        .rmb-result-text {{
                            color: white;
                            font-size: 1.3rem;
                            font-weight: 600;
                            margin: 0;
                            word-break: break-all;
                        }}
                        .rmb-result-hint {{
                            color: rgba(255,255,255,0.7);
                            font-size: 0.8rem;
                            margin-top: 0.5rem;
                        }}
                        .copy-success {{
                            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
                        }}
                    </style>
                    <div class="rmb-result" id="rmb-box">
                        <p class="rmb-result-text">{chinese_result}</p>
                        <p class="rmb-result-hint" id="hint">📋 Click to copy</p>
                    </div>
                    <script>
                        const box = document.getElementById('rmb-box');
                        const hint = document.getElementById('hint');
                        const text = "{chinese_result}";
                        box.addEventListener('click', function() {{
                            navigator.clipboard.writeText(text).then(function() {{
                                box.classList.add('copy-success');
                                hint.innerText = '✓ Copied!';
                                setTimeout(function() {{
                                    box.classList.remove('copy-success');
                                    hint.innerText = '📋 Click to copy';
                                }}, 2000);
                            }});
                        }});
                    </script>
                ''', height=120)
            elif number:
                st.error("Please enter a valid positive integer.")
        st.markdown("---")
        st.caption("Converts numbers to formal Chinese RMB format used in financial documents.")
