import re
import yaml 
import requests
import webbrowser
import pandas as pd 
import streamlit as st
from io import BytesIO 
from rmb_converter import to_rmb_upper
import streamlit_authenticator as stauth

# load config
with open('config.yaml') as file:
    config = yaml.safe_load(file)

username, password = st.secrets['auth']['username'], st.secrets['auth']['password']
config['credentials']['usernames'][username]['password'] = password

#@st.cache_data
def load_excel(url):
    response = requests.get(url)
    return pd.read_excel(BytesIO(response.content), sheet_name="Analytics")

def get_google_sheet_download_link(edit_url: str, export_format: str = 'xlsx') -> str:
    """
    Convert a Google Sheets edit URL to a direct download link.
    
    Parameters:
        edit_url (str): The original Google Sheets edit URL.
        export_format (str): The format to export. Supported: 'xlsx', 'csv', 'pdf', 'ods', etc.
    
    Returns:
        str: The direct download URL.
    """
    # Extract the spreadsheet ID using regex
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', edit_url)
    if not match:
        raise ValueError("Invalid Google Sheets URL")
    
    sheet_id = match.group(1)
    
    # Construct download link
    download_link = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format={export_format}"
    return download_link

receipt_url = st.secrets["general"]["receipt_url"]
contract_url = st.secrets["general"]["contract_url"]
data_url = st.secrets["general"]["data_url"]
receipt_download = get_google_sheet_download_link(st.secrets["general"]["receipt_download"])

authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

def open_doc(link):
    webbrowser.open(link)

# Render login widget
authenticator.login()

# Main control flow
auth_status = st.session_state.get("authentication_status")

if "page" not in st.session_state:
    st.session_state.page = "main"

if auth_status:
    st.title(f"{st.session_state['name']}'s Work Space")

    # SIDE BAR
    with st.sidebar:
        st.image("https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png")
        st.sidebar.title("Options")

        # sec 1
        if st.sidebar.button("Main"):
            st.session_state.page = "main"
            st.rerun()
        elif st.sidebar.button("Analytics"):
            st.session_state.page = "analytics"
            st.rerun()
    
    authenticator.logout("Logout", "sidebar")

    if st.session_state.page == "main":
        # document files
        st.subheader("Documents")
        st.markdown(f'''
            <style>
            a.custom-button {{
                display: inline-block;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                line-height: 1.5;
                text-align: center;
                text-decoration: none;
                color: white;
                border-radius: 8px;
                margin: 4px 8px 4px 0;
                cursor: pointer;
                min-width: 140px; /* optional: ensures consistent width */
                transition: all 0.3s ease; 
            }}
                    
            a.custom-button:hover {{
                box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);  /* Soft shadow */
                transform: scale(1.05);  /* Slight grow */
            }}
                    
            .blue-bg {{ background-color: #4CAF50; }}
            .green-bg {{ background-color: #4CAF50; }}
            </style>

            <a href="{receipt_url}" target="_blank" class="custom-button blue-bg">Receipt</a>
            <a href="{contract_url}" target="_blank" class="custom-button green-bg">Contract</a>
        ''', unsafe_allow_html=True)

        st.subheader("Rules")
        st.markdown(
            f"""
            <style>
            iframe {{
                overflow: hidden !important;
                scrollbar-width: none !important;  /* Firefox */
            }}

            /* Hide scrollbar for WebKit browsers */
            iframe::-webkit-scrollbar {{
                display: none !important;
            }}
     
            </style>

            <iframe src="{data_url}" width="100%" height="600px" style="max-width: 900px; border: none; overflow: hidden;"></iframe>
            """,
            unsafe_allow_html=True
        )

        # rmb converter
        st.subheader("RMB Converter")
        number = st.text_input("Enter a number", "")
        # Convert button
        if st.button("Convert"):
            if number.isdigit():
                chinese_result = to_rmb_upper(int(number))
                st.success(f"Chinese Numerals: {chinese_result}")
            else:
                st.error("Please enter a valid positive integer.")

    elif st.session_state.page == "analytics":

        df = load_excel(receipt_download)

        # 1. Show raw data preview
        st.write("## Raw Data Preview")
        st.dataframe(df)

        # 2. revenue/company
        st.write('## Company Revenue Total')
        st.bar_chart(df, x="公司", y="收入")

        # 3. trend lines 
        st.write('## Company Revenue Trend')
        month_cols = ['一月', '二月', '三月', '四月', '五月', '六月',
              '七月', '八月', '九月', '十月', '十一月', '十二月']

        df_long = df.melt(
            id_vars=['公司', '收入'],
            value_vars=month_cols,
            var_name='月份',
            value_name='月收入'
        )

        month_map = {
            '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
            '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
        }
        df_long['month'] = df_long['月份'].map(month_map)

        df_wide = df_long.pivot(index='month', columns='公司', values='月收入')
        st.line_chart(df_wide, x_label="月份", y_label="公司")

elif auth_status is False:
    st.error("Username or password is incorrect.")

else:
    st.warning("Please log in to continue.")