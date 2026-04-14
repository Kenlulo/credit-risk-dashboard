"""
🏦 Credit Risk Dashboard — Bảng điều khiển Rủi ro Tín dụng
Giám sát danh mục cho vay, phân loại nợ, concentration risk, credit scoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
from sample_data import generate_sample_data, get_excel_template, get_full_sample_excel
import io
from datetime import datetime

# ============================================================
# CẤU HÌNH TRANG
# ============================================================
st.set_page_config(
    page_title="Credit Risk Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS TÙY CHỈNH
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Main background — giống FIH */
    [data-testid="stAppViewContainer"] { background-color: #E9ECEF; color: #1E1E1E; }

    /* Sidebar — nền màu Dark Green giống advanced_evaluator.py */
    [data-testid="stSidebar"] {
        background-color: #0B5C57 !important; border-right: none;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] { color: #F8F9F9 !important; }
    [data-testid="stSidebar"] .stRadio label { color: #F8F9F9 !important; }
    [data-testid="stSidebar"] .stSlider label, [data-testid="stSidebar"] .stNumberInput label { color: #F8F9F9 !important; }
    [data-testid="stSidebar"] .stSelectbox label { color: #F8F9F9 !important; }
    [data-testid="stHeader"] { background-color: transparent; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 98% !important; }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0A4F4A 0%, #0D6B65 60%, #1ABC9C 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(10,79,74,0.25);
    }
    .main-header h1 { color: #ffffff; font-size: 1.8rem; margin: 0; }
    .main-header p { color: #A8E6DF; margin: 0.3rem 0 0 0; font-size: 0.95rem; }

    /* KPI Cards — white + teal accent giống FIH */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 18px 14px;
        text-align: center;
        border-top: 3px solid #D5D8DC;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        transition: all 0.25s ease;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(26,188,156,0.15); border-top-color: #1ABC9C; }
    .kpi-value { color: #1ABC9C; font-size: 1.7rem; font-weight: 800; }
    .kpi-label { color: #7F8C8D; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; margin-top: 6px; }
    .kpi-green .kpi-value { color: #27AE60; }
    .kpi-green { border-top-color: #27AE60; }
    .kpi-red .kpi-value { color: #E74C3C; }
    .kpi-red { border-top-color: #E74C3C; }
    .kpi-yellow .kpi-value { color: #F39C12; }
    .kpi-yellow { border-top-color: #F39C12; }

    /* Alert boxes */
    .alert-red {
        background: #FDEDEC;
        border-left: 4px solid #E74C3C;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        color: #C0392B;
    }
    .alert-yellow {
        background: #FEF9E7;
        border-left: 4px solid #F39C12;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        color: #9A7D0A;
    }
    .alert-green {
        background: #EAFAF1;
        border-left: 4px solid #27AE60;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        color: #1E8449;
    }

    /* Scoring card */
    .score-card {
        background: linear-gradient(135deg, #0A4F4A 0%, #0D6B65 100%);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(10,79,74,0.3);
    }
    .score-value { font-size: 3.5rem; font-weight: 800; color: #1ABC9C; }
    .score-grade { font-size: 1.3rem; font-weight: 600; margin-top: 0.5rem; color: #A8E6DF; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: rgba(10,79,74,0.08);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #5D6D7E;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0A4F4A;
        color: #ffffff !important;
    }

    /* Dataframe */
    .dataframe { font-size: 0.85rem; }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Override Streamlit primary color — slider, radio, button → blue */
    [data-testid="stSlider"] [data-testid="stThumbValue"],
    [data-testid="stSlider"] .st-emotion-cache-1lkh3fd,
    div[data-baseweb="slider"] [role="slider"] { background-color: #2563EB !important; }
    div[data-baseweb="slider"] div[data-testid="stSliderThumb"] { background-color: #2563EB !important; }
    div[data-baseweb="slider"] div { border-color: #2563EB !important; }

    /* Slider track filled */
    [data-testid="stSlider"] .st-emotion-cache-ue6h4q { background: #2563EB !important; }
    div[data-baseweb="slider"] [data-testid="stSliderTrackFill"] { background: #2563EB !important; }

    /* Radio button selected */
    [data-testid="stRadio"] [data-testid="stMarkdownContainer"] + div span[aria-checked="true"],
    div[data-baseweb="radio"] div[data-checked="true"] div { border-color: #2563EB !important; background-color: #2563EB !important; }
    div[data-baseweb="radio"] [aria-checked="true"] div div { background-color: #2563EB !important; }

    /* Primary button */
    .stButton button[kind="primary"] { background-color: #2563EB !important; border-color: #2563EB !important; }
    .stButton button[kind="primary"]:hover { background-color: #1D4ED8 !important; }

    /* Download button */
    .stDownloadButton button { border-color: #2563EB !important; color: #2563EB !important; }

    /* Focus/active ring */
    *:focus { outline-color: #2563EB !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# NGÔN NGỮ / LANGUAGE
# ============================================================
_LANG = {
    # Header / Footer
    'Bảng điều khiển Giám sát Rủi ro Tín dụng | Phân loại theo Thông tư 11/2021/TT-NHNN': 'Credit Risk Monitoring Dashboard | Classification per Circular 11/2021/TT-NHNN',
    'Giám sát Rủi ro Tín dụng': 'Credit Risk Monitoring',
    '⚖️ DỰ ÁN CÁ NHÂN (PORTFOLIO PROJECT): Công cụ Giám sát Rủi ro Tín dụng mã nguồn mở. Các phân tích chỉ mang tính chất tham khảo.': '⚖️ PORTFOLIO PROJECT: Open-source Credit Risk Monitoring tool. All analyses are for reference purposes only.',
    '👉 **Nếu bạn muốn xem thêm dự án khác hãy [nhấp vào đây](https://hoanhkhoa.vercel.app)**': '👉 **To view more projects, please [click here](https://hoanhkhoa.vercel.app)**',

    # Sidebar
    '📂 NGUỒN DỮ LIỆU': '📂 DATA SOURCE',
    'Chọn nguồn:': 'Select source:',
    '📊 Dữ liệu mẫu (30 KH)': '📊 Sample data (30 clients)',
    '📤 Upload file Excel': '📤 Upload Excel file',
    '📥 Template': '📥 Template',
    '📥 Mẫu đầy đủ': '📥 Full Sample',
    'Upload Excel:': 'Upload Excel:',
    '⚙️ CÀI ĐẶT GIỚI HẠN': '⚙️ LIMIT SETTINGS',
    'Giới hạn 1 ngành (%)': 'Single industry limit (%)',
    'Giới hạn 1 khu vực (%)': 'Single region limit (%)',
    'Giới hạn 1 KH lớn (%)': 'Single large client limit (%)',

    # Navigation
    'Tổng quan': 'Overview',
    'Phân loại Nợ': 'Loan Classification',
    'Rủi ro Tập trung': 'Concentration Risk',
    'Chấm điểm TD': 'Credit Scoring',
    'Báo cáo': 'Report',

    # KPI cards
    'Tổng dư nợ': 'Total Outstanding',
    'Số khách hàng': 'Total Clients',
    'Tỷ lệ nợ xấu (NPL)': 'NPL Ratio',
    'Tỷ lệ bao phủ TSĐB': 'Collateral Coverage',
    'Tổng dự phòng': 'Total Provisions',

    # Tab 1 - Overview
    'Dư nợ theo Ngành': 'Outstanding Loans by Industry',
    'Cơ cấu Nhóm nợ': 'Loan Group Structure',
    '🏢 Top 10 Khách hàng dư nợ lớn nhất': '🏢 Top 10 Largest Borrowers',
    '% Tổng dư nợ': '% Total Outstanding',

    # Tab 2 - Loan Classification
    '🏷️ Phân loại Nợ theo Thông tư 11/2021/TT-NHNN': '🏷️ Loan Classification per Circular 11/2021/TT-NHNN',
    'Nhóm': 'Group',
    'Phân loại': 'Classification',
    'Số KH': 'No. Clients',
    'Dư nợ (tỷ)': 'Outstanding (Bn)',
    '% Tổng dư nợ_col': '% Total Outstanding',
    'Tỷ lệ dự phòng': 'Provision Rate',
    'Dự phòng (tỷ)': 'Provision (Bn)',
    'Phân bổ Nhóm nợ theo Ngành': 'Loan Group Distribution by Industry',
    '📋 Chi tiết từng Khách hàng': '📋 Client Detail',
    'Lọc theo nhóm nợ:': 'Filter by loan group:',

    # Tab 3 - Concentration Risk
    '📈 Phân tích Rủi ro Tập trung (Concentration Risk)': '📈 Concentration Risk Analysis',
    'Tập trung theo Ngành': 'Industry Concentration',
    'Tập trung theo Khu vực': 'Region Concentration',
    '% Tổng dư nợ_axis': '% Total Outstanding',
    '✅ Tất cả ngành trong giới hạn': '✅ All industries within limits',
    '✅ Tất cả khu vực trong giới hạn': '✅ All regions within limits',
    '🏢 Tập trung theo Khách hàng lớn (Top 10)': '🏢 Large Client Concentration (Top 10)',
    '🚨 Vượt limit': '🚨 Over limit',
    '⚠️ Cận limit': '⚠️ Near limit',
    '✅ OK': '✅ OK',
    '🏠 Tập trung theo Loại tài sản bảo đảm': '🏠 Concentration by Collateral Type',

    # Tab 4 - Credit Scoring
    '🏆 Mô hình Chấm điểm Tín dụng (Credit Scoring)': '🏆 Credit Scoring Model',
    'Nhập thông tin Khách hàng': 'Enter Client Information',
    'Tên khách hàng:': 'Client name:',
    'Công ty CP ABC': 'ABC Joint Stock Company',
    'Tỷ lệ Nợ/Vốn CSH (D/E):': 'Debt/Equity (D/E):',
    'Thấp hơn = tốt hơn. < 1.0 là lý tưởng': 'Lower = better. < 1.0 is ideal',
    'Current Ratio:': 'Current Ratio:',
    'Cao hơn = tốt hơn. > 1.5 là tốt': 'Higher = better. > 1.5 is good',
    'ROE (%):': 'ROE (%):',
    'Cao hơn = tốt hơn. > 15% là xuất sắc': 'Higher = better. > 15% is excellent',
    'Dư nợ đề xuất (tỷ):': 'Proposed loan (Bn):',
    'TSĐB (tỷ):': 'Collateral (Bn):',
    'Số năm hoạt động:': 'Years in operation:',
    'Lịch sử trả nợ (năm):': 'Repayment history (years):',
    '🔍 Chấm điểm': '🔍 Score',
    'Kết quả chấm điểm': 'Scoring Result',
    'Hạng': 'Grade',
    '📊 Chi tiết chấm điểm': '📊 Scoring Details',
    'Chỉ số': 'Metric',
    'Giá trị': 'Value',
    'Trọng số': 'Weight',
    'Lịch sử trả nợ': 'Repayment History',
    'Năm hoạt động': 'Years Active',
    'năm': 'years',
    'Nhập thông tin khách hàng bên trái': 'Enter client information on the left',
    'và nhấn': 'and click',
    'Chấm điểm': 'Score',
    '📋 Xếp hạng Toàn bộ Danh mục': '📋 Full Portfolio Rating',
    'Phân bổ Xếp hạng tín dụng': 'Credit Rating Distribution',
    'Xếp hạng': 'Rating',

    # Tab 5 - Report
    '📋 Báo cáo Giám sát Rủi ro Tín dụng': '📋 Credit Risk Monitoring Report',
    'Ngày báo cáo:': 'Report date:',
    '1. Tóm tắt Danh mục': '1. Portfolio Summary',
    'Chỉ tiêu': 'Indicator',
    '2. Cảnh báo Rủi ro': '2. Risk Alerts',
    '3. Danh sách Nợ xấu (Nhóm 3-5)': '3. Non-Performing Loans (Group 3-5)',
    'Không có khách hàng nợ xấu': 'No non-performing clients',
    '4. Khách hàng cần Theo dõi (Nhóm 2)': '4. Clients Under Watch (Group 2)',
    'Không có khách hàng cần theo dõi': 'No clients under watch',
    '5. Đề xuất': '5. Recommendations',
    '✅ Không có cảnh báo rủi ro nào': '✅ No risk alerts',

    # Nhóm nợ names
    'Nợ đủ tiêu chuẩn': 'Standard Loan',
    'Nợ cần chú ý': 'Watch Loan',
    'Nợ dưới tiêu chuẩn': 'Substandard Loan',
    'Nợ nghi ngờ': 'Doubtful Loan',
    'Nợ có khả năng mất vốn': 'Loss Loan',

    # Credit grade
    'Rủi ro thấp': 'Low Risk',
    'Rủi ro trung bình': 'Medium Risk',
    'Rủi ro cao': 'High Risk',
    'Rủi ro rất cao': 'Very High Risk',
    'Rủi ro cực cao': 'Extreme Risk',
    '✅ Cho vay bình thường': '✅ Approve loan',
    '🟡 Cho vay có điều kiện': '🟡 Conditional loan',
    '🟠 Cần thêm TSĐB': '🟠 Requires more collateral',
    '🔴 Hạn chế cho vay': '🔴 Restrict lending',
    '⛔ Từ chối': '⛔ Reject',

    # Format
    'nghìn tỷ': 'Tn',
    'tỷ': 'Bn',
    'KH': 'Clients',

    # Report recommendations
    'Tăng cường đôn đốc thu hồi nợ nhóm 3-5': 'Intensify recovery efforts for Group 3-5 loans',
    'Rà soát lại chính sách cho vay, thắt chặt điều kiện cấp tín dụng': 'Review lending policies, tighten credit approval criteria',
    'Yêu cầu bổ sung TSĐB cho các khoản vay thiếu tài sản bảo đảm': 'Request additional collateral for under-secured loans',
    'Danh mục tín dụng trong tình trạng kiểm soát tốt': 'Credit portfolio is well under control',
    'Tiếp tục giám sát định kỳ theo quy định': 'Continue periodic monitoring per regulations',
}

def t(text):
    """Translate Vietnamese → English if English mode selected."""
    if st.session_state.get('lang', '🇻🇳 Tiếng Việt') == '🇬🇧 English':
        return _LANG.get(text, text)
    return text


# ============================================================
# HÀM TIỆN ÍCH
# ============================================================
def classify_loan(ngay_qua_han):
    """Phân loại nợ theo Thông tư 11/2021/TT-NHNN"""
    if ngay_qua_han < 10: return 1
    elif ngay_qua_han <= 90: return 2
    elif ngay_qua_han <= 180: return 3
    elif ngay_qua_han <= 360: return 4
    else: return 5

def get_nhom_info(nhom):
    """Trả về thông tin nhóm nợ"""
    info = {
        1: {'ten': 'Nợ đủ tiêu chuẩn', 'mau': '#66bb6a', 'du_phong': 0.0, 'icon': '🟢'},
        2: {'ten': 'Nợ cần chú ý', 'mau': '#ffa726', 'du_phong': 0.05, 'icon': '🟡'},
        3: {'ten': 'Nợ dưới tiêu chuẩn', 'mau': '#ff7043', 'du_phong': 0.20, 'icon': '🟠'},
        4: {'ten': 'Nợ nghi ngờ', 'mau': '#ef5350', 'du_phong': 0.50, 'icon': '🔴'},
        5: {'ten': 'Nợ có khả năng mất vốn', 'mau': '#b71c1c', 'du_phong': 1.0, 'icon': '⚫'}
    }
    return info.get(nhom, info[1])

def credit_score(de, cr, roe, nam_hd, lich_su, tsdb_ratio):
    """Tính điểm tín dụng"""
    score = 0
    
    # D/E Ratio (20%) — thấp hơn = tốt hơn
    if de <= 0.5: score += 20
    elif de <= 1.0: score += 16
    elif de <= 1.5: score += 12
    elif de <= 2.5: score += 8
    else: score += 4
    
    # Current Ratio (15%) — cao hơn = tốt hơn
    if cr >= 2.5: score += 15
    elif cr >= 2.0: score += 12
    elif cr >= 1.5: score += 9
    elif cr >= 1.0: score += 6
    else: score += 3
    
    # ROE (15%)
    if roe >= 15: score += 15
    elif roe >= 10: score += 12
    elif roe >= 5: score += 9
    elif roe >= 0: score += 5
    else: score += 2
    
    # Lịch sử trả nợ (20%)
    if lich_su >= 10: score += 20
    elif lich_su >= 7: score += 16
    elif lich_su >= 5: score += 12
    elif lich_su >= 3: score += 8
    else: score += 4
    
    # TSĐB / Dư nợ (15%)
    if tsdb_ratio >= 2.0: score += 15
    elif tsdb_ratio >= 1.5: score += 12
    elif tsdb_ratio >= 1.0: score += 9
    elif tsdb_ratio >= 0.5: score += 5
    else: score += 2
    
    # Năm hoạt động (15%)
    if nam_hd >= 15: score += 15
    elif nam_hd >= 10: score += 12
    elif nam_hd >= 5: score += 9
    elif nam_hd >= 3: score += 6
    else: score += 3
    
    return score

def get_grade(score):
    """Xếp hạng theo điểm"""
    if score >= 80: return 'A', t('Rủi ro thấp'), '#66bb6a', t('✅ Cho vay bình thường')
    elif score >= 60: return 'B', t('Rủi ro trung bình'), '#4fc3f7', t('🟡 Cho vay có điều kiện')
    elif score >= 40: return 'C', t('Rủi ro cao'), '#ffa726', t('🟠 Cần thêm TSĐB')
    elif score >= 20: return 'D', t('Rủi ro rất cao'), '#ef5350', t('🔴 Hạn chế cho vay')
    else: return 'E', t('Rủi ro cực cao'), '#b71c1c', t('⛔ Từ chối')

def format_ty(value):
    """Format số tỷ VND"""
    if value >= 1000:
        return f"{value/1000:,.1f} {t('nghìn tỷ')}"
    return f"{value:,.1f} {t('tỷ')}"


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    lang_choice = st.radio("🌍 Ngôn ngữ / Language:", ['🇻🇳 Tiếng Việt', '🇬🇧 English'], horizontal=True, label_visibility="collapsed")
    st.session_state.lang = lang_choice

    st.markdown(f"""
    <div style='text-align:center; padding: 1rem 0 0.5rem 0;'>
        <span style='font-size:2.5rem;'>🏦</span>
        <h2 style='color:#F8F9F9 !important; margin:0.3rem 0 0 0; font-size:1.1rem;'>Credit Risk Dashboard</h2>
        <p style='color:#A8E6DF !important; font-size:0.75rem; margin:0;'>{t('Giám sát Rủi ro Tín dụng')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Menu labels (translated)
    _menu_vi = ["Tổng quan", "Phân loại Nợ", "Rủi ro Tập trung", "Chấm điểm TD", "Báo cáo"]
    _menu_display = [t(m) for m in _menu_vi]

    # Vertical navigation menu
    selected_display = option_menu(
        menu_title=None,
        options=_menu_display,
        icons=["bar-chart-fill", "tags-fill", "exclamation-triangle-fill", "trophy-fill", "file-earmark-text-fill"],
        default_index=0,
        styles={
            "container": {"background-color": "#F8FAFC", "padding": "10px", "border-radius": "10px", "margin-bottom": "15px"},
            "nav-link": {"font-size": "14px", "font-weight": "500", "color": "#1E293B", "--hover-color": "#E2E8F0"},
            "nav-link-selected": {"background-color": "#2563EB", "color": "white", "font-weight": "bold"},
            "icon": {"color": "#64748B"}
        }
    )
    # Map display label back to internal Vietnamese key
    _display_to_vi = dict(zip(_menu_display, _menu_vi))
    selected = _display_to_vi.get(selected_display, "Tổng quan")

    st.markdown("---")

    # Data source
    st.markdown(f"<p style='color:#A8E6DF; font-size:0.8rem; font-weight:600; margin-bottom:4px;'>{t('📂 NGUỒN DỮ LIỆU')}</p>", unsafe_allow_html=True)
    _src_vi = ["📊 Dữ liệu mẫu (30 KH)", "📤 Upload file Excel"]
    _src_display = [t(s) for s in _src_vi]
    data_source_display = st.radio(
        t("Chọn nguồn:"),
        _src_display,
        label_visibility="collapsed"
    )
    data_source = dict(zip(_src_display, _src_vi)).get(data_source_display, _src_vi[0])

    if data_source == "📤 Upload file Excel":
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                t("📥 Template"),
                data=get_excel_template(),
                file_name="credit_risk_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            st.download_button(
                t("📥 Mẫu đầy đủ"),
                data=get_full_sample_excel(),
                file_name="credit_risk_sample_30kh.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        uploaded = st.file_uploader(t("Upload Excel:"), type=['xlsx', 'xls'])
    else:
        uploaded = None

    st.markdown("---")
    st.markdown(f"<p style='color:#A8E6DF; font-size:0.8rem; font-weight:600; margin-bottom:4px;'>{t('⚙️ CÀI ĐẶT GIỚI HẠN')}</p>", unsafe_allow_html=True)
    limit_nganh = st.number_input(t("Giới hạn 1 ngành (%)"), min_value=1, max_value=100, value=25, step=1)
    limit_khuvuc = st.number_input(t("Giới hạn 1 khu vực (%)"), min_value=1, max_value=100, value=30, step=1)
    limit_kh = st.number_input(t("Giới hạn 1 KH lớn (%)"), min_value=1, max_value=100, value=15, step=1)




# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data_from_upload(file_bytes):
    return pd.read_excel(io.BytesIO(file_bytes))

if uploaded:
    try:
        df = load_data_from_upload(uploaded.getvalue())
        st.sidebar.success(f"✅ Đã tải {len(df)} khách hàng")
    except Exception as e:
        st.sidebar.error(f"❌ Lỗi đọc file: {e}")
        df = generate_sample_data()
else:
    df = generate_sample_data()

# Tính nhóm nợ
if 'Số ngày quá hạn' in df.columns:
    df['Nhóm nợ'] = df['Số ngày quá hạn'].apply(classify_loan)
    df['Tên nhóm'] = df['Nhóm nợ'].apply(lambda x: get_nhom_info(x)['ten'])
    df['Tỷ lệ dự phòng'] = df['Nhóm nợ'].apply(lambda x: get_nhom_info(x)['du_phong'])
    df['Dự phòng (tỷ)'] = df['Dư nợ (tỷ)'] * df['Tỷ lệ dự phòng']

# Tính điểm tín dụng nếu có đủ cột
if all(c in df.columns for c in ['D/E', 'Current Ratio', 'ROE (%)', 'Năm hoạt động', 'Lịch sử trả nợ (năm)', 'TSĐB (tỷ)', 'Dư nợ (tỷ)']):
    df['Điểm TD'] = df.apply(
        lambda r: credit_score(r['D/E'], r['Current Ratio'], r['ROE (%)'], 
                               r['Năm hoạt động'], r['Lịch sử trả nợ (năm)'], 
                               r['TSĐB (tỷ)'] / max(r['Dư nợ (tỷ)'], 0.01)), axis=1)
    df['Xếp hạng'] = df['Điểm TD'].apply(lambda x: get_grade(x)[0])


# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class="main-header">
    <h1>🏦 Credit Risk Dashboard</h1>
    <p>{t('Bảng điều khiển Giám sát Rủi ro Tín dụng | Phân loại theo Thông tư 11/2021/TT-NHNN')}</p>
</div>
""", unsafe_allow_html=True)

st.warning(t("⚖️ DỰ ÁN CÁ NHÂN (PORTFOLIO PROJECT): Công cụ Giám sát Rủi ro Tín dụng mã nguồn mở. Các phân tích chỉ mang tính chất tham khảo."))
st.markdown(t("👉 **Nếu bạn muốn xem thêm dự án khác hãy [nhấp vào đây](https://hoanhkhoa.vercel.app)**"))
st.markdown("---")

# ============================================================
# TÍNH TOÁN KPI (dùng chung cho mọi tab)
# ============================================================
tong_du_no = df['Dư nợ (tỷ)'].sum()
so_kh = len(df)
no_xau = df[df['Nhóm nợ'] >= 3]['Dư nợ (tỷ)'].sum() if 'Nhóm nợ' in df.columns else 0
npl_ratio = (no_xau / tong_du_no * 100) if tong_du_no > 0 else 0
tong_tsdb = df['TSĐB (tỷ)'].sum() if 'TSĐB (tỷ)' in df.columns else 0
coverage = (tong_tsdb / tong_du_no * 100) if tong_du_no > 0 else 0
tong_du_phong = df['Dự phòng (tỷ)'].sum() if 'Dự phòng (tỷ)' in df.columns else 0
nganh_conc = df.groupby('Ngành')['Dư nợ (tỷ)'].sum().reset_index()
nganh_conc['%'] = (nganh_conc['Dư nợ (tỷ)'] / tong_du_no * 100).round(1)
nganh_conc = nganh_conc.sort_values('%', ascending=False)
kv_conc = df.groupby('Khu vực')['Dư nợ (tỷ)'].sum().reset_index()
kv_conc['%'] = (kv_conc['Dư nợ (tỷ)'] / tong_du_no * 100).round(1)
kv_conc = kv_conc.sort_values('%', ascending=False)

# ============================================================
# NỘI DUNG THEO MENU
# ============================================================

# ============================================================
# TAB 1: TỔNG QUAN
# ============================================================
if selected == "Tổng quan":
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{format_ty(tong_du_no)}</div>
            <div class="kpi-label">{t('Tổng dư nợ')}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{so_kh}</div>
            <div class="kpi-label">{t('Số khách hàng')}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        npl_class = "kpi-green" if npl_ratio < 3 else ("kpi-yellow" if npl_ratio < 5 else "kpi-red")
        st.markdown(f"""
        <div class="kpi-card {npl_class}">
            <div class="kpi-value">{npl_ratio:.1f}%</div>
            <div class="kpi-label">{t('Tỷ lệ nợ xấu (NPL)')}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        cov_class = "kpi-green" if coverage >= 100 else ("kpi-yellow" if coverage >= 70 else "kpi-red")
        st.markdown(f"""
        <div class="kpi-card {cov_class}">
            <div class="kpi-value">{coverage:.0f}%</div>
            <div class="kpi-label">{t('Tỷ lệ bao phủ TSĐB')}</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="kpi-card kpi-red">
            <div class="kpi-value">{format_ty(tong_du_phong)}</div>
            <div class="kpi-label">{t('Tổng dự phòng')}</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Dư nợ theo ngành
        nganh_data = df.groupby('Ngành')['Dư nợ (tỷ)'].sum().sort_values(ascending=True).reset_index()
        fig_nganh = px.bar(
            nganh_data, x='Dư nợ (tỷ)', y='Ngành', orientation='h',
            color='Dư nợ (tỷ)', color_continuous_scale=['#0A4F4A', '#1ABC9C', '#A8E6DF'],
            title=t('Dư nợ theo Ngành')
        )
        fig_nganh.update_layout(
            plot_bgcolor='rgba(255,255,255,0.8)', paper_bgcolor='rgba(255,255,255,0)',
            font_color='#2C3E50', title_font_color='#0A4F4A',
            coloraxis_showscale=False, height=350,
            margin=dict(l=0, r=20, t=40, b=0)
        )
        fig_nganh.update_xaxes(gridcolor='#ECF0F1')
        st.plotly_chart(fig_nganh, use_container_width=True)
    
    with col2:
        # Cơ cấu nhóm nợ
        if 'Nhóm nợ' in df.columns:
            nhom_data = df.groupby('Nhóm nợ')['Dư nợ (tỷ)'].sum().reset_index()
            nhom_data['Tên'] = nhom_data['Nhóm nợ'].apply(lambda x: f"{t('Nhóm')} {x}: {t(get_nhom_info(x)['ten'])}")
            colors = [get_nhom_info(n)['mau'] for n in nhom_data['Nhóm nợ']]
            
            fig_nhom = px.pie(
                nhom_data, values='Dư nợ (tỷ)', names='Tên',
                color_discrete_sequence=colors,
                title=t('Cơ cấu Nhóm nợ')
            )
            fig_nhom.update_layout(
                plot_bgcolor='rgba(255,255,255,0)', paper_bgcolor='rgba(255,255,255,0)',
                font_color='#2C3E50', title_font_color='#0A4F4A',
                height=350, margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(font=dict(size=10))
            )
            fig_nhom.update_traces(textposition='inside', textinfo='percent+label',
                                   textfont_size=10)
            st.plotly_chart(fig_nhom, use_container_width=True)
    
    # Top 10 KH dư nợ lớn
    st.markdown(f"#### {t('🏢 Top 10 Khách hàng dư nợ lớn nhất')}")
    top10 = df.nlargest(10, 'Dư nợ (tỷ)')[['Mã KH', 'Tên KH', 'Ngành', 'Dư nợ (tỷ)', 'TSĐB (tỷ)', 'Nhóm nợ', 'Xếp hạng']].copy()
    top10[t('% Tổng dư nợ')] = (top10['Dư nợ (tỷ)'] / tong_du_no * 100).round(1)
    st.dataframe(top10, use_container_width=True, hide_index=True)


# ============================================================
# TAB 2: PHÂN LOẠI NỢ
# ============================================================
elif selected == "Phân loại Nợ":
    st.markdown(f"#### {t('🏷️ Phân loại Nợ theo Thông tư 11/2021/TT-NHNN')}")
    
    # Summary table
    summary_data = []
    for nhom in range(1, 6):
        info = get_nhom_info(nhom)
        nhom_df = df[df['Nhóm nợ'] == nhom]
        du_no_nhom = nhom_df['Dư nợ (tỷ)'].sum()
        du_phong = du_no_nhom * info['du_phong']
        summary_data.append({
            t('Nhóm'): f"{info['icon']} {t('Nhóm')} {nhom}",
            t('Phân loại'): t(info['ten']),
            t('Số KH'): len(nhom_df),
            t('Dư nợ (tỷ)'): round(du_no_nhom, 1),
            t('% Tổng dư nợ'): f"{du_no_nhom/tong_du_no*100:.1f}%" if tong_du_no > 0 else "0%",
            t('Tỷ lệ dự phòng'): f"{info['du_phong']*100:.0f}%",
            t('Dự phòng (tỷ)'): round(du_phong, 1)
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Tổng dự phòng
    st.markdown(f"""
    <div class="alert-red">
        <strong>💰 {t('Tổng dự phòng')}: {format_ty(tong_du_phong)}</strong>
        &nbsp;&nbsp;|&nbsp;&nbsp; NPL ({t('Nhóm')} 3-5): {format_ty(no_xau)} ({npl_ratio:.1f}%)
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stacked bar chart
    fig_stack = go.Figure()
    for nhom in range(1, 6):
        info = get_nhom_info(nhom)
        nhom_df = df[df['Nhóm nợ'] == nhom]
        if len(nhom_df) > 0:
            nganh_nhom = nhom_df.groupby('Ngành')['Dư nợ (tỷ)'].sum().reset_index()
            fig_stack.add_trace(go.Bar(
                name=f"{t('Nhóm')} {nhom}: {t(info['ten'])}",
                x=nganh_nhom['Ngành'], y=nganh_nhom['Dư nợ (tỷ)'],
                marker_color=info['mau']
            ))
    
    fig_stack.update_layout(
        barmode='stack', title=t('Phân bổ Nhóm nợ theo Ngành'),
        plot_bgcolor='rgba(255,255,255,0.8)', paper_bgcolor='rgba(255,255,255,0)',
        font_color='#2C3E50', title_font_color='#0A4F4A',
        height=400, legend=dict(font=dict(size=10)),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    fig_stack.update_xaxes(gridcolor='#ECF0F1')
    fig_stack.update_yaxes(gridcolor='#ECF0F1')
    st.plotly_chart(fig_stack, use_container_width=True)
    
    # Chi tiết từng KH
    st.markdown(f"#### {t('📋 Chi tiết từng Khách hàng')}")
    nhom_filter = st.multiselect(t("Lọc theo nhóm nợ:"), [1, 2, 3, 4, 5], default=[3, 4, 5])
    filtered = df[df['Nhóm nợ'].isin(nhom_filter)] if nhom_filter else df
    display_cols = ['Mã KH', 'Tên KH', 'Ngành', 'Dư nợ (tỷ)', 'TSĐB (tỷ)', 
                    'Số ngày quá hạn', 'Nhóm nợ', 'Tên nhóm', 'Dự phòng (tỷ)']
    display_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[display_cols].sort_values('Nhóm nợ', ascending=False), 
                 use_container_width=True, hide_index=True)


# ============================================================
# TAB 3: RỦI RO TẬP TRUNG
# ============================================================
elif selected == "Rủi ro Tập trung":
    st.markdown(f"#### {t('📈 Phân tích Rủi ro Tập trung (Concentration Risk)')}")
    
    col1, col2 = st.columns(2)
    
    # --- Theo Ngành ---
    with col1:
        st.markdown(f"##### {t('Tập trung theo Ngành')}")
        
        colors_nganh = []
        alerts_nganh = []
        for _, row in nganh_conc.iterrows():
            if row['%'] > limit_nganh:
                colors_nganh.append('#ef5350')
                alerts_nganh.append(f"🚨 **{row['Ngành']}**: {row['%']:.1f}% > giới hạn {limit_nganh}%")
            elif row['%'] > limit_nganh * 0.8:
                colors_nganh.append('#ffa726')
            else:
                colors_nganh.append('#4fc3f7')
        
        fig_conc_nganh = go.Figure(go.Bar(
            x=nganh_conc['Ngành'], y=nganh_conc['%'],
            marker_color=colors_nganh,
            text=nganh_conc['%'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        fig_conc_nganh.add_hline(y=limit_nganh, line_dash="dash", line_color="#ef5350",
                                  annotation_text=f"Limit: {limit_nganh}%")
        fig_conc_nganh.update_layout(
            plot_bgcolor='rgba(255,255,255,0.8)', paper_bgcolor='rgba(255,255,255,0)',
            font_color='#2C3E50', height=350,
            margin=dict(l=0, r=0, t=20, b=0),
            yaxis_title="% Tổng dư nợ"
        )
        fig_conc_nganh.update_yaxes(gridcolor='#ECF0F1')
        st.plotly_chart(fig_conc_nganh, use_container_width=True)
        
        for alert in alerts_nganh:
            st.markdown(f'<div class="alert-red">{alert}</div>', unsafe_allow_html=True)
        if not alerts_nganh:
            st.markdown(f'<div class="alert-green">{t("✅ Tất cả ngành trong giới hạn")}</div>', unsafe_allow_html=True)
    
    # --- Theo Khu vực ---
    with col2:
        st.markdown(f"##### {t('Tập trung theo Khu vực')}")
        
        colors_kv = []
        alerts_kv = []
        for _, row in kv_conc.iterrows():
            if row['%'] > limit_khuvuc:
                colors_kv.append('#ef5350')
                alerts_kv.append(f"🚨 **{row['Khu vực']}**: {row['%']:.1f}% > giới hạn {limit_khuvuc}%")
            elif row['%'] > limit_khuvuc * 0.8:
                colors_kv.append('#ffa726')
            else:
                colors_kv.append('#26c6da')
        
        fig_conc_kv = go.Figure(go.Bar(
            x=kv_conc['Khu vực'], y=kv_conc['%'],
            marker_color=colors_kv,
            text=kv_conc['%'].apply(lambda x: f"{x:.1f}%"),
            textposition='outside'
        ))
        fig_conc_kv.add_hline(y=limit_khuvuc, line_dash="dash", line_color="#ef5350",
                               annotation_text=f"Limit: {limit_khuvuc}%")
        fig_conc_kv.update_layout(
            plot_bgcolor='rgba(255,255,255,0.8)', paper_bgcolor='rgba(255,255,255,0)',
            font_color='#2C3E50', height=350,
            margin=dict(l=0, r=0, t=20, b=0),
            yaxis_title="% Tổng dư nợ"
        )
        fig_conc_kv.update_yaxes(gridcolor='#ECF0F1')
        st.plotly_chart(fig_conc_kv, use_container_width=True)
        
        for alert in alerts_kv:
            st.markdown(f'<div class="alert-red">{alert}</div>', unsafe_allow_html=True)
        if not alerts_kv:
            st.markdown(f'<div class="alert-green">{t("✅ Tất cả khu vực trong giới hạn")}</div>', unsafe_allow_html=True)
    
    # --- Top KH lớn ---
    st.markdown(f"##### {t('🏢 Tập trung theo Khách hàng lớn (Top 10)')}")
    top_kh = df.nlargest(10, 'Dư nợ (tỷ)')[['Mã KH', 'Tên KH', 'Ngành', 'Dư nợ (tỷ)']].copy()
    top_kh[t('% Tổng dư nợ')] = (top_kh['Dư nợ (tỷ)'] / tong_du_no * 100).round(1)
    top_kh[t('Xếp hạng')] = top_kh[t('% Tổng dư nợ')].apply(
        lambda x: t('🚨 Vượt limit') if x > limit_kh else (t('⚠️ Cận limit') if x > limit_kh * 0.8 else t('✅ OK'))
    )
    st.dataframe(top_kh, use_container_width=True, hide_index=True)
    
    # --- Theo loại TSĐB ---
    if 'Loại TSĐB' in df.columns:
        st.markdown(f"##### {t('🏠 Tập trung theo Loại tài sản bảo đảm')}")
        tsdb_conc = df.groupby('Loại TSĐB')['TSĐB (tỷ)'].sum().reset_index()
        tsdb_conc['%'] = (tsdb_conc['TSĐB (tỷ)'] / tsdb_conc['TSĐB (tỷ)'].sum() * 100).round(1)
        
        fig_tsdb = px.pie(tsdb_conc, values='TSĐB (tỷ)', names='Loại TSĐB',
                          color_discrete_sequence=px.colors.qualitative.Set2,
                          title='')
        fig_tsdb.update_layout(
            plot_bgcolor='rgba(255,255,255,0)', paper_bgcolor='rgba(255,255,255,0)',
            font_color='#2C3E50', height=350,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        fig_tsdb.update_traces(textposition='inside', textinfo='percent+label', textfont_size=11)
        st.plotly_chart(fig_tsdb, use_container_width=True)


# ============================================================
# TAB 4: CHẤM ĐIỂM TÍN DỤNG
# ============================================================
elif selected == "Chấm điểm TD":
    st.markdown(f"#### {t('🏆 Mô hình Chấm điểm Tín dụng (Credit Scoring)')}")
    
    col_input, col_result = st.columns([1, 1])
    
    with col_input:
        st.markdown(f"##### {t('Nhập thông tin Khách hàng')}")
        
        ten_input = st.text_input(t("Tên khách hàng:"), t("Công ty CP ABC"))
        
        c1, c2 = st.columns(2)
        with c1:
            de_input = st.number_input(t("Tỷ lệ Nợ/Vốn CSH (D/E):"), 0.0, 10.0, 1.2, 0.1, 
                                        help=t("Thấp hơn = tốt hơn. < 1.0 là lý tưởng"))
            cr_input = st.number_input(t("Current Ratio:"), 0.0, 10.0, 1.5, 0.1,
                                        help=t("Cao hơn = tốt hơn. > 1.5 là tốt"))
            roe_input = st.number_input(t("ROE (%):"), -50.0, 100.0, 12.0, 1.0,
                                         help=t("Cao hơn = tốt hơn. > 15% là xuất sắc"))
        with c2:
            du_no_input = st.number_input(t("Dư nợ đề xuất (tỷ):"), 0.1, 1000.0, 50.0, 5.0)
            tsdb_input = st.number_input(t("TSĐB (tỷ):"), 0.0, 2000.0, 60.0, 5.0)
            nam_hd_input = st.number_input(t("Số năm hoạt động:"), 0, 50, 8)
        lich_su_input = st.number_input(t("Lịch sử trả nợ (năm):"), min_value=0, max_value=50, value=5, step=1)
        
        btn_score = st.button(t("🔍 Chấm điểm"), type="primary", use_container_width=True)
    
    with col_result:
        if btn_score:
            tsdb_ratio = tsdb_input / max(du_no_input, 0.01)
            score = credit_score(de_input, cr_input, roe_input, nam_hd_input, lich_su_input, tsdb_ratio)
            grade, risk_level, color, recommendation = get_grade(score)
            
            st.markdown(f"""
            <div class="score-card">
                <div style="color:#8ba3c4;font-size:0.9rem;">{t('Kết quả chấm điểm')}</div>
                <div class="score-value" style="color:{color};">{score}</div>
                <div class="score-grade" style="color:{color};">{t('Hạng')} {grade} — {risk_level}</div>
                <div style="color:#aab;font-size:1rem;margin-top:1rem;">{recommendation}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Chi tiết điểm
            st.markdown(f"##### {t('📊 Chi tiết chấm điểm')}")
            details = {
                t('Chỉ số'): ['D/E Ratio', 'Current Ratio', 'ROE', t('Lịch sử trả nợ'), 'TSĐB/Dư nợ', t('Năm hoạt động')],
                t('Giá trị'): [f"{de_input:.2f}", f"{cr_input:.2f}", f"{roe_input:.1f}%", 
                           f"{lich_su_input} {t('năm')}", f"{tsdb_ratio:.1f}x", f"{nam_hd_input} {t('năm')}"],
                t('Trọng số'): ['20%', '15%', '15%', '20%', '15%', '15%']
            }
            st.dataframe(pd.DataFrame(details), use_container_width=True, hide_index=True)
        
        else:
            st.markdown(f"""
            <div style="text-align:center;padding:3rem;color:#556677;">
                <p style="font-size:3rem;">🏦</p>
                <p>{t('Nhập thông tin khách hàng bên trái')}<br>{t('và nhấn')} <strong>{t('Chấm điểm')}</strong></p>
            </div>
            """, unsafe_allow_html=True)
    
    # Bảng xếp hạng toàn danh mục
    if 'Điểm TD' in df.columns:
        st.markdown("---")
        st.markdown(f"#### {t('📋 Xếp hạng Toàn bộ Danh mục')}")
        
        grade_dist = df['Xếp hạng'].value_counts().reset_index()
        grade_dist.columns = ['Xếp hạng', 'Số KH']
        grade_colors = {'A': '#66bb6a', 'B': '#4fc3f7', 'C': '#ffa726', 'D': '#ef5350', 'E': '#b71c1c'}
        
        fig_grade = px.bar(grade_dist, x='Xếp hạng', y='Số KH',
                           color='Xếp hạng', color_discrete_map=grade_colors,
                           text='Số KH', title=t('Phân bổ Xếp hạng tín dụng'))
        fig_grade.update_layout(
            plot_bgcolor='rgba(255,255,255,0.8)', paper_bgcolor='rgba(255,255,255,0)',
            font_color='#2C3E50', title_font_color='#0A4F4A',
            height=300, showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        fig_grade.update_yaxes(gridcolor='#ECF0F1')
        fig_grade.update_traces(textposition='outside')
        st.plotly_chart(fig_grade, use_container_width=True)
        
        ranking = df[['Mã KH', 'Tên KH', 'Ngành', 'Dư nợ (tỷ)', 'Điểm TD', 'Xếp hạng', 'Nhóm nợ']].copy()
        ranking = ranking.sort_values('Điểm TD', ascending=True)
        st.dataframe(ranking, use_container_width=True, hide_index=True)


# ============================================================
# TAB 5: BÁO CÁO
# ============================================================
elif selected == "Báo cáo":
    st.markdown(f"#### {t('📋 Báo cáo Giám sát Rủi ro Tín dụng')}")
    st.markdown(f"**{t('Ngày báo cáo:')}** {datetime.now().strftime('%d/%m/%Y')}")
    
    st.markdown("---")
    
    # 1. Tóm tắt
    st.markdown(f"##### {t('1. Tóm tắt Danh mục')}")
    summary_report = {
        t('Chỉ tiêu'): [t('Tổng dư nợ'), t('Số khách hàng'), t('Tỷ lệ nợ xấu (NPL)'), 
                      'TSĐB', t('Tỷ lệ bao phủ TSĐB'), t('Tổng dự phòng')],
        t('Giá trị'): [format_ty(tong_du_no), f"{so_kh} {t('KH')}", f"{npl_ratio:.1f}%",
                    format_ty(tong_tsdb), f"{coverage:.0f}%", format_ty(tong_du_phong)]
    }
    st.dataframe(pd.DataFrame(summary_report), use_container_width=True, hide_index=True)
    
    # 2. Cảnh báo
    st.markdown(f"##### {t('2. Cảnh báo Rủi ro')}")
    has_alert = False
    
    if npl_ratio >= 3:
        st.markdown(f'<div class="alert-red">🚨 Tỷ lệ nợ xấu {npl_ratio:.1f}% — vượt ngưỡng 3%</div>', unsafe_allow_html=True)
        has_alert = True
    
    # Check concentration
    for _, row in nganh_conc.iterrows():
        if row['%'] > limit_nganh:
            st.markdown(f'<div class="alert-red">🚨 Ngành {row["Ngành"]}: {row["%"]:.1f}% dư nợ — vượt giới hạn {limit_nganh}%</div>', unsafe_allow_html=True)
            has_alert = True
    
    for _, row in kv_conc.iterrows():
        if row['%'] > limit_khuvuc:
            st.markdown(f'<div class="alert-yellow">⚠️ Khu vực {row["Khu vực"]}: {row["%"]:.1f}% dư nợ — vượt giới hạn {limit_khuvuc}%</div>', unsafe_allow_html=True)
            has_alert = True
    
    if not has_alert:
        st.markdown(f'<div class="alert-green">{t("✅ Không có cảnh báo rủi ro nào")}</div>', unsafe_allow_html=True)
    
    # 3. Nợ xấu
    st.markdown(f"##### {t('3. Danh sách Nợ xấu (Nhóm 3-5)')}")
    no_xau_df = df[df['Nhóm nợ'] >= 3][['Mã KH', 'Tên KH', 'Ngành', 'Dư nợ (tỷ)', 
                                          'Số ngày quá hạn', 'Nhóm nợ', 'Tên nhóm', 'Dự phòng (tỷ)']].copy()
    if len(no_xau_df) > 0:
        st.dataframe(no_xau_df.sort_values('Nhóm nợ', ascending=False), 
                     use_container_width=True, hide_index=True)
    else:
        st.info(t("Không có khách hàng nợ xấu"))
    
    # 4. KH cần theo dõi (nhóm 2)
    st.markdown(f"##### {t('4. Khách hàng cần Theo dõi (Nhóm 2)')}")
    can_td = df[df['Nhóm nợ'] == 2][['Mã KH', 'Tên KH', 'Ngành', 'Dư nợ (tỷ)', 'Số ngày quá hạn']].copy()
    if len(can_td) > 0:
        st.dataframe(can_td, use_container_width=True, hide_index=True)
    else:
        st.info(t("Không có khách hàng cần theo dõi"))
    
    # 5. Đề xuất
    st.markdown(f"##### {t('5. Đề xuất')}")
    recommendations = []
    if npl_ratio >= 3:
        recommendations.append(f"- {t('Tăng cường đôn đốc thu hồi nợ nhóm 3-5')}")
        recommendations.append(f"- {t('Rà soát lại chính sách cho vay, thắt chặt điều kiện cấp tín dụng')}")
    
    for _, row in nganh_conc.iterrows():
        if row['%'] > limit_nganh:
            _is_en = st.session_state.get('lang', '🇻🇳 Tiếng Việt') == '🇬🇧 English'
            if _is_en:
                recommendations.append(f"- Gradually reduce exposure to {row['Ngành']} below {limit_nganh}%")
            else:
                recommendations.append(f"- Giảm dần dư nợ ngành {row['Ngành']} về dưới {limit_nganh}%")
    
    if coverage < 100:
        recommendations.append(f"- {t('Yêu cầu bổ sung TSĐB cho các khoản vay thiếu tài sản bảo đảm')}")
    
    if not recommendations:
        recommendations.append(f"- {t('Danh mục tín dụng trong tình trạng kiểm soát tốt')}")
        recommendations.append(f"- {t('Tiếp tục giám sát định kỳ theo quy định')}")
    
    for rec in recommendations:
        st.markdown(rec)
