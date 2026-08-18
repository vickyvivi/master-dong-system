import streamlit as st
import re
import requests
import os
import base64
import html
import datetime
import time
from lunar_python import Solar, Lunar

# -------------------------------------------------------------
# 0. 🔑 Google API Key 配置
# -------------------------------------------------------------

# -------------------------------------------------------------
# 1. 頁面全域配置
# -------------------------------------------------------------
st.set_page_config(
    page_title="辰祐閣 ‧ 數字易經排盤系統 (東方 MBTI 版)",
    page_icon="🔮",
    layout="wide"
)

# -------------------------------------------------------------
# 2. 狀態管理 (Session State)
# -------------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'report_cache' not in st.session_state:
    st.session_state.report_cache = None
if 'love_report_cache' not in st.session_state:
    st.session_state.love_report_cache = None
if 'career_report_cache' not in st.session_state:
    st.session_state.career_report_cache = None

def switch_page(page_name: str):
    st.session_state.page = page_name

def clear_report_cache():
    st.session_state.report_cache = None
    st.session_state.love_report_cache = None
    st.session_state.career_report_cache = None

# -------------------------------------------------------------
# 3. 自訂 CSS 樣式：水墨宣紙 ‧ 標題尺寸與防溢位排版優化
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;900&family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

    /* 鎖定全域水平滑動 */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #F5F2EB !important;
        color: #262626 !important;
        font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        overflow-x: hidden !important;
        max-width: 100vw !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    *:focus, *:focus-visible, *:focus-within {
        outline: none !important;
        box-shadow: none !important;
    }

    .block-container {
        max-width: 920px !important;
        width: 100% !important;
        padding-top: 4.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        overflow-x: hidden !important;
        box-sizing: border-box !important;
    }

    /* 頂部 Logo 與品牌標題區塊 */
    .brand-header-container {
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 24px;
        padding-top: 0.5rem;
    }
    .brand-logo-badge {
        display: inline-block;
        width: 52px;
        height: 52px;
        line-height: 48px;
        border: 1.5px solid #8C1C1C;
        border-radius: 50%;
        color: #8C1C1C;
        font-size: 22px;
        font-family: 'Noto Serif TC', serif;
        font-weight: 900;
        margin-bottom: 8px;
        background-color: transparent;
    }
    .brand-main-title {
        font-family: 'Noto Serif TC', serif !important;
        color: #1A1A1A !important;
        font-size: 30px !important;
        font-weight: 900;
        letter-spacing: 6px;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }
    .brand-sub-title {
        font-size: 11px;
        color: #78716C;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .brand-slogan-text {
        font-family: 'Noto Serif TC', serif !important;
        font-size: 15px;
        color: #8C1C1C;
        letter-spacing: 3px;
        font-weight: 700;
    }

    /* 報告內 Markdown 字體尺寸收斂（防止標題過大兩排折行） */
    .stMarkdown h1 {
        font-family: 'Noto Serif TC', serif !important;
        font-size: 21px !important;
        font-weight: 800 !important;
        color: #8C1C1C !important;
        line-height: 1.4 !important;
        letter-spacing: 1.5px !important;
        margin-top: 10px !important;
        margin-bottom: 16px !important;
        text-align: center !important;
    }
    .stMarkdown h2 {
        font-family: 'Noto Serif TC', serif !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #262626 !important;
        margin-top: 18px !important;
        margin-bottom: 12px !important;
    }
    .stMarkdown h3 {
        font-family: 'Noto Serif TC', serif !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #8C1C1C !important;
        border-bottom: 1px solid #E7E5E4 !important;
        padding-bottom: 6px !important;
        margin-top: 20px !important;
        margin-bottom: 12px !important;
    }
    .stMarkdown p, .stMarkdown li {
        font-size: 14.5px !important;
        line-height: 1.65 !important;
        color: #333333 !important;
    }

    [data-testid="stForm"] {
        background: #FFFFFF !important;
        border-radius: 20px !important;
        border: 1px solid #E0DACA !important;
        padding: 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        box-sizing: border-box !important;
        width: 100% !important;
    }

    [data-testid="stInputInstruction"], [data-testid="InputInstructions"] { display: none !important; }

    label, [data-testid="stWidgetLabel"] p {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
    }

    div[data-testid="stNumberInput"],
    div[data-testid="stNumberInput"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #8C1C1C !important;
        border-radius: 12px !important;
        box-shadow: none !important;
        outline: none !important;
        overflow: hidden !important;
    }

    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        color: #8C1C1C !important;
        -webkit-text-fill-color: #8C1C1C !important;
        font-weight: 800 !important;
        font-size: 20px !important;
        text-align: center !important;
        border: none !important;
        outline: none !important;
    }

    div[data-testid="stNumberInput"] button {
        background-color: #EBE5D8 !important;
        color: #8C1C1C !important;
        border: none !important;
        border-left: 1px solid #E0DACA !important;
    }

    [data-baseweb="tab-highlight-title"], [data-baseweb="tab-border"] { display: none !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        margin-top: 15px !important;
        flex-wrap: wrap !important;
    }

    .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] {
        background-color: #E2DACB !important;
        border-radius: 12px !important;
        border: 1.5px solid #C5BBB0 !important;
        padding: 8px 14px !important;
        opacity: 1 !important;
    }

    .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"] * {
        color: #444444 !important;
        -webkit-text-fill-color: #444444 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        opacity: 1 !important;
    }

    .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #8C1C1C !important;
        border: 1.5px solid #8C1C1C !important;
        opacity: 1 !important;
    }

    .stTabs [data-baseweb="tab-list"] button[data-baseweb="tab"][aria-selected="true"] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        opacity: 1 !important;
    }

    .stButton > button, [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #9E2A2A 0%, #8C1C1C 50%, #681212 100%) !important;
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 20px !important;
        width: 100% !important;
        letter-spacing: 2px !important;
        box-shadow: 0 4px 15px rgba(140, 28, 28, 0.25) !important;
    }

    .panel-header {
        color: #333333 !important;
        font-size: 17px;
        font-weight: 800;
        margin-top: 15px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #8C1C1C;
    }

    .combined-box {
        background: #FFFFFF !important;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 15px;
        border: 1px solid #E0DACA;
        display: flex;
        flex-wrap: wrap;
        gap: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        box-sizing: border-box !important;
        width: 100% !important;
    }

    .combined-col { display: flex; flex-direction: column; }
    .combined-core { flex: 1; min-width: 160px; border-right: 1px solid #E0DACA; padding-right: 12px; }
    .combined-matrix { flex: 1.2; min-width: 180px; border-right: 1px solid #E0DACA; padding-right: 12px; }
    .combined-energy { flex: 1; min-width: 140px; }

    @media (max-width: 640px) {
        .combined-core, .combined-matrix {
            border-right: none !important;
            border-bottom: 1px solid #E0DACA !important;
            padding-right: 0 !important;
            padding-bottom: 12px !important;
            min-width: 100% !important;
        }
    }

    .metric-item {
        background: #F8F5EE;
        border: 1px solid #E2DCCF;
        border-radius: 10px;
        padding: 8px 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .metric-value-gold { font-size: 16px; font-weight: 800; color: #8C1C1C; }
    .status-badge { font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: 6px; }
    .status-unbound { background: #E0DACA; color: #4A4A4A; }
    .status-bound { background: #D1FAE5; color: #065F46; }

    .matrix-row { display: flex; justify-content: center; align-items: center; gap: 8px; margin: 4px 0; flex-wrap: wrap; }
    .star-box {
        border: 1px solid #D0C8B8 !important;
        background-color: #F0ECE1 !important;
        border-radius: 10px; width: 54px; height: 54px;
        display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative;
    }
    .star-box-core {
        border: 2px solid #8C1C1C !important;
        background-color: #FDF2F2 !important;
        box-shadow: 0 0 10px rgba(140, 28, 28, 0.2) !important;
        border-radius: 10px; width: 54px; height: 54px;
        display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative;
    }
    .star-top, .star-bottom { font-size: 14px; font-weight: 700; color: #1A1A1A !important; }
    .star-mark { position: absolute; top: 1px; right: 3px; font-size: 11px !important; font-weight: 800 !important; color: #8C1C1C !important; }

    .tk-fieldset {
        border: 1px solid #E0DACA !important;
        padding: 12px 14px; margin-top: 16px; border-radius: 12px; background: #FAF7F0 !important;
        box-sizing: border-box !important;
    }
    .tk-legend { font-size: 13px; font-weight: 700; color: #8C1C1C !important; padding: 0 8px; }
    .tk-text-area { font-size: 13px; color: #333333 !important; white-space: pre-wrap; line-height: 1.6; word-break: break-all; }

    /* 辰祐閣雙盤結果頁：原創宣紙卡片系統 */
    .result-overview {
        position: relative; overflow: hidden;
        background: linear-gradient(145deg, rgba(255,253,247,.96), rgba(238,229,211,.92));
        border: 1px solid #D8C8AD; border-radius: 24px;
        padding: 22px 24px; margin: 22px 0 18px;
        box-shadow: 0 14px 34px rgba(78,55,35,.08);
    }
    .result-overview::after {
        content: "辰"; position: absolute; right: 18px; top: -18px;
        font-family: 'Noto Serif TC', serif; font-size: 108px; font-weight: 900;
        color: rgba(140,28,28,.045); transform: rotate(-8deg);
    }
    .overview-kicker { color:#8C1C1C; font-size:12px; font-weight:800; letter-spacing:3px; }
    .overview-title { font-family:'Noto Serif TC',serif; font-size:24px; font-weight:900; margin:5px 0; color:#29221D; }
    .overview-copy { color:#74675B; font-size:13px; line-height:1.7; max-width:650px; }
    .overview-dates { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; }
    .overview-date { background:rgba(255,255,255,.7); border:1px solid #DDD0BC; border-radius:999px; padding:6px 11px; font-size:12px; color:#544A42; }

    .destiny-card {
        --tone:#8C1C1C; --soft:#F8EDEA;
        height:100%; background:rgba(255,253,248,.96); border:1px solid #DCCFBD;
        border-top:5px solid var(--tone); border-radius:22px; padding:18px;
        box-shadow:0 10px 28px rgba(57,43,31,.07); box-sizing:border-box;
    }
    .destiny-card.lunar { --tone:#607D8B; --soft:#EDF3F5; }
    .destiny-card-head { display:flex; justify-content:space-between; gap:12px; align-items:center; padding-bottom:14px; border-bottom:1px solid #E7DCCB; }
    .destiny-eyebrow { color:var(--tone); font-size:11px; font-weight:900; letter-spacing:2px; }
    .destiny-title { font-family:'Noto Serif TC',serif; color:#2B2520; font-size:19px; font-weight:900; margin-top:3px; }
    .destiny-date { color:#7B7067; font-size:11px; margin-top:3px; }
    .life-seal { flex:0 0 76px; width:76px; height:76px; border-radius:50%; border:2px solid var(--tone); background:var(--soft); display:flex; flex-direction:column; justify-content:center; align-items:center; box-shadow:inset 0 0 0 5px rgba(255,255,255,.7); }
    .life-seal span { color:#796D63; font-size:9px; letter-spacing:1px; }
    .life-seal strong { color:var(--tone); font-family:'Noto Serif TC',serif; font-size:31px; line-height:1; }
    .formula-strip { margin:14px 0; padding:11px 12px; background:#F5EFE5; border-left:3px solid var(--tone); border-radius:4px 12px 12px 4px; }
    .formula-label { color:#8A7C70; font-size:10px; letter-spacing:1px; }
    .formula-value { color:#302923; font-size:13px; font-weight:800; word-break:break-all; margin-top:3px; }
    .stat-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:6px; margin:12px 0 15px; }
    .stat-chip { min-width:0; background:var(--soft); border:1px solid rgba(80,65,50,.09); border-radius:10px; padding:8px 4px; text-align:center; }
    .stat-chip b { display:block; color:var(--tone); font-size:16px; line-height:1.1; }
    .stat-chip span { display:block; color:#766B62; font-size:9px; margin-top:4px; white-space:nowrap; }
    .result-section-label { color:#75695E; font-size:11px; font-weight:800; letter-spacing:1px; margin:12px 0 7px; }
    .pattern-row { display:flex; align-items:center; justify-content:space-between; gap:8px; background:#FBF7F0; border:1px solid #E7DDCF; border-radius:12px; padding:9px 11px; }
    .pattern-name { color:#302923; font-weight:900; }
    .energy-list { min-height:40px; color:#4D443D; font-size:12px; line-height:1.7; }
    .energy-token { display:inline-block; color:var(--tone); background:var(--soft); border-radius:999px; padding:3px 8px; margin:2px; font-weight:800; }
    div[data-testid="stExpander"] { border:1px solid #DED2C0 !important; border-radius:14px !important; background:rgba(255,253,248,.8) !important; }
    div[data-testid="stExpander"] summary { color:#5D5046 !important; font-weight:800 !important; }

    @media (max-width:760px) {
        .result-overview { padding:18px; }
        .overview-title { font-size:21px; }
        .stat-grid { grid-template-columns:repeat(3,1fr); }
        .life-seal { flex-basis:66px; width:66px; height:66px; }
        .life-seal strong { font-size:27px; }
    }


    /* 商業化第一階段：品牌首屏、價值旅程與進階報告預覽 */
    .commerce-shell { margin-bottom:22px; }
    .commerce-nav { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:2px 2px 16px; border-bottom:1px solid rgba(126,101,75,.15); }
    .commerce-brand { display:flex; align-items:center; gap:10px; }
    .commerce-seal { width:38px; height:38px; border:1.5px solid #8C1C1C; border-radius:50%; display:grid; place-items:center; color:#8C1C1C; font-family:'Noto Serif TC',serif; font-weight:900; }
    .commerce-brand-name { font-family:'Noto Serif TC',serif; font-weight:900; letter-spacing:3px; color:#28211C; }
    .commerce-brand-en { font-size:8px; letter-spacing:1.7px; color:#94867A; margin-top:2px; }
    .commerce-nav-note { font-size:11px; color:#7B6F64; background:#F3EDE3; border-radius:999px; padding:6px 10px; }
    .commerce-hero { position:relative; overflow:hidden; margin-top:18px; padding:34px 34px 30px; border:1px solid #DCCDB8; border-radius:28px; background:linear-gradient(135deg,#FFFCF6 0%,#F3E9DA 58%,#E8EEF0 100%); box-shadow:0 18px 45px rgba(66,46,28,.09); }
    .commerce-hero::before { content:""; position:absolute; width:240px; height:240px; border:1px solid rgba(140,28,28,.10); border-radius:50%; right:-76px; top:-100px; box-shadow:0 0 0 24px rgba(140,28,28,.025),0 0 0 50px rgba(96,125,139,.025); }
    .commerce-kicker { color:#8C1C1C; font-size:11px; font-weight:900; letter-spacing:3px; }
    .commerce-title { position:relative; max-width:650px; margin:10px 0 12px; font-family:'Noto Serif TC',serif; font-size:34px; line-height:1.35; font-weight:900; color:#29211B; letter-spacing:1px; }
    .commerce-title em { color:#8C1C1C; font-style:normal; }
    .commerce-lead { position:relative; max-width:620px; color:#675B51; font-size:14px; line-height:1.85; }
    .commerce-pills { position:relative; display:flex; flex-wrap:wrap; gap:8px; margin-top:20px; }
    .commerce-pill { padding:7px 11px; border-radius:999px; background:rgba(255,255,255,.72); border:1px solid rgba(124,100,78,.16); color:#5E5349; font-size:11px; font-weight:700; }
    .value-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:14px 0 22px; }
    .value-card { background:rgba(255,253,248,.9); border:1px solid #E3D8C8; border-radius:16px; padding:14px; }
    .value-index { color:#8C1C1C; font-family:'Noto Serif TC',serif; font-size:17px; font-weight:900; }
    .value-title { color:#332A24; font-weight:900; font-size:13px; margin:5px 0 3px; }
    .value-copy { color:#7C7066; font-size:11px; line-height:1.6; }
    .entry-heading { text-align:center; margin:28px 0 13px; }
    .entry-heading small { color:#8C1C1C; letter-spacing:2px; font-size:10px; font-weight:900; }
    .entry-heading h2 { font-family:'Noto Serif TC',serif; color:#302720; font-size:22px; margin:5px 0 !important; }
    .entry-heading p { color:#81756A !important; font-size:12px !important; margin:0 !important; }
    .privacy-note { display:flex; justify-content:center; gap:8px; align-items:center; color:#7A7067; font-size:10px; margin:10px 0 2px; }

    .insight-intro { text-align:center; margin:8px 0 14px; }
    .insight-intro strong { display:block; color:#332820; font-family:'Noto Serif TC',serif; font-size:20px; }
    .insight-intro span { color:#80746A; font-size:11px; }
    .premium-preview { position:relative; overflow:hidden; background:#302925; color:#F7F0E5; border-radius:22px; padding:23px; margin:18px 0 10px; box-shadow:0 14px 34px rgba(40,30,23,.14); }
    .premium-preview::after { content:"祐"; position:absolute; right:12px; bottom:-36px; font-family:'Noto Serif TC',serif; font-size:110px; font-weight:900; color:rgba(255,255,255,.035); }
    .premium-kicker { color:#D8A9A2; font-size:10px; letter-spacing:2px; font-weight:900; }
    .premium-title { font-family:'Noto Serif TC',serif; font-size:21px; font-weight:900; margin:6px 0; }
    .premium-copy { color:#CFC4B8; font-size:12px; line-height:1.7; max-width:680px; }
    .premium-grid { position:relative; display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-top:14px; }
    .premium-item { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.1); border-radius:12px; padding:11px; }
    .premium-item b { display:block; color:#F7EFE3; font-size:12px; margin-bottom:3px; }
    .premium-item span { color:#BFB2A7; font-size:10px; line-height:1.5; }
    .test-badge { display:inline-block; margin-top:12px; color:#EAC8C2; border:1px solid rgba(234,200,194,.35); border-radius:999px; padding:4px 8px; font-size:9px; letter-spacing:1px; }

    @media (max-width:760px) {
        .commerce-nav-note { display:none; }
        .commerce-hero { padding:25px 20px; border-radius:22px; }
        .commerce-title { font-size:27px; }
        .value-grid { grid-template-columns:1fr; }
        .premium-grid { grid-template-columns:repeat(2,1fr); }
    }

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. 命理知識庫與東方 MBTI 配置庫
# -------------------------------------------------------------
SHEN_SHA_DB = {
    "比肩": {
        "title": "老學究", "power_type": "合作之力", "power_directions": ["合作力"],
        "positive": "有耐心、溫和、細心、謹慎、願意溝通、責任心強、人緣好。",
        "negative": "過度保守、固執主觀、狀態停滯、缺乏安全感、防衛心強。",
        "relatives": "代表兄弟、朋友、同僚。男命難有火花易晚婚；女命朋友圈廣。",
        "emotion": "豪氣、不拘小節、略帶神經質。",
        "advice": "用輕鬆愉快的方式打成一片，留意其是否有實質計畫。"
    },
    "劫財": {
        "title": "散財童子", "power_type": "合作之力", "power_directions": ["合作力"],
        "positive": "鬼點子多、特立獨行、具獨特魅力與吸引力、具備隱性才華。",
        "negative": "雙重人格、極度缺乏安全感、心思多、易遭遇財務流失。",
        "relatives": "代表異性緣、姊妹/兄弟。男命劫財為女性，女命劫財為男性。",
        "emotion": "性情靈活但心思隱晦，努力易無結果，財來財去。",
        "advice": "溝通要直接且有自信，千萬不可以取笑或惡言相向。"
    },
    "正官": {
        "title": "老闆", "power_type": "正義之星", "power_directions": ["執行力"],
        "positive": "獨當一面、不拘小節、大將之風、意志力堅強、掌控性強、責任心、使命感凌駕一切、王者風範與氣度。",
        "negative": "主觀意識強烈、喜歡打抱不平、不惜為正義而戰、較不圓融、一板一眼、好面子(面子裡子須兼顧)。",
        "relatives": "代表父親、丈夫、老闆、法官、年長的男性、主女性的異性追求者。在女命代表：父親、公司、丈夫、親密男友 (180度時會因夫而貴)。",
        "emotion": "責任、壓力、形象、自尊、面子、脾氣、扛責任、地位、名聲、權力、大男/女人主義。",
        "advice": "傾聽他的意見、觀察他的情緒、察顏悅色、鼓勵正向看。"
    },
    "七煞": {
        "title": "黑幫老大", "power_type": "正義之星", "power_directions": ["執行力"],
        "positive": "有膽識、開疆闢土、衝鋒陷陣、以口成就事業、盤聚力極強、口才佳、反應快。",
        "negative": "常有身體病痛或是口舌之爭、過度主觀、愛面子、說話易誇張、善於心計、內心脆弱、不堪打擊、無守成之力。",
        "relatives": "代表父親、丈夫、老闆、法官、年長的男性態度、主女性的異性追求者態度。",
        "emotion": "責任、壓力、形象、自尊、面子、脾氣、扛責任、重地位、名聲、權力。",
        "advice": "不能胡亂批評他、處理事情時也要配合他的速度、給他正面的評價、談話時先說正面的，負面的參雜著說。"
    },
    "正印": {
        "title": "貴人", "power_type": "仁慈之星", "power_directions": ["穩定力", "協調力"],
        "positive": "樂觀積極活潑、處事冷靜沉著、EQ極高、協調能力強、常有貴人(轉機)相助、能轉危為安、逢凶化吉、福星高照、具有犧牲奉獻(熱心)的精神。",
        "negative": "過度樂觀、不會未雨綢繆、協調不當、不懂得拒絕、承諾性高(答應太多做不完造成雙方壓力)。",
        "relatives": "代表母親、宗教家、師字輩、婆婆、年長的女性。",
        "emotion": "慈悲、包容、付出、熱心、重視心靈層面、宗教(信仰)緣強。",
        "advice": "避免激烈的口吻、正印格易被忽略，會覺得不受重視。"
    },
    "偏印": {
        "title": "紛亂桃花", "power_type": "仁慈之星", "power_directions": ["穩定力", "協調力"],
        "positive": "異性緣強(但不易有結果)、人氣旺、有意外的助力、行使好可人脈大小通吃、具有犧牲奉獻的精神(選擇性)、特立獨行、精明靈巧。",
        "negative": "意志力不堅定、耳根軟、常會與親近好友起衝突、人際關係較不佳、易有爛桃花、容易喜新厭舊、與人相處容易有弄巧成拙的狀況。",
        "relatives": "代表母親、宗教家、老師、女性長輩態度、對自己不利之入或長輩態度。",
        "emotion": "忌妒、溝通不良、易與親近的人產生誤解、孤單、分居、濫好人、易造成婚姻上的課題。",
        "advice": "尊重他們的感受、注意表達方式(平和請託而非要求)、直接且真誠的態度讚美他們。"
    },
    "食神": {
        "title": "財富", "power_type": "才華之星", "power_directions": ["創意力", "專業力"],
        "positive": "為人高尚、單純善良、在家庭及情感世界裡常是真心負責的典範、代表凡是順利、有赤子之心。",
        "negative": "過度包容、因為沒有堅持自己立場，受人欺侮時會把怨氣發在親友身上、安逸閒散、缺乏行動力。",
        "relatives": "代表妻子與妻子的態度、姑、嫂、叔、伯、在男盤時表示妻子 (女生食神在180度時會因妻而貴)。",
        "emotion": "智慧、德性、文采氣質、吃喝享樂、財富、安逸。",
        "advice": "小心他把事情合理化、用發問的方式使他聚焦、不能高壓、要自然輕鬆柔和的狀態。"
    },
    "傷官": {
        "title": "反對黨", "power_type": "才華之星", "power_directions": ["創意力", "專業力"],
        "positive": "有創造力、有才華、自我優越感、企劃能力強、心思細膩、善於謀略、具有別人看的到的才華。",
        "negative": "有兩極化的現象(大起大落)、主觀意識強、協調性差、常有意外發生、易有官司是非糾紛。",
        "relatives": "代表子女、家庭、部屬、幕僚人才、司法官、有官司訴訟問題。",
        "emotion": "創造力、直覺力、藝術天分、才華、思路敏捷、重視小孩(有時是溺愛小孩、部屬)。",
        "advice": "要多讚美傷官的獨特之處、認同他的感覺和情緒、讓他感受到你對他的支持。"
    }
}

EASTERN_MBTI_MAP = {
    "正官": {"code": "O", "title": "統籌官", "camp": "領航者陣營 (Leaders)", "color": "#1E3A8A", "bg": "#EFF6FF", "icon": "👔", "image": "images/officer.png", "desc": "講求紀律與秩序、善於組織管理與執行"},
    "七煞": {"code": "W", "title": "開拓者", "camp": "領航者陣營 (Leaders)", "color": "#1E3A8A", "bg": "#EFF6FF", "icon": "⚔️", "image": "images/warrior.png", "desc": "果斷有魄力、擅長破局與危機處理"},
    "正印": {"code": "G", "title": "守護者", "camp": "智囊團陣營 (Thinkers)", "color": "#065F46", "bg": "#ECFDF5", "icon": "🛡️", "image": "images/guardian.png", "desc": "溫和包容、重視和諧、自帶貴人磁場"},
    "偏印": {"code": "S", "title": "策略家", "camp": "智囊團陣營 (Thinkers)", "color": "#065F46", "bg": "#ECFDF5", "icon": "🔍", "image": "images/sage.png", "desc": "直覺敏銳、思路深邃、具極高專業天賦"},
    "傷官": {"code": "D", "title": "演說家", "camp": "創作者陣營 (Creators)", "color": "#EA580C", "bg": "#FFF7ED", "icon": "🎤", "image": "images/orator.png", "desc": "反應靈敏、口才極佳、具強烈顛覆與表現力"},
    "食神": {"code": "E", "title": "策劃師", "camp": "創作者陣營 (Creators)", "color": "#EA580C", "bg": "#FFF7ED", "icon": "🎨", "image": "images/planner.png", "desc": "樂觀隨和、注重品質、善於將創意融入生活"},
    "比肩": {"code": "A", "title": "實幹家", "camp": "實務家陣營 (Networkers)", "color": "#78350F", "bg": "#FEFCE8", "icon": "🤝", "image": "images/realist.png", "desc": "獨立有原則、腳踏實地、講求平等溝通"},
    "劫財": {"code": "C", "title": "談判家", "camp": "實務家陣營 (Networkers)", "color": "#78350F", "bg": "#FEFCE8", "icon": "⚡", "image": "images/catalyst.png", "desc": "靈活有魅力、鬼點子多、擅長人際突破"}
}

LIFE_NUMBERS_DB = {
    1: {
        "title": "數字1 - 開創數 | 獨立數",
        "positive": ["具領袖氣質", "獨立", "大方", "直覺力強", "勇往直前", "堅持到底", "有開創力", "具行動力", "自信心強", "先鋒"],
        "success": ["自治能力佳", "獨立性高", "可在陌生環境中找到適應的方法"],
        "negative": ["獨裁", "報復心強", "不易溝通", "浮躁", "自我", "愛吹噓", "目中無人", "不懂得如何與他人合作", "一意孤行", "自尊心強", "不易信任他人", "主觀性強", "博學卻不精"],
        "immature": ["固執自我", "猜忌心重", "無法獨立"]
    },
    2: {
        "title": "數字2 - 協調數 | 溝通數",
        "positive": ["體貼", "善於溝通", "外交能力強", "能看穿人的思想", "值得信賴", "清楚自己的能力範圍", "重細節", "能與人產生很好的合作關係", "最有女人味"],
        "success": ["對社會價值高度認同", "處事圓融", "外交及公關能力強", "想像力及創造力豐富"],
        "negative": ["敏感", "抗壓弱", "容易崩潰", "情緒起伏大", "意氣用事", "具雙重人格", "優柔寡斷", "依賴性強也強迫他人依賴", "過度幫忙又突然退縮", "對於不認同的事會當個破壞份子"],
        "immature": ["一味的以別人的看法為主", "無主見", "為反對而反對", "投機取巧(抄捷徑)"]
    },
    3: {
        "title": "數字3 - 創意數",
        "positive": ["創造力佳", "多樣式", "工作偏向藝術", "活潑", "外向", "經常激發別人", "關心別人", "善溝通", "具發明力", "好奇心強"],
        "success": ["目標設定明確", "工作能力強(機智、敏銳)", "意念越強，成功特質越強"],
        "negative": ["注意力不集中", "情緒起伏大", "任性", "沒耐心", "注重表面(不夠深入了解)", "憤世嫉俗(挑剔批判)", "焦躁不安", "推卸責任", "濫用職權", "博而不精"],
        "immature": ["溝通技巧弱，無法完整表達自己的主見", "容易跳脫思維，觀念不容易被採納", "無創意，追求及整合智慧的過程不夠熟練"]
    },
    4: {
        "title": "數字4 - 執著數 | 務實數",
        "positive": ["有始有終", "實際", "持續", "耐力強", "思考邏輯性", "講求效率", "信守承諾", "刻苦耐勞", "保守", "乖巧", "精打細算"],
        "success": ["重視本身責任", "有廣大的胸襟", "善於利用周邊資源"],
        "negative": ["獨斷獨行", "具暴力傾向(被逼到反彈)", "不易接受改變", "無安全感", "沒情調", "呆板(實際、務實、實在)"],
        "immature": ["無安全感", "強烈對基本物質的追求", "無責任感", "組織能力不夠"]
    },
    5: {
        "title": "數字5 - 自由數",
        "positive": ["熱情", "反應快", "競爭力強", "具吸引力", "友善", "觀察力敏銳", "多才多藝", "喜愛旅遊", "挑戰性強", "好奇心重", "頭腦好", "喜歡交朋友", "有正義感", "健談"],
        "success": ["善於交際", "維持廣泛的人際關係", "包容別人"],
        "negative": ["博而不精", "害怕親密關係", "怕束縛", "知己少", "雞婆性高", "會為了得到自己的需求而欺瞞"],
        "immature": ["對物質更深層的追求", "喜新厭舊", "為追求個人自由，犧牲他人的力量", "無法讓心智自由", "作繭自縛"]
    },
    6: {
        "title": "數字6 - 關懷數 | 志工數",
        "positive": ["激發靈感", "產生智慧", "有悲天憫人的胸懷", "設身處地的為人著想", "愛家", "感情豐富", "願意承擔責任", "完美主義", "服務他人", "不求回報"],
        "success": ["能做好風險管理", "對事敏銳(非敏感)"],
        "negative": ["情緒化", "忌妒心強", "佔有慾強", "愛批評別人", "易有被害妄想症(在事件中有受害者心態)"],
        "immature": ["對於犧牲自己，成就他人無法釋懷", "對不公平的犧牲，心智需要被人治療，無法自救", "愛別人勝於愛自己", "追求絕對的愛情觀"]
    },
    7: {
        "title": "數字7 - 協調數 | 真理數",
        "positive": ["喜好追求真理", "善給人意見", "誠實", "具自信心", "深思熟慮", "分析力強", "處事冷靜", "貴人多", "相信專家"],
        "success": ["喜歡幫助弱小", "不求回報", "相信數據", "對金錢渴望不高", "喜歡服務別人"],
        "negative": ["冷漠(過度理性)", "不接受別人批評", "反社交", "孤僻", "自卑或自大傲慢", "在真理上得不到答案時就會放縱自身慾望"],
        "immature": ["懷疑靈光與真理的可信度", "無法釐清思緒與缺乏分辨真假的能力", "無法掌握機運，錯失良機", "不相信別人", "封閉自我"]
    },
    8: {
        "title": "數字8 - 理財數 | 管理數",
        "positive": ["實際", "企圖心", "有組織力與分析能力", "聰明有成就大事業的領導特質", "管理能力強", "外柔內剛"],
        "success": ["思考能力強", "照計畫行事", "依據可靠資訊做決議"],
        "negative": ["高傲", "無情", "記仇", "急躁", "無道德觀", "容易過於擔憂", "無法忍受不同意見", "投機心大", "野心大", "攀附權貴", "不擇手段", "包容性低", "沒耐心", "膠著"],
        "immature": ["控制慾強", "自欺欺人，做事不切實際", "不誠實面對事件，推三阻四", "理想與現實落差太大，得過且過"]
    },
    9: {
        "title": "數字9 - 智慧數 | 慈悲數",
        "positive": ["人道精神", "心思廣大", "心靈導師", "悲天憫人的胸懷", "對神秘事物有興趣", "樂於分享快樂幸福", "責任感", "求知慾望", "善於計劃", "心太軟", "重信仰"],
        "success": ["做事有毅力", "不輕易放棄", "不怕挫折", "願意長時間工作", "不輕易妥協"],
        "negative": ["自私", "奉承", "具毀滅性(不能一直被打壓，否則會破壞)", "愛做白日夢", "空想", "沒有行動力", "愛哭(易受感動)", "不容易拒絕他人"],
        "immature": ["忽略物質，強調心靈層次", "常做白日夢", "對別人不誠實，汲汲於自身營利，損人利己", "無法追求深層的智慧"]
    }
}

# -------------------------------------------------------------
# 5. 模組化 Prompt 配置結構 (辰祐閣 專屬定義)
# -------------------------------------------------------------
THEME_CONFIGS = {
    "general": {
        "title": "🔮【辰祐閣數字易經】東方 MBTI 雙盤全方位解析報告",
        "role_desc": "「辰祐閣」首席命理顧問",
        "sections": [
            ("☀️【外顯人格】社會面具與人生理想 (`{solar_code}` {solar_title})", [
                ("外在形象", "外界對你的第一印象與【{solar_archetype}】行為標籤。"),
                ("人生夢想 (`+`格局)", "根據【{solar_pattern}】，剖析陽曆顯性人生追求與理想抱負。"),
                ("外在情緒障礙 (`-`黑洞)", "當情緒來時，【{solar_blackhole}】如何影響人事物並造成阻礙。")
            ]),
            ("🌙【內在人格】潛意識與靈魂渴望 (`{lunar_code}` {lunar_title})", [
                ("靈魂渴望 (`+`格局)", "根據【{lunar_pattern}】，剖析陰曆深處最渴望實現的真實自我。"),
                ("內在情緒地雷 (`-`黑洞)", "當情緒波動時，【{lunar_blackhole}】如何干擾內在安全感。")
            ]),
            ("☯️【雙盤共振】內外碰撞與能量交互", [
                ("MBTI 組合效應", "陽曆外顯【{solar_title}】與陰曆內在【{lunar_title}】是相互加持還是內外拉扯。"),
                ("情緒阻礙衝突", "當內外黑洞爆發時的情緒內耗與行為矛盾。"),
                ("調和關鍵", "讓外顯面具與內在人格達成平衡的具體心法。")
            ]),
            ("💡【落地指南】辰祐閣升級心法", [
                ("天賦發揮策略", "充分發揮 `{solar_code}` 能量特質的實用方法。"),
                ("情緒修煉指南", "化解 `-先天黑洞` 情緒影響人事物的解套法門。"),
                ("最佳拍檔指引", "職場與生活中最適合合作的東方 MBTI 類型。")
            ])
        ]
    },
    "love": {
        "title": "❤️【辰祐閣數字易經】感情與姻緣專項深度報告",
        "role_desc": "「辰祐閣」情感命理專家",
        "sections": [
            ("💘【戀愛模式】心動密碼與感情理想", [
                ("吸引力特質", "身為【{solar_title}】，你在異性眼中最具魅力的亮點。"),
                ("感情理想 (`+`格局)", "你在親密關係中最想追求與實現的相處狀態。"),
                ("理想對象條件", "最能吸引你且長久相處的人格類型。")
            ]),
            ("💣【親密地雷】情緒黑洞與相處卡點", [
                ("情緒阻礙 (`-`黑洞)", "當情緒上頭時，【{solar_blackhole}】如何影響與伴侶的相處。"),
                ("情緒盲點", "不安感強烈時容易產生的行為（如控制、退縮、猜忌）。"),
                ("避坑提醒", "戀愛中需要刻意提醒自己的不健康心態。")
            ]),
            ("🌹【幸福指南】辰祐閣姻緣調和心法", [
                ("溝通修煉", "適合你的伴侶溝通與化解衝突方式。"),
                ("關係維持", "讓感情長久保鮮的具體行動。"),
                ("擇偶指南", "避開相剋性格對象的篩選標準。")
            ])
        ]
    },
    "career": {
        "title": "💼【辰祐閣數字易經】事業發展與財富變現專項報告",
        "role_desc": "「辰祐閣」商業財富顧問",
        "sections": [
            ("🚀【職場定位】天賦優勢與事業夢想", [
                ("核心天賦", "身為【{solar_title}】，你在職場上最難被取代的能力。"),
                ("事業夢想 (`+`格局)", "你在工作中最渴望實現的抱負與理想定位。"),
                ("團隊合作模式", "與上司、下屬或合夥人的最佳互動方式。")
            ]),
            ("💰【生財磁場】180度變現途徑與商業模式", [
                ("主要財富來源", "最能幫你創造財富的業務或商業型態（180度能量：【{solar_wealth}】）。"),
                ("適合商業模式", "適合獨資創業、企業內升遷、技術授權還是合夥經營。"),
                ("貴人財運關鍵", "如何引動你的 180 度生財貴人磁場。")
            ]),
            ("🔓【破局關鍵】解鎖90度黑洞與財富卡點", [
                ("情緒阻礙與漏財破口", "當情緒爆發時，90度黑洞【{solar_blackhole}】如何影響職場人事物。"),
                ("事業發展瓶頸", "限制你收入與事業突破上限的主要障礙。"),
                ("落地破局心法", "3 點解開財富鎖鏈並實現事業夢想的落地建議。")
            ])
        ]
    }
}

def generate_prompt(solar_res: dict, lunar_res: dict, solar_mbti: dict, lunar_mbti: dict, theme_key: str = "general") -> str:
    config = THEME_CONFIGS.get(theme_key, THEME_CONFIGS["general"])
    solar_geo = solar_res.get('geometry', {})
    lunar_geo = lunar_res.get('geometry', {}) if lunar_res else {}

    format_dict = {
        "solar_code": solar_mbti['code'],
        "solar_title": solar_mbti['title'],
        "solar_camp": solar_mbti['camp'],
        "solar_archetype": solar_mbti['archetype'],
        "solar_pattern": solar_geo.get('core_pattern', '無'),
        "solar_blackhole": ', '.join(solar_geo.get('mental_blackhole', ['無'])),
        "solar_wealth": solar_geo.get('wealth_energy', '無'),
        "lunar_code": lunar_mbti['code'],
        "lunar_title": lunar_mbti['title'],
        "lunar_camp": lunar_mbti['camp'],
        "lunar_archetype": lunar_mbti['archetype'],
        "lunar_pattern": lunar_geo.get('core_pattern', '無'),
        "lunar_blackhole": ', '.join(lunar_geo.get('mental_blackhole', ['無'])),
        "lunar_wealth": lunar_geo.get('wealth_energy', '無'),
    }

    body_sections = []
    for section_title_template, items in config["sections"]:
        sec_title = section_title_template.format(**format_dict)
        item_lines = []
        for label, desc_template in items:
            desc = desc_template.format(**format_dict)
            item_lines.append(f"* **【{label}】**：{desc}")
        body_sections.append(f"### {sec_title}\n" + "\n".join(item_lines))

    prompt = f"""
【系統最高優先指令】：
1. 全程使用繁體中文（台灣）。
2. 絕對禁止輸出任何英文開場白或翻譯。
3. 嚴格採用「重點條列 (Bullet Points)」與「關鍵字加粗 (**...**)`」排版！
4. 絕對不要使用「第幾章」作為標題，直接使用指定的主題標題！

【東方 MBTI 角色數據】：
- ☀️ 陽曆（外顯人格）：{solar_mbti['code']} {solar_mbti['title']} ({solar_mbti['camp']})
- 🌙 陰曆（內在人格）：{lunar_mbti['code']} {lunar_mbti['title']} ({lunar_mbti['camp']})

【辰祐閣核心定義】：
- `+格局`：代表「來到人世間的夢想與理想」。
- `-先天黑洞 (90度)`：代表「當情緒爆發時影響人事物、阻礙理想」的核心卡點。

---

你是{config['role_desc']}。請根據求測者數據，生成一份條列式解析報告：

# {config['title']}

---

""" + "\n\n---\n\n".join(body_sections)

    return prompt

# -------------------------------------------------------------
# 6. 精細化 API 呼叫模組 (固定鎖定 gemini-3.5-flash-lite)
# -------------------------------------------------------------
def call_model(api_key: str, prompt_content: str) -> str:
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("尚未設定有效的 API Key！")

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    payload = {
        "contents": [{"parts": [{"text": prompt_content}]}],
        "generationConfig": {
            "maxOutputTokens": 4096
        }
    }

    # 優先使用低延遲模型；遇到暫時性 503 時重試，再切換備援模型。
    model_plan = [
        ("gemini-3.5-flash-lite", 2),
        ("gemini-3.5-flash", 1)
    ]
    last_service_message = ""

    for model_name, max_attempts in model_plan:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"

        for attempt in range(max_attempts):
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=(10, 120))
            except requests.exceptions.Timeout:
                raise TimeoutError("AI 報告生成時間超過 120 秒，請稍後重新嘗試。")
            except requests.exceptions.ConnectionError:
                raise ConnectionError("無法連線至 Google API 伺服器，請檢查網路連線。")
            except requests.exceptions.RequestException as req_err:
                raise RuntimeError(f"網路請求發生異常：{str(req_err)}")

            try:
                res_data = res.json()
            except ValueError:
                raise ValueError(f"API 回傳非標準 JSON 格式（HTTP {res.status_code}）：{res.text}")

            if res.status_code == 200 and "error" not in res_data:
                candidates = res_data.get("candidates", [])
                try:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"]
                    raise KeyError("API 回傳資料結構中缺少文字內容。")
                except (KeyError, IndexError, TypeError) as parse_err:
                    raise ValueError(f"解析 API 回傳內容時發生錯誤：{str(parse_err)}")

            err_info = res_data.get("error", {})
            err_code = err_info.get("code", res.status_code)
            err_msg = err_info.get("message", res.text)

            if err_code == 503:
                last_service_message = err_msg
                if attempt + 1 < max_attempts:
                    time.sleep(2 ** attempt)
                continue

            if err_code == 401:
                raise PermissionError(
                    "Gemini API 拒絕目前的憑證。請確認 Streamlit Secrets 的 GEMINI_API_KEY "
                    "是從 Google AI Studio API Keys 頁面新建立的 Gemini Auth API Key，"
                    "不是 OAuth Token、Service Account 憑證或其他 Google Cloud 金鑰。"
                )

            if "RESOURCE_EXHAUSTED" in err_msg or "Quota exceeded" in err_msg:
                raise ResourceWarning("系統用量已達額度上限，請稍後再重新生成。")

            raise RuntimeError(f"Google API 錯誤 [狀態碼 {err_code}]：{err_msg}")

    raise RuntimeError(
        "Google AI 目前服務繁忙，系統已自動重試並切換備援模型，但仍未成功。"
        "請等待一至兩分鐘後再試。"
        + (f"（服務訊息：{last_service_message}）" if last_service_message else "")
    )

# -------------------------------------------------------------
# 7. 排盤邏輯與幾何角度分析引擎 (90度 & 180度)
# -------------------------------------------------------------
STAR_MAP = {
    '11': ('比肩', '最強'), '22': ('比肩', '最強'), '88': ('比肩', '強'), '99': ('比肩', '強'),
    '66': ('比肩', '次強'), '77': ('比肩', '次強'), '33': ('比肩', '弱'), '44': ('比肩', '弱'),
    '14': ('正印', '最強'), '41': ('正印', '最強'), '67': ('正印', '強'), '76': ('正印', '強'),
    '39': ('正印', '次強'), '93': ('正印', '次強'), '28': ('正印', '弱'), '82': ('正印', '弱'),
    '13': ('食神', '最強'), '31': ('食神', '最強'), '68': ('食神', '強'), '86': ('食神', '強'),
    '49': ('食神', '次強'), '94': ('食神', '次強'), '27': ('食神', '弱'), '72': ('食神', '弱'),
    '19': ('正官', '最強'), '91': ('正官', '最強'), '78': ('正官', '強'), '87': ('正官', '強'),
    '34': ('正官', '次強'), '43': ('正官', '次強'), '26': ('正官', '弱'), '62': ('正官', '弱'),
    '17': ('七煞', '最強'), '71': ('七煞', '最強'), '89': ('七煞', '強'), '98': ('七煞', '強'),
    '46': ('七煞', '次強'), '64': ('七煞', '次強'), '23': ('七煞', '弱'), '32': ('七煞', '弱'),
    '16': ('偏印', '最強'), '61': ('偏印', '最強'), '47': ('偏印', '強'), '74': ('偏印', '強'),
    '38': ('偏印', '次強'), '83': ('偏印', '次強'), '29': ('偏印', '弱'), '92': ('偏印', '弱'),
    '12': ('傷官', '最強'), '21': ('傷官', '最強'), '69': ('傷官', '強'), '96': ('傷官', '強'),
    '48': ('傷官', '次強'), '84': ('傷官', '次強'), '37': ('傷官', '弱'), '73': ('傷官', '弱'),
    '18': ('劫財', '最強'), '81': ('劫財', '最強'), '97': ('劫財', '強'), '79': ('劫財', '強'),
    '36': ('劫財', '次強'), '63': ('劫財', '次強'), '24': ('劫財', '弱'), '42': ('劫財', '弱'),
}

COMPOUND_PATTERN_MAP = {
    19: "正官格", 28: "比肩格", 29: "比肩格",
    37: "傷官格", 38: "比肩格", 39: "傷官格",
    46: "七煞格", 47: "比肩格", 48: "傷官格"
}

TOP_ROW_STARS = {"比肩", "正印", "食神", "正官"}
BOTTOM_ROW_STARS = {"七煞", "偏印", "傷官", "劫財"}
HIDDEN_ENERGY_MAP = {
    "正官": "七煞", "正印": "偏印", "比肩": "劫財", "食神": "劫財",
    "七煞": "正官", "偏印": "正印", "劫財": "食神", "傷官": "食神"
}

def process_digits_and_pairs(year: int, month: int, day: int):
    year_s, month_s, day_s = str(abs(year)), str(abs(month)), str(abs(day))
    raw_seq = f"{year_s}{month_s}{day_s}"
    pairs_info = []
    n = len(raw_seq)
    i = 0
    
    while i < n - 1:
        current_char = raw_seq[i]
        if current_char == '5':
            pair = f"5{raw_seq[i+1]}"
            pairs_info.append({"pair": pair, "star": "比肩", "strength": "強", "is_infinite": False})
            i += 1
            continue

        if raw_seq[i+1] == '5':
            j = i + 1
            while j < n and raw_seq[j] == '5': j += 1
            prev_d = current_char
            if prev_d != '0' and j < n and raw_seq[j] != '0':
                next_d = raw_seq[j]
                target_pair = prev_d + next_d
                star_name, strength = STAR_MAP.get(target_pair, (None, None))
                fives_str = raw_seq[i+1:j]
                if star_name:
                    pairs_info.append({"pair": f"{prev_d}{fives_str}{next_d}➔{target_pair}", "star": star_name, "strength": strength, "is_infinite": True})
                i = j
                continue
            else:
                pairs_info.append({"pair": f"{current_char}5", "star": "比肩", "strength": "強", "is_infinite": False})
                i += 1
                continue

        pair = raw_seq[i:i+2]
        star_name, strength = ("比肩", "強") if '0' in pair else STAR_MAP.get(pair, (None, None))
        if star_name:
            pairs_info.append({"pair": pair, "star": "比肩", "strength": strength, "is_infinite": False})
        i += 1

    return raw_seq, pairs_info

def calculate_destiny_chart(year: int, month: int, day: int):
    raw_seq, pairs_info = process_digits_and_pairs(year, month, day)
    full_digits = [int(ch) for ch in raw_seq if ch.isdigit()]
    pattern_num = sum(full_digits)
    
    goal_num = pattern_num
    while goal_num >= 10:
        goal_num = sum(int(c) for c in str(goal_num))
        
    if pattern_num in COMPOUND_PATTERN_MAP:
        pattern_name = COMPOUND_PATTERN_MAP[pattern_num]
    else:
        p_pair = str(pattern_num)
        star = STAR_MAP.get(p_pair, ("比肩", "普通"))[0]
        pattern_name = f"{star}格"

    core_pattern_star = pattern_name.replace("格", "")

    star_counts = {}
    star_has_infinite = {}
    for p in pairs_info:
        s_name = p['star']
        star_counts[s_name] = star_counts.get(s_name, 0) + 1
        if p['is_infinite']: star_has_infinite[s_name] = True

    processed_stars = []
    visited = set()
    for p in pairs_info:
        s_name = p['star']
        if s_name in visited: continue
        visited.add(s_name)
        count = star_counts[s_name]
        mark = "∞" if star_has_infinite.get(s_name, False) else (str(count) if count > 1 else "")
        processed_stars.append({
            "name": s_name, "top_char": s_name[0] if len(s_name) > 0 else "",
            "bottom_char": s_name[1] if len(s_name) > 1 else "", "mark": mark, "is_hidden": False
        })

    top_stars = [s for s in processed_stars if s['name'] in TOP_ROW_STARS]
    bottom_stars = [s for s in processed_stars if s['name'] in BOTTOM_ROW_STARS]
    
    num_cols = max(len(top_stars), len(bottom_stars))
    if num_cols == 0: num_cols = 1
    
    matrix_top = [None] * num_cols
    matrix_bottom = [None] * num_cols

    for t_idx, star in enumerate(top_stars):
        if t_idx < num_cols: matrix_top[t_idx] = star
    for b_idx, star in enumerate(bottom_stars):
        if b_idx < num_cols: matrix_bottom[b_idx] = star

    for c in range(num_cols):
        if matrix_top[c] is not None and matrix_bottom[c] is None:
            hidden_name = HIDDEN_ENERGY_MAP.get(matrix_top[c]['name'], "")
            if hidden_name:
                matrix_bottom[c] = {"name": hidden_name, "top_char": hidden_name[0], "bottom_char": hidden_name[1], "mark": "x", "is_hidden": True}
        elif matrix_bottom[c] is not None and matrix_top[c] is None:
            hidden_name = HIDDEN_ENERGY_MAP.get(matrix_bottom[c]['name'], "")
            if hidden_name:
                matrix_top[c] = {"name": hidden_name, "top_char": hidden_name[0], "bottom_char": hidden_name[1], "mark": "x", "is_hidden": True}

    grid_2d = [matrix_top, matrix_bottom]
    core_r, core_c = -1, -1
    core_item = None
    has_exact_pattern_star = False

    for r in range(2):
        for c in range(num_cols):
            item = grid_2d[r][c]
            if item and item['name'] == core_pattern_star and not item.get('is_hidden', False):
                core_r, core_c, core_item, has_exact_pattern_star = r, c, item, True
                break
        if core_r != -1: break

    if not has_exact_pattern_star:
        pattern_name = f"{pattern_name}-未入格"
        fallback_star_name = None
        for p in reversed(pairs_info):
            if p.get('star'):
                fallback_star_name = p['star']
                break
        
        if fallback_star_name:
            for r in range(2):
                for c in range(num_cols):
                    item = grid_2d[r][c]
                    if item and item['name'] == fallback_star_name and not item.get('is_hidden', False):
                        core_r, core_c, core_item = r, c, item
                        break
                if core_r != -1: break

    pattern_layout_tuples = []
    geometry_dict = {
        "core_pattern": "",
        "mental_blackhole": [],
        "wealth_energy": "",
        "wealth_blackhole": []
    }

    if core_item and core_r != -1:
        opp_r = 1 if core_r == 0 else 0
        
        geometry_dict["core_pattern"] = f"{core_item['name']}{core_item['mark']}"
        pattern_layout_tuples.append(("+", geometry_dict["core_pattern"]))

        opp_side_items = [grid_2d[opp_r][c]['name'] + grid_2d[opp_r][c]['mark'] for c in (core_c - 1, core_c + 1) if 0 <= c < num_cols and grid_2d[opp_r][c]]
        if opp_side_items:
            geometry_dict["mental_blackhole"] = opp_side_items
            pattern_layout_tuples.append(("-", " ".join(opp_side_items)))

        opp_item = grid_2d[opp_r][core_c]
        if opp_item:
            geometry_dict["wealth_energy"] = f"{opp_item['name']}{opp_item['mark']}"
            pattern_layout_tuples.append(("+", geometry_dict["wealth_energy"]))

        same_side_items = [grid_2d[core_r][c]['name'] + grid_2d[core_r][c]['mark'] for c in (core_c - 1, core_c + 1) if 0 <= c < num_cols and grid_2d[core_r][c]]
        if same_side_items:
            geometry_dict["wealth_blackhole"] = same_side_items
            pattern_layout_tuples.append(("-", " ".join(same_side_items)))

    clean_top = [item for item in matrix_top if item is not None]
    clean_bottom = [item for item in matrix_bottom if item is not None]

    return {
        "raw_seq": raw_seq,
        "pattern_num": pattern_num,
        "goal_num": f"{goal_num}號人",
        "pattern_name": pattern_name,
        "core_item": core_item,
        "matrix_top": clean_top,
        "matrix_bottom": clean_bottom,
        "pairs_info": pairs_info,
        "pattern_layout_tuples": pattern_layout_tuples,
        "geometry": geometry_dict
    }

# -------------------------------------------------------------
# 8. 東方 MBTI 代碼與角色計算器 (含安全圖片與文字跳脫)
# -------------------------------------------------------------
def get_character_img_tag(img_rel_path: str, fallback_icon: str) -> str:
    if img_rel_path and os.path.exists(img_rel_path):
        try:
            with open(img_rel_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{b64}" style="width:110px; height:110px; object-fit:contain; margin:8px auto; display:block; border-radius:12px;" />'
        except Exception:
            pass
    clean_icon = html.escape(fallback_icon)
    return f'<div style="font-size:48px; margin:8px 0;">{clean_icon}</div>'

def get_eastern_mbti_info(res: dict, prefix: str = "S") -> dict:
    if not res:
        return {
            "code": "N/A", "title": "未知角色", "archetype": "未知",
            "digit": "?", "modifier": "+", "desc": "",
            "camp": "未知陣營", "color": "#8C1C1C", "bg": "#F8F5EE", "icon": "🔮", "img_tag": "🔮"
        }
    
    raw_pattern = res.get('pattern_name', '比肩格')
    clean_star = raw_pattern.replace("格", "").replace("-未入格", "")
    
    mbti_data = EASTERN_MBTI_MAP.get(clean_star, {
        "code": "A", "title": "實幹家", "camp": "實務家陣營",
        "color": "#78350F", "bg": "#FEFCE8", "icon": "🤝", "image": "images/realist.png", "desc": "獨立腳踏實地"
    })
    
    goal_str = res.get('goal_num', '1號人')
    match = re.search(r'\d+', goal_str)
    goal_digit = match.group() if match else "1"
    
    modifier = "-" if "-未入格" in raw_pattern else "+"
    
    full_code = f"{prefix}-{mbti_data['code']}{goal_digit}{modifier}"
    full_title = f"【 {goal_digit}號 {mbti_data['title']} 】"
    img_tag = get_character_img_tag(mbti_data.get('image', ''), mbti_data.get('icon', '🔮'))
    
    return {
        "code": full_code,
        "title": full_title,
        "archetype": mbti_data['title'],
        "digit": goal_digit,
        "modifier": modifier,
        "desc": mbti_data['desc'],
        "camp": mbti_data['camp'],
        "color": mbti_data['color'],
        "bg": mbti_data['bg'],
        "icon": mbti_data['icon'],
        "img_tag": img_tag
    }

# -------------------------------------------------------------
# 9. UI 渲染模組
# -------------------------------------------------------------
def build_star_box_html(item: dict, core_item: dict) -> str:
    if not item: return ''
    is_core = (core_item is not None and item == core_item)
    box_class = "star-box-core" if is_core else "star-box"
    mark_text = html.escape(str(item.get("mark", "")))
    mark_html = f'<div class="star-mark">{mark_text}</div>' if mark_text else ''
    top_c = html.escape(str(item.get("top_char", "")))
    bot_c = html.escape(str(item.get("bottom_char", "")))
    return f'<div class="{box_class}">{mark_html}<div class="star-top">{top_c}</div><div class="star-bottom">{bot_c}</div></div>'

def render_panel(res: dict, title_prefix: str, date_desc: str, tone: str = "solar"):
    """只負責結果視覺呈現；所有命理數值沿用 calculate_destiny_chart 的輸出。"""
    core_item = res['core_item']
    top_boxes_html = "".join([build_star_box_html(item, core_item) for item in res['matrix_top']])
    bottom_boxes_html = "".join([build_star_box_html(item, core_item) for item in res['matrix_bottom']])

    pattern_str = res['pattern_name']
    is_bound = "-未入格" not in pattern_str
    pattern_main = html.escape(pattern_str.replace("-未入格", ""))
    badge_html = (
        '<span class="status-badge status-bound">已入格</span>'
        if is_bound else '<span class="status-badge status-unbound">未入格</span>'
    )

    layout_tokens = []
    for sign, content in res['pattern_layout_tuples']:
        layout_tokens.append(
            f'<span class="energy-token">{html.escape(str(sign))} {html.escape(str(content))}</span>'
        )
    layout_content = "".join(layout_tokens) or "<span style='color:#8A7C70;'>尚無能量排列組合</span>"

    goal_match = re.search(r'\d+', str(res['goal_num']))
    goal_digit = goal_match.group() if goal_match else "—"
    pair_count = len(res['pairs_info'])
    infinite_count = sum(1 for item in res['pairs_info'] if item.get('is_infinite'))
    matrix_count = len(res['matrix_top']) + len(res['matrix_bottom'])
    energy_count = len(res['pattern_layout_tuples'])

    detail_text = f"{date_desc}\n"
    detail_text += f"【處理後數字串】: {res['raw_seq']}\n"
    detail_text += f"【格局數】: {res['pattern_num']}  ｜  【目標數】: {res['goal_num']}  ｜  【格局】: {res['pattern_name']}\n"
    detail_text += "────────────────────────────────────────\n"
    detail_text += "【兩兩拆解與歸類詳情】:\n"
    for p in res['pairs_info']:
        inf_tag = " [無限大 ∞]" if p['is_infinite'] else ""
        detail_text += f"  • 組合 [{p['pair']}] ➔ {p['star']} ({p['strength']}){inf_tag}\n"

    card_class = "destiny-card lunar" if tone == "lunar" else "destiny-card"
    tone_label = "LUNAR · INNER" if tone == "lunar" else "SOLAR · OUTER"
    card_html = (
        f'<div class="{card_class}">'
        f'<div class="destiny-card-head"><div>'
        f'<div class="destiny-eyebrow">{tone_label}</div>'
        f'<div class="destiny-title">{html.escape(title_prefix)}</div>'
        f'<div class="destiny-date">{html.escape(date_desc)}</div>'
        f'</div><div class="life-seal"><span>生命數</span><strong>{goal_digit}</strong></div></div>'
        f'<div class="formula-strip"><div class="formula-label">數字演算軌跡</div>'
        f'<div class="formula-value">{html.escape(str(res["raw_seq"]))} → 格局 {res["pattern_num"]} → {html.escape(res["goal_num"])}</div></div>'
        f'<div class="stat-grid">'
        f'<div class="stat-chip"><b>{goal_digit}</b><span>目標數</span></div>'
        f'<div class="stat-chip"><b>{res["pattern_num"]}</b><span>格局數</span></div>'
        f'<div class="stat-chip"><b>{pair_count}</b><span>神煞組合</span></div>'
        f'<div class="stat-chip"><b>{matrix_count}</b><span>矩陣節點</span></div>'
        f'<div class="stat-chip"><b>{energy_count}</b><span>能量排列</span></div>'
        f'</div>'
        f'<div class="result-section-label">命格摘要</div>'
        f'<div class="pattern-row"><span class="pattern-name">{pattern_main}</span>{badge_html}</div>'
        f'<div class="result-section-label">神煞排盤矩陣</div>'
        f'<div class="matrix-row">{top_boxes_html}</div>'
        f'<hr style="border:none;border-top:1px dashed #D5C8B7;margin:8px 0;">'
        f'<div class="matrix-row">{bottom_boxes_html}</div>'
        f'<div class="result-section-label">格局能量排列</div>'
        f'<div class="energy-list">{layout_content}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    with st.expander(f"展開 {title_prefix} 詳細計算解析"):
        st.markdown(
            f'<div class="tk-text-area">{html.escape(detail_text)}</div>',
            unsafe_allow_html=True
        )

# -------------------------------------------------------------
# 10. 頁面渲染與專項報告調用主邏輯
# -------------------------------------------------------------

if st.session_state.page == 'main':
    # 商業版品牌首屏：先說明價值，再引導免費排盤
    st.markdown(
        """
        <div class="commerce-shell">
            <div class="commerce-nav">
                <div class="commerce-brand">
                    <div class="commerce-seal">辰</div>
                    <div>
                        <div class="commerce-brand-name">辰 祐 閣</div>
                        <div class="commerce-brand-en">EASTERN NUMEROLOGY STUDIO</div>
                    </div>
                </div>
                <div class="commerce-nav-note">雙曆人格分析・測試體驗版</div>
            </div>
            <section class="commerce-hero">
                <div class="commerce-kicker">以數觀心・照見內外人格</div>
                <div class="commerce-title">從出生數字，看見你的<br><em>外在行動與內在天賦</em></div>
                <div class="commerce-lead">以陽曆理解你面對世界的方式，以陰曆梳理內在需求；結合生命數與神煞格局，把複雜命盤整理成可以閱讀、理解與實踐的人生線索。</div>
                <div class="commerce-pills">
                    <span class="commerce-pill">☀ 陽曆外顯人格</span>
                    <span class="commerce-pill">☾ 陰曆內在人格</span>
                    <span class="commerce-pill">◇ 生命數字</span>
                    <span class="commerce-pill">⌁ 神煞格局</span>
                </div>
            </section>
            <div class="value-grid">
                <div class="value-card"><div class="value-index">壹</div><div class="value-title">輸入生日</div><div class="value-copy">以單一日期完成陽曆與陰曆雙盤換算。</div></div>
                <div class="value-card"><div class="value-index">貳</div><div class="value-title">讀懂雙重人格</div><div class="value-copy">先看外在行動，再理解內在節奏與需求。</div></div>
                <div class="value-card"><div class="value-index">參</div><div class="value-title">轉化為行動</div><div class="value-copy">從優勢、盲點到關係與職涯，找到下一步。</div></div>
            </div>
            <div class="entry-heading">
                <small>FREE DUAL-CHART READING</small>
                <h2>開始免費雙曆排盤</h2>
                <p>輸入陽曆生日，即時取得基礎人格與命盤摘要</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("birth_form"):
        col_y, col_m, col_d = st.columns([1.2, 1, 1])
        with col_y:
            year = st.number_input("陽曆西元年", min_value=1900, max_value=2100, value=2000, step=1, key="input_year")
        with col_m:
            month = st.number_input("月", min_value=1, max_value=12, value=1, step=1, key="input_month")
        with col_d:
            day = st.number_input("日", min_value=1, max_value=31, value=1, step=1, key="input_day")
        
        submit_btn = st.form_submit_button("一 鍵 自 動 排 盤", on_click=clear_report_cache)

    st.markdown(
        '<div class="privacy-note"><span>◌</span><span>生日僅用於本次排盤；測試版不建立個人會員檔案</span></div>',
        unsafe_allow_html=True
    )

    try:
        validated_date = datetime.date(year, month, day)
    except ValueError:
        st.error(f"⚠️ 輸入的日期無效：陽曆 {year} 年 {month} 月沒有第 {day} 天，請檢查後重新輸入！")
        st.stop()

    solar_res = calculate_destiny_chart(year, month, day)
    st.session_state.current_res = solar_res

    try:
        solar_obj = Solar.fromYmd(year, month, day)
        lunar_obj = solar_obj.getLunar()
        ly, lm, ld = lunar_obj.getYear(), lunar_obj.getMonth(), lunar_obj.getDay()
        is_leap = "閏" if lm < 0 else ""
        lunar_res = calculate_destiny_chart(ly, abs(lm), ld)
        st.session_state.current_lunar_res = lunar_res
        lunar_desc = f"【自動轉換陰曆】: {ly}年{is_leap}{abs(lm)}月{ld}日 (對應陽曆 {year}/{month}/{day})"
    except Exception as e:
        lunar_res = None
        st.session_state.current_lunar_res = None
        lunar_desc = f"⚠️ 日期轉換失敗: {e}"

    st.markdown(
        f"""
        <div class="result-overview">
            <div class="overview-kicker">CHEN YOU GE · DUAL CHART</div>
            <div class="overview-title">雙曆命盤總覽</div>
            <div class="overview-copy">一個生日，映照兩種觀看自己的角度。朱砂標記外顯行動，霧藍收納內在節奏，讓關鍵數字先被看見，再循線閱讀細節。</div>
            <div class="overview-dates">
                <span class="overview-date">陽曆｜{year} 年 {month} 月 {day} 日</span>
                <span class="overview-date">陰曆｜{ly if lunar_res else "—"} 年 {is_leap + str(abs(lm)) if lunar_res else "—"} 月 {ld if lunar_res else "—"} 日</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    solar_col, lunar_col = st.columns(2, gap="medium")
    with solar_col:
        render_panel(
            solar_res,
            "陽曆・外顯命盤",
            f"{year} 年 {month} 月 {day} 日",
            tone="solar"
        )
    with lunar_col:
        if lunar_res:
            render_panel(
                lunar_res,
                "陰曆・內在命盤",
                f"{ly} 年 {is_leap}{abs(lm)} 月 {ld} 日",
                tone="lunar"
            )
        else:
            st.error(lunar_desc)

    st.markdown(
        """
        <div class="insight-intro">
            <strong>免費雙盤摘要已完成</strong>
            <span>先理解命盤輪廓，再進一步探索關係、天賦與成長策略</span>
        </div>
        <section class="premium-preview">
            <div class="premium-kicker">COMPLETE INSIGHT PREVIEW</div>
            <div class="premium-title">完整雙盤深度解析</div>
            <div class="premium-copy">商業版將把命盤轉譯成容易實踐的個人指南。現階段可先免費體驗完整分析流程，付款與會員功能將於下一階段接入。</div>
            <div class="premium-grid">
                <div class="premium-item"><b>人格優勢</b><span>看見自然天賦與可放大的能力</span></div>
                <div class="premium-item"><b>盲點課題</b><span>辨識壓力下容易重複的模式</span></div>
                <div class="premium-item"><b>感情互動</b><span>理解安全感與關係溝通方式</span></div>
                <div class="premium-item"><b>事業財富</b><span>整理適合的工作與決策方向</span></div>
            </div>
            <div class="test-badge">測試版・目前不收費</div>
        </section>
        """,
        unsafe_allow_html=True
    )
    st.button("查看完整雙盤深度解析（測試體驗）", on_click=lambda: switch_page('analysis'), use_container_width=True, key="btn_unlock_report")

elif st.session_state.page == 'analysis':
    st.button("⬅️ 返回排盤主頁", on_click=lambda: switch_page('main'), key="btn_back_to_main")
    
    solar_res = st.session_state.get('current_res', None)
    lunar_res = st.session_state.get('current_lunar_res', None)

    if solar_res:
        solar_mbti = get_eastern_mbti_info(solar_res, prefix="S")
        lunar_mbti = get_eastern_mbti_info(lunar_res, prefix="L")

        solar_goal_int = int(re.search(r'\d+', solar_res['goal_num']).group())
        solar_num_info = LIFE_NUMBERS_DB.get(solar_goal_int, {})

        lunar_num_info = {}
        if lunar_res:
            lunar_goal_int = int(re.search(r'\d+', lunar_res['goal_num']).group())
            lunar_num_info = LIFE_NUMBERS_DB.get(lunar_goal_int, {})

        # 🔮 辰祐閣 東方 MBTI 視覺形象卡片
        st.markdown(f"""
        <div style="background:#FFFFFF; border:2px solid #8C1C1C; border-radius:18px; padding:20px; margin-bottom:24px; box-shadow:0 8px 25px rgba(140,28,28,0.08); box-sizing:border-box;">
            <div style="color:#8C1C1C; font-size:22px; font-weight:800; text-align:center; margin-bottom:18px; letter-spacing:2px;">🔮 辰祐閣 ‧ 東方 MBTI 性格卡片</div>
            <div style="display:flex; flex-wrap:wrap; justify-content:space-around; gap:16px;">
                <!-- 陽曆外顯人格卡 -->
                <div style="flex:1; min-width:240px; background:{solar_mbti['bg']}; border:1.5px solid {solar_mbti['color']}; border-radius:14px; padding:18px; text-align:center; box-sizing:border-box;">
                    <div style="font-size:12px; font-weight:700; color:{solar_mbti['color']}; text-transform:uppercase; letter-spacing:1px;">☀️ 陽曆外顯人格 ‧ {html.escape(solar_mbti['camp'])}</div>
                    <div style="margin:6px 0;">{solar_mbti['img_tag']}</div>
                    <div style="background:{solar_mbti['color']}; color:#FFFFFF; padding:4px 14px; border-radius:20px; font-weight:800; font-size:15px; display:inline-block; margin-bottom:8px;">{html.escape(solar_mbti['code'])}</div>
                    <div style="font-size:19px; font-weight:800; color:#1A1A1A; margin-bottom:6px;">{html.escape(solar_mbti['title'])}</div>
                    <div style="font-size:13px; color:#4A4A4A; line-height:1.5;">{html.escape(solar_mbti['desc'])}</div>
                </div>
                <!-- 陰曆內在人格卡 -->
                <div style="flex:1; min-width:240px; background:{lunar_mbti['bg']}; border:1.5px solid {lunar_mbti['color']}; border-radius:14px; padding:18px; text-align:center; box-sizing:border-box;">
                    <div style="font-size:12px; font-weight:700; color:{lunar_mbti['color']}; text-transform:uppercase; letter-spacing:1px;">🌙 陰曆內在人格 ‧ {html.escape(lunar_mbti['camp'])}</div>
                    <div style="margin:6px 0;">{lunar_mbti['img_tag']}</div>
                    <div style="background:{lunar_mbti['color']}; color:#FFFFFF; padding:4px 14px; border-radius:20px; font-weight:800; font-size:15px; display:inline-block; margin-bottom:8px;">{html.escape(lunar_mbti['code'])}</div>
                    <div style="font-size:19px; font-weight:800; color:#1A1A1A; margin-bottom:6px;">{html.escape(lunar_mbti['title'])}</div>
                    <div style="font-size:13px; color:#4A4A4A; line-height:1.5;">{html.escape(lunar_mbti['desc'])}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align:center; color:#8C1C1C; margin-top:15px;'>🎯 雙盤生命靈數報告卡</h2>", unsafe_allow_html=True)
        st.write("---")

        num_tab1, num_tab2 = st.tabs([
            f"☀️ 陽曆外顯人格：{solar_res['goal_num']} ({solar_num_info.get('title', '')})",
            f"🌙 陰曆內在人格：{lunar_res['goal_num'] if lunar_res else '未知'} ({lunar_num_info.get('title', '') if lunar_num_info else ''})"
        ])

        with num_tab1:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🌟 外在正面特質")
                st.info(" • " + "\n • ".join(solar_num_info.get('positive', [])))
                st.markdown("### ⚠️ 外在負面盲點")
                st.warning(" • " + "\n • ".join(solar_num_info.get('negative', [])))
            with c2:
                st.markdown("### 🏆 落地成功鑰匙")
                st.success(" • " + "\n • ".join(solar_num_info.get('success', [])))
                st.markdown("### 🧘 心智成長課題")
                st.error(" • " + "\n • ".join(solar_num_info.get('immature', [])))

        with num_tab2:
            if lunar_num_info:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### 🌟 內在潛能特質")
                    st.info(" • " + "\n • ".join(lunar_num_info.get('positive', [])))
                    st.markdown("### ⚠️ 潛意識情緒盲點")
                    st.warning(" • " + "\n • ".join(lunar_num_info.get('negative', [])))
                with c2:
                    st.markdown("### 🏆 內在安全感鑰匙")
                    st.success(" • " + "\n • ".join(lunar_num_info.get('success', [])))
                    st.markdown("### 🧘 潛意識轉化課題")
                    st.error(" • " + "\n • ".join(lunar_num_info.get('immature', [])))
            else:
                st.warning("無陰曆轉換資料")

        st.write("---")
        
        st.markdown("<h3 style='text-align:center; color:#8C1C1C;'>🔮 專向深度主題剖析</h3>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.button("❤️ 解鎖 辰祐閣 感情專項深度分析", on_click=lambda: switch_page('love_analysis'), use_container_width=True, key="btn_love_report")
        with col_btn2:
            st.button("💼 解鎖 辰祐閣 事業與財富專項深度分析", on_click=lambda: switch_page('career_analysis'), use_container_width=True, key="btn_career_report")

        st.write("---")

        active_api_key = None
        try:
            if "GEMINI_API_KEY" in st.secrets:
                active_api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            active_api_key = None

        prompt_content = generate_prompt(solar_res, lunar_res, solar_mbti, lunar_mbti, theme_key="general")

        if st.session_state.report_cache is None:
            if active_api_key:
                with st.spinner("🔮 辰祐閣正在為您演算雙盤目標數、東方 MBTI 與幾何角度能量流，請稍候..."):
                    try:
                        report_text = call_model(active_api_key, prompt_content)
                        st.session_state.report_cache = report_text
                        st.rerun()
                    except Exception as gen_e:
                        st.error(f"⚠️ {gen_e}")
                        if st.button("🔄 重新嘗試生成總體報告", key="retry_main_report"):
                            st.rerun()
            else:
                st.warning("⚠️ 尚未在 Streamlit Secrets 設定 `GEMINI_API_KEY`！")

        if st.session_state.report_cache:
            st.markdown(st.session_state.report_cache)

elif st.session_state.page == 'love_analysis':
    st.button("⬅️ 返回總體報告頁", on_click=lambda: switch_page('analysis'), key="btn_back_to_analysis_from_love")
    
    solar_res = st.session_state.get('current_res', None)
    lunar_res = st.session_state.get('current_lunar_res', None)

    if solar_res:
        solar_mbti = get_eastern_mbti_info(solar_res, prefix="S")
        lunar_mbti = get_eastern_mbti_info(lunar_res, prefix="L")
        
        active_api_key = None
        try:
            if "GEMINI_API_KEY" in st.secrets:
                active_api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            active_api_key = None

        love_prompt = generate_prompt(solar_res, lunar_res, solar_mbti, lunar_mbti, theme_key="love")

        if st.session_state.love_report_cache is None:
            if active_api_key:
                with st.spinner("❤️ 辰祐閣正在為您推演東方 MBTI 感情磁場與姻緣黑洞，請稍候..."):
                    try:
                        love_text = call_model(active_api_key, love_prompt)
                        st.session_state.love_report_cache = love_text
                        st.rerun()
                    except Exception as gen_e:
                        st.error(f"⚠️ {gen_e}")
                        if st.button("🔄 重新嘗試生成感情報告", key="retry_love_report"):
                            st.rerun()
            else:
                st.warning("⚠️ 尚未在 Streamlit Secrets 設定 `GEMINI_API_KEY`！")

        if st.session_state.love_report_cache:
            st.markdown(st.session_state.love_report_cache)

elif st.session_state.page == 'career_analysis':
    st.button("⬅️ 返回總體報告頁", on_click=lambda: switch_page('analysis'), key="btn_back_to_analysis_from_career")
    
    solar_res = st.session_state.get('current_res', None)
    lunar_res = st.session_state.get('current_lunar_res', None)

    if solar_res:
        solar_mbti = get_eastern_mbti_info(solar_res, prefix="S")
        lunar_mbti = get_eastern_mbti_info(lunar_res, prefix="L")

        active_api_key = None
        try:
            if "GEMINI_API_KEY" in st.secrets:
                active_api_key = st.secrets["GEMINI_API_KEY"]
        except Exception:
            active_api_key = None

        career_prompt = generate_prompt(solar_res, lunar_res, solar_mbti, lunar_mbti, theme_key="career")

        if st.session_state.career_report_cache is None:
            if active_api_key:
                with st.spinner("💼 辰祐閣正在為您演算東方 MBTI 事業天賦與財富鎖鏈，請稍候..."):
                    try:
                        career_text = call_model(active_api_key, career_prompt)
                        st.session_state.career_report_cache = career_text
                        st.rerun()
                    except Exception as gen_e:
                        st.error(f"⚠️ {gen_e}")
                        if st.button("🔄 重新嘗試生成事業報告", key="retry_career_report"):
                            st.rerun()
            else:
                st.warning("⚠️ 尚未在 Streamlit Secrets 設定 `GEMINI_API_KEY`！")

        if st.session_state.career_report_cache:
            st.markdown(st.session_state.career_report_cache)
