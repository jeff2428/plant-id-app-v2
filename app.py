import streamlit as st
import requests
import re
from PIL import Image
import io
import json
from datetime import datetime
from urllib.parse import quote

# ==========================================
# 0. 頁面設定
# ==========================================
st.set_page_config(
    page_title="🌿 生態探索｜植物辨識",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. CSS 樣式
# ==========================================
st.markdown("""
<style>
/* ══════════════════════════════════════════
   電腦端 - 側邊欄展開按鈕
   ══════════════════════════════════════════ */
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    z-index: 999999 !important;
    background: linear-gradient(135deg, #2d6e45, #1a4a2e) !important;
    border: 2px solid #4a9e5f !important;
    border-radius: 10px !important;
    width: 48px !important;
    height: 48px !important;
    min-width: 48px !important;
    min-height: 48px !important;
    padding: 8px !important;
    margin: 0 !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4), 0 0 20px rgba(74,158,95,0.3) !important;
    transition: all 0.2s ease !important;
}

[data-testid="collapsedControl"]:hover {
    background: linear-gradient(135deg, #3a8a56, #245c38) !important;
    border-color: #7ec98a !important;
    transform: scale(1.05) !important;
}

/* 電腦端 SVG 圖標顏色 */
[data-testid="collapsedControl"] svg {
    stroke: #c8f0cc !important;
    color: #c8f0cc !important;
    width: 24px !important;
    height: 24px !important;
}

[data-testid="collapsedControl"] svg line,
[data-testid="collapsedControl"] svg path,
[data-testid="collapsedControl"] svg polyline {
    stroke: #c8f0cc !important;
}

/* ══════════════════════════════════════════
   電腦端 - 側邊欄關閉按鈕
   ══════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
[data-testid="stSidebar"] button[kind="header"],
[data-testid="stSidebar"] [data-testid="baseButton-header"] {
    position: absolute !important;
    top: 12px !important;
    right: 12px !important;
    z-index: 9999 !important;
    background: linear-gradient(135deg, #1a3020, #0e1a14) !important;
    border: 1px solid #3a7a50 !important;
    border-radius: 8px !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    padding: 6px !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover,
[data-testid="stSidebar"] button[kind="header"]:hover {
    background: linear-gradient(135deg, #243828, #162018) !important;
    border-color: #4a9e5f !important;
}

/* 電腦端關閉按鈕 SVG 顏色 */
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebar"] button[kind="header"] svg {
    stroke: #7ec98a !important;
    color: #7ec98a !important;
    width: 18px !important;
    height: 18px !important;
}

[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg line,
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg path,
[data-testid="stSidebar"] button[kind="header"] svg line,
[data-testid="stSidebar"] button[kind="header"] svg path {
    stroke: #7ec98a !important;
}

/* ══════════════════════════════════════════
   手機端專用樣式 - 修復圖示顯示問題
   ══════════════════════════════════════════ */
@media (max-width: 768px) {
    /* 手機端展開按鈕基本樣式 */
    [data-testid="collapsedControl"] {
        top: 10px !important;
        left: 10px !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
        font-size: 0 !important;
        color: transparent !important;
    }
    
    /* 隱藏按鈕內所有子元素的文字（包括 bubble_arrow_right） */
    [data-testid="collapsedControl"] * {
        font-size: 0 !important;
        color: transparent !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* 隱藏 SVG */
    [data-testid="collapsedControl"] svg {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 使用偽元素顯示漢堡圖示 */
    [data-testid="collapsedControl"]::after {
        content: "☰" !important;
        font-size: 1.6rem !important;
        color: #c8f0cc !important;
        -webkit-text-fill-color: #c8f0cc !important;
        display: block !important;
        visibility: visible !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        pointer-events: none !important;
        font-family: Arial, Helvetica, sans-serif !important;
        line-height: 1 !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* 手機端關閉按鈕基本樣式 */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] button[kind="header"],
    [data-testid="stSidebar"] [data-testid="baseButton-header"] {
        top: 10px !important;
        right: 10px !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: hidden !important;
        font-size: 0 !important;
        color: transparent !important;
    }
    
    /* 隱藏關閉按鈕內所有子元素文字 */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stSidebar"] button[kind="header"] *,
    [data-testid="stSidebar"] [data-testid="baseButton-header"] * {
        font-size: 0 !important;
        color: transparent !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* 隱藏關閉按鈕 SVG */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebar"] button[kind="header"] svg,
    [data-testid="stSidebar"] [data-testid="baseButton-header"] svg {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* 使用偽元素顯示關閉圖示 */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]::after,
    [data-testid="stSidebar"] button[kind="header"]::after,
    [data-testid="stSidebar"] [data-testid="baseButton-header"]::after {
        content: "✕" !important;
        font-size: 1.2rem !important;
        color: #7ec98a !important;
        -webkit-text-fill-color: #7ec98a !important;
        display: block !important;
        visibility: visible !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        pointer-events: none !important;
        font-family: Arial, Helvetica, sans-serif !important;
        line-height: 1 !important;
        font-weight: bold !important;
    }
}

/* ══════════════════════════════════════════
   側邊欄主體樣式
   ══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1510 0%, #0a1210 100%) !important;
    border-right: 1px solid #1a3020 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 3.5rem !important;
}

[data-testid="stSidebar"] .stMarkdown {
    color: #7aab82 !important;
}

/* ══════════════════════════════════════════
   主要樣式
   ══════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=Noto+Sans+TC:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans TC', sans-serif;
    background-color: #0e1a14;
    color: #d4e8d0;
}

.main .block-container {
    padding: 2rem 3rem 4rem;
    max-width: 1100px;
}

h1 {
    font-family: 'Noto Serif TC', serif !important;
    font-size: 2.6rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #7ec98a, #3a9e5f, #a8d8a8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.06em;
    margin-bottom: 0.2rem !important;
}

h2, h3 {
    font-family: 'Noto Serif TC', serif !important;
    color: #a8d8a8 !important;
}

.subtitle {
    color: #6a9b72;
    font-size: 0.95rem;
    letter-spacing: 0.12em;
    margin-bottom: 2rem;
    font-weight: 300;
}

/* 上傳區 */
[data-testid="stFileUploader"] {
    border: 2px dashed #2d5c3a !important;
    border-radius: 16px !important;
    background: #111f16 !important;
    padding: 1.5rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #4a9e5f !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: transparent !important;
    border: 1px solid #2d5c3a !important;
    border-radius: 8px !important;
    padding: 0.3rem 1.2rem !important;
    color: #5a9a6a !important;
}

[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] label {
    display: none !important;
}

/* 主要按鈕 */
.main .stButton > button {
    background: linear-gradient(135deg, #2d6e45, #1a4a2e) !important;
    color: #c8f0cc !important;
    border: 1px solid #3a7a50 !important;
    border-radius: 12px !important;
    font-family: 'Noto Sans TC', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 2.4rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(58,158,95,0.25) !important;
}

.main .stButton > button:hover {
    background: linear-gradient(135deg, #3a8a56, #245c38) !important;
    transform: translateY(-2px) !important;
}

.main .stButton > button:disabled {
    opacity: 0.5 !important;
}

/* 側邊欄按鈕 */
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #2d6e45, #1a4a2e) !important;
    color: #c8f0cc !important;
    border: 1px solid #3a7a50 !important;
    border-radius: 10px !important;
    font-family: 'Noto Sans TC', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.5rem 1rem !important;
}

/* 結果卡片 */
.result-card {
    background: linear-gradient(145deg, #112018, #0e1a12);
    border: 1px solid #2d5c3a;
    border-radius: 20px;
    padding: 1.8rem 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.result-card-best {
    background: linear-gradient(145deg, #141f12, #0e1a0c);
    border: 1.5px solid #4a9e5f;
    border-radius: 20px;
    padding: 2rem 2.2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 40px rgba(74,158,95,0.2);
    position: relative;
}

.result-card-best::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3a9e5f, #7ec98a, #3a9e5f);
    border-radius: 20px 20px 0 0;
}

.plant-name {
    font-family: 'Noto Serif TC', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #8fd4a0;
    margin-bottom: 0.3rem;
}

.scientific-name {
    font-style: italic;
    color: #5a8a6a;
    font-size: 1.05rem;
    margin-bottom: 1rem;
}

.confidence-bar-wrap {
    background: #1a2e20;
    border-radius: 8px;
    height: 10px;
    margin: 0.5rem 0 0.2rem;
    overflow: hidden;
    border: 1px solid #2d4a35;
}

.confidence-bar {
    height: 100%;
    border-radius: 8px;
}

.badge {
    display: inline-block;
    background: #1d3d28;
    color: #7ec98a;
    border: 1px solid #2d5c3a;
    border-radius: 20px;
    padding: 0.22rem 0.85rem;
    font-size: 0.78rem;
    margin: 0.2rem;
}

.badge-gold {
    background: #2a2a10;
    color: #c8b864;
    border-color: #5a5020;
}

.detail-section {
    background: #0a1410;
    border: 1px solid #1e3824;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
}

.history-item {
    background: #111a14;
    border: 1px solid #1e3824;
    border-radius: 12px;
    padding: 0.8rem 1.1rem;
    margin: 0.4rem 0;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

hr {
    border: none;
    border-top: 1px solid #1e3824 !important;
    margin: 1.5rem 0 !important;
}

.stSpinner > div {
    border-top-color: #4a9e5f !important;
}

[data-testid="stImage"] img {
    border-radius: 16px;
    border: 1px solid #2d5c3a;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}

[data-testid="stMetricValue"] {
    color: #7ec98a !important;
    font-family: 'Noto Serif TC', serif !important;
}

.taxon-table { width: 100%; border-collapse: collapse; margin: 0.5rem 0; }
.taxon-table tr { border-bottom: 1px solid #1a3020; }
.taxon-table tr:last-child { border-bottom: none; }
.taxon-table td { padding: 0.65rem 0.5rem; font-size: 0.88rem; }
.taxon-label { color: #5a8a6a; width: 60px; font-weight: 500; }
.taxon-value { color: #c0e0c8; font-style: italic; }
.taxon-cn { color: #7ec98a; font-style: normal; margin-left: 0.5rem; font-size: 0.82rem; }

.char-card { background: #0e1a12; border: 1px solid #1e3824; border-radius: 14px; padding: 1.2rem 1.4rem; margin: 0.8rem 0; }
.char-row { display: flex; justify-content: space-between; align-items: center; padding: 0.55rem 0; border-bottom: 1px solid #1a2e1e; font-size: 0.87rem; }
.char-row:last-child { border-bottom: none; }
.char-key { color: #5a8a6a; }
.char-val { color: #b0d8b8; font-weight: 500; }

.care-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; margin: 0.8rem 0; }
.care-item { background: #0e1a12; border: 1px solid #1e3824; border-radius: 12px; padding: 1rem 1.1rem; }
.care-icon { font-size: 1.4rem; margin-bottom: 0.3rem; }
.care-title { color: #7ec98a; font-size: 0.82rem; font-weight: 600; margin-bottom: 0.2rem; }
.care-desc { color: #90b898; font-size: 0.85rem; }

.wiki-extract { background: #0c1810; border-left: 3px solid #2d6a40; border-radius: 0 10px 10px 0; padding: 0.9rem 1.2rem; color: #8ab898; font-size: 0.85rem; line-height: 1.8; margin: 0.8rem 0; }

/* 名稱資訊區塊 */
.name-info-section {
    background: #0c1810;
    border: 1px solid #1e3824;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}

.name-info-section .section-title {
    color: #7ec98a;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.6rem;
}

.alias-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    margin-bottom: 0.5rem;
}

.english-names {
    color: #3a6058;
    font-size: 0.82rem;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid #1a2e1e;
}

.wiki-link {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: linear-gradient(135deg, #1a3828, #0e2018);
    border: 1px solid #2d5c3a;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    color: #7ec98a !important;
    text-decoration: none !important;
    font-size: 0.88rem;
    font-weight: 500;
    margin-top: 0.8rem;
    transition: all 0.2s ease;
}

.wiki-link:hover {
    background: linear-gradient(135deg, #245038, #163028);
    border-color: #4a9e5f;
    transform: translateY(-1px);
}

/* ══════════════════════════════════════════
   手機響應式 - 其他元素
   ══════════════════════════════════════════ */
@media (max-width: 768px) {
    .care-grid { grid-template-columns: 1fr; }
    .plant-name { font-size: 1.6rem; }
    h1 { font-size: 2rem !important; }
    .main .block-container { padding: 1.5rem 1rem 3rem; }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API 設定
# ==========================================
API_KEY = st.secrets.get("PLANTNET_API_KEY", "2b10XXXXXXXXXXXXXXXXXXXXXXXXxx")
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# ==========================================
# 3. Session State
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []
if "total_identifications" not in st.session_state:
    st.session_state.total_identifications = 0
if "expanded_cards" not in st.session_state:
    st.session_state.expanded_cards = {}
if "identification_results" not in st.session_state:
    st.session_state.identification_results = None
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "just_identified" not in st.session_state:
    st.session_state.just_identified = False

def validate_history():
    valid = []
    for r in st.session_state.history:
        if isinstance(r, dict):
            try:
                valid.append({
                    'name': r.get('name', '未知'),
                    'sci': r.get('sci', ''),
                    'score': float(r.get('score', 0)),
                    'time': r.get('time', ''),
                    'emoji': r.get('emoji', '🌿')
                })
            except:
                continue
    st.session_state.history = valid

validate_history()

# ==========================================
# 4. 工具函數
# ==========================================
def has_chinese(text):
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', text))

@st.cache_data(ttl=3600, show_spinner=False)
def search_wikipedia(scientific_name):
    url = "https://zh.wikipedia.org/w/api.php"
    headers = {"User-Agent": "PlantExplorer/3.0"}
    try:
        res = requests.get(url, params={
            "action": "query", "list": "search",
            "srsearch": scientific_name, "format": "json", "utf8": 1
        }, headers=headers, timeout=5).json()
        results = res.get("query", {}).get("search", [])
        if not results:
            return None, None
        title = results[0].get("title", "")
        if not has_chinese(title):
            return None, None
        rd = requests.get(url, params={
            "action": "query", "titles": title,
            "prop": "redirects", "rdlimit": "50",
            "format": "json", "utf8": 1
        }, headers=headers, timeout=5).json()
        pages = rd.get("query", {}).get("pages", {})
        aliases = [title]
        for _, info in pages.items():
            for r in info.get("redirects", []):
                t = r.get("title", "")
                if ":" not in t and has_chinese(t):
                    aliases.append(t)
        return list(dict.fromkeys(aliases)), f"https://zh.wikipedia.org/wiki/{quote(title)}"
    except:
        return None, None

@st.cache_data(ttl=3600, show_spinner=False)
def get_gbif(scientific_name):
    try:
        res = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": scientific_name},
            timeout=6
        ).json()
        return {
            "phylum": res.get("phylum", ""),
            "class": res.get("class", ""),
            "order": res.get("order", ""),
            "family": res.get("family", ""),
            "genus": res.get("genus", ""),
            "species": res.get("species", scientific_name),
        }
    except:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def get_wiki_extract(title):
    try:
        res = requests.get(
            "https://zh.wikipedia.org/w/api.php",
            params={
                "action": "query", "prop": "extracts",
                "exintro": True, "explaintext": True,
                "exsentences": 3, "titles": title,
                "format": "json", "utf8": 1, "redirects": 1
            },
            headers={"User-Agent": "PlantExplorer/3.0"},
            timeout=5
        ).json()
        for pid, page in res.get("query", {}).get("pages", {}).items():
            if pid != "-1":
                txt = page.get("extract", "").strip()
                if txt and len(txt) > 30:
                    return txt[:350]
    except:
        pass
    return None

def get_color(score):
    if score >= 80:
        return "#3fcf6e"
    elif score >= 50:
        return "#c8b864"
    return "#c86464"

def get_label(score):
    if score >= 80:
        return "高度吻合", "🟢"
    elif score >= 50:
        return "中度吻合", "🟡"
    return "低度吻合", "🔴"

def render_bar(score, color):
    st.markdown(f'''
    <div class="confidence-bar-wrap">
        <div class="confidence-bar" style="width:{score:.1f}%;background:linear-gradient(90deg,{color}88,{color});"></div>
    </div>
    <p style="color:{color};font-size:0.82rem;margin:0;text-align:right;">{score:.2f}%</p>
    ''', unsafe_allow_html=True)

def compress_image(img, max_w=1920):
    try:
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), Image.Resampling.LANCZOS)
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                bg.paste(img, mask=img.split()[-1])
            else:
                bg.paste(img)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except:
        return img

TAXON_ZH = {
    "Tracheophyta": "維管束植物門",
    "Magnoliopsida": "木蘭綱",
    "Liliopsida": "百合綱",
    "Pinopsida": "松綱",
    "Polypodiopsida": "蕨綱",
    "Lamiales": "唇形目",
    "Rosales": "薔薇目",
    "Fabales": "豆目",
    "Asterales": "菊目",
    "Poales": "禾本目",
    "Malpighiales": "金虎尾目",
    "Sapindales": "無患子目",
    "Malvales": "錦葵目",
    "Gentianales": "龍膽目",
    "Solanales": "茄目",
    "Brassicales": "十字花目",
    "Myrtales": "桃金孃目",
    "Ericales": "杜鵑花目",
    "Lamiaceae": "唇形科",
    "Rosaceae": "薔薇科",
    "Fabaceae": "豆科",
    "Asteraceae": "菊科",
    "Poaceae": "禾本科",
    "Moraceae": "桑科",
    "Euphorbiaceae": "大戟科",
    "Rutaceae": "芸香科",
    "Orchidaceae": "蘭科",
    "Araceae": "天南星科",
    "Apocynaceae": "夾竹桃科",
    "Solanaceae": "茄科",
    "Brassicaceae": "十字花科",
    "Myrtaceae": "桃金孃科",
    "Convolvulaceae": "旋花科",
}

CARE_DATA = {
    "Lamiaceae": {"diff": "容易", "diff_c": "#3fcf6e", "temp": "-5~41°C", "zone": "8-10", "water": "中等", "fert": "每月一次", "prune": "冬季", "prop": "扦插", "sun": "全日照"},
    "Rosaceae": {"diff": "中等", "diff_c": "#c8b864", "temp": "-15~35°C", "zone": "5-9", "water": "規律", "fert": "每2週", "prune": "早春", "prop": "扦插嫁接", "sun": "全日照"},
    "Fabaceae": {"diff": "容易", "diff_c": "#3fcf6e", "temp": "5~40°C", "zone": "7-11", "water": "少量", "fert": "少量", "prune": "花後", "prop": "播種", "sun": "全日照"},
    "Asteraceae": {"diff": "容易", "diff_c": "#3fcf6e", "temp": "0~35°C", "zone": "6-10", "water": "中等", "fert": "每2-4週", "prune": "花後", "prop": "播種分株", "sun": "全日照"},
    "Orchidaceae": {"diff": "困難", "diff_c": "#c86464", "temp": "15~30°C", "zone": "10-12", "water": "少量", "fert": "蘭花肥", "prune": "花後", "prop": "分株", "sun": "散射光"},
    "Araceae": {"diff": "中等", "diff_c": "#c8b864", "temp": "18~30°C", "zone": "10-12", "water": "保持濕潤", "fert": "每2週", "prune": "去黃葉", "prop": "分株扦插", "sun": "散射光"},
    "Solanaceae": {"diff": "中等", "diff_c": "#c8b864", "temp": "15~30°C", "zone": "8-11", "water": "規律", "fert": "每2週", "prune": "整形", "prop": "播種扦插", "sun": "全日照"},
    "DEFAULT": {"diff": "中等", "diff_c": "#c8b864", "temp": "5~35°C", "zone": "7-10", "water": "中等", "fert": "每月一次", "prune": "春季", "prop": "扦插播種", "sun": "全日照"},
}

def get_care(family):
    return CARE_DATA.get(family, CARE_DATA["DEFAULT"])

# ==========================================
# 5. 側邊欄
# ==========================================
with st.sidebar:
    st.markdown("## 📋 辨識歷史")
    
    if not st.session_state.history:
        st.markdown('<p style="color:#3a6a48;font-size:0.85rem;">尚無紀錄</p>', unsafe_allow_html=True)
    else:
        for r in reversed(st.session_state.history[-10:]):
            try:
                emoji = r.get('emoji', '🌿')
                name = r.get('name', '未知')
                time_str = r.get('time', '')
                score = r.get('score', 0)
                if not isinstance(score, (int, float)):
                    score = 0
                st.markdown(f'''
                <div class="history-item">
                    <span style="font-size:1.5rem;">{emoji}</span>
                    <div>
                        <div style="font-size:0.88rem;color:#a0d0a8;font-weight:500;">{name}</div>
                        <div style="font-size:0.72rem;color:#4a7a56;">{time_str} | {score:.1f}%</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            except:
                continue
    
    st.markdown("---")
    
    if st.session_state.history:
        if st.button("🗑️ 清除歷史", use_container_width=True):
            st.session_state.history = []
            st.session_state.total_identifications = 0
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ 設定")
    top_n = st.slider("顯示候選數", 1, 5, 3)
    
    st.markdown("---")
    st.markdown('''
    <div style="color:#3a6a48;font-size:0.78rem;line-height:1.8;">
    🌿 <strong style="color:#5a9a68;">生態探索 v3.0</strong><br>
    PlantNet + 維基百科 + GBIF
    </div>
    ''', unsafe_allow_html=True)

# ==========================================
# 6. 主頁面
# ==========================================
st.markdown("# 🌿 生態探索")
st.markdown('<p class="subtitle">植物智能辨識系統 Powered by PlantNet AI</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("已辨識", f"{st.session_state.total_identifications} 種")
with col2:
    if st.session_state.history:
        scores = [r.get('score', 0) for r in st.session_state.history if isinstance(r.get('score'), (int, float))]
        avg = sum(scores) / len(scores) if scores else 0
        st.metric("平均信心度", f"{avg:.1f}%")
    else:
        st.metric("平均信心度", "—")
with col3:
    st.metric("資料庫", "30,000+ 種")

st.markdown("---")

# ==========================================
# 7. 上傳區
# ==========================================
col_up, col_prev = st.columns([1, 1], gap="large")

with col_up:
    st.markdown("### 📸 上傳植物照片")
    st.markdown('<p style="color:#4a7a56;font-size:0.85rem;">建議清晰拍攝葉片、花朵或果實</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("選擇檔案", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")
    if uploaded:
        kb = uploaded.size // 1024
        mb = kb / 1024
        size_str = f"{mb:.1f} MB" if mb >= 1 else f"{kb} KB"
        st.markdown(f'<div class="badge">📁 {uploaded.name}</div><div class="badge">📦 {size_str}</div>', unsafe_allow_html=True)

with col_prev:
    if uploaded:
        try:
            image = Image.open(uploaded)
            image = compress_image(image)
            st.image(image, caption="📸 預覽", use_container_width=True)
        except Exception as e:
            st.error(f"圖片載入失敗：{e}")
            image = None
    else:
        st.markdown('''
        <div style="background:#0a1410;border:1px dashed #1e3820;border-radius:16px;
                    height:280px;display:flex;align-items:center;justify-content:center;
                    flex-direction:column;gap:1rem;">
            <span style="font-size:4rem;">🍃</span>
            <p style="color:#2d5c3a;font-size:0.9rem;text-align:center;">上傳照片後<br>預覽顯示於此</p>
        </div>
        ''', unsafe_allow_html=True)
        image = None

st.markdown("")
btn_col, _ = st.columns([1, 3])
with btn_col:
    start_btn = st.button("🔬 開始辨識", disabled=(uploaded is None), use_container_width=True)

# ==========================================
# 8. 辨識邏輯
# ==========================================
if start_btn and uploaded and image:
    st.session_state.expanded_cards = {0: True}
    with st.spinner("🌱 AI 辨識中..."):
        buf = io.BytesIO()
        image.save(buf, format='JPEG', quality=85)
        try:
            resp = requests.post(
                API_ENDPOINT,
                files={'images': ('image.jpg', buf.getvalue(), 'image/jpeg')},
                data={'organs': ['auto']},
                timeout=30
            )
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            st.error("請求逾時，請檢查網路")
            st.stop()
        except requests.exceptions.ConnectionError:
            st.error("無法連接伺服器")
            st.stop()
        except requests.exceptions.HTTPError:
            st.error(f"HTTP 錯誤：{resp.status_code}")
            st.stop()
        except Exception as e:
            st.error(f"錯誤：{e}")
            st.stop()
        
        try:
            result = resp.json()
        except:
            st.error("回應格式錯誤")
            st.stop()
        
        all_results = result.get('results', [])
        if not all_results:
            st.warning("未能辨識，請嘗試更清晰的照片")
            st.stop()
        
        st.session_state.identification_results = all_results[:top_n]
        st.session_state.show_results = True
        st.session_state.just_identified = True

# ==========================================
# 9. 顯示結果
# ==========================================
if st.session_state.get('show_results') and st.session_state.get('identification_results'):
    st.markdown("---")
    st.markdown("## 🎯 辨識結果")
    st.markdown('<p style="color:#4a7a56;font-size:0.85rem;text-align:center;">點擊按鈕展開詳細資訊</p>', unsafe_allow_html=True)
    
    top_results = st.session_state.identification_results
    
    for idx, match in enumerate(top_results):
        sci = match.get('species', {}).get('scientificNameWithoutAuthor', '未知')
        genus = match.get('species', {}).get('genus', {}).get('scientificNameWithoutAuthor', '')
        family = match.get('species', {}).get('family', {}).get('scientificNameWithoutAuthor', '')
        common = match.get('species', {}).get('commonNames', [])
        score = match.get('score', 0) * 100
        
        color = get_color(score)
        label, emoji_label = get_label(score)
        
        cn_list = list(dict.fromkeys([n for n in common if has_chinese(n)]))
        wiki_link = None
        
        if not cn_list:
            wiki_names, wiki_link = search_wikipedia(sci)
            if wiki_names:
                cn_list = wiki_names
                source = f"維基百科({len(cn_list)}筆)"
            else:
                source = "無中文資料"
        else:
            source = f"PlantNet({len(cn_list)}筆)"
            _, wiki_link = search_wikipedia(sci)
        
        display = cn_list[0] if cn_list else "資料不足"
        
        if idx == 0 and st.session_state.get('just_identified'):
            st.session_state.history.append({
                'name': display,
                'sci': sci,
                'score': score,
                'time': datetime.now().strftime("%H:%M"),
                'emoji': '🌿'
            })
            st.session_state.total_identifications += 1
            st.session_state.just_identified = False
        
        card = "result-card-best" if idx == 0 else "result-card"
        badge = '<span class="badge badge-gold">✨ 最佳匹配</span>' if idx == 0 else f'<span class="badge">候選 #{idx+1}</span>'
        genus_html = f"<span style='color:#4a7a56;font-size:0.85rem;'>🌱 屬：{genus}</span>" if genus else ""
        family_html = f"<span style='color:#4a7a56;font-size:0.85rem;'>🌾 科：{family}</span>" if family else ""
        
        st.markdown(f'''
        <div class="{card}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">
                <div>{badge} <span class="badge">{emoji_label} {label}</span></div>
                <span style="color:#3a6a48;font-size:0.8rem;">{source}</span>
            </div>
            <div class="plant-name">{display}</div>
            <div class="scientific-name">{sci}</div>
            <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">{genus_html} {family_html}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown(f"**信心指標** {score:.2f}%")
        render_bar(score, color)
        
        card_key = idx
        is_expanded = st.session_state.expanded_cards.get(card_key, idx == 0)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            btn_text = "🔼 收合詳情" if is_expanded else "🔽 查看詳情"
            if st.button(btn_text, key=f"toggle_{idx}", use_container_width=True):
                st.session_state.expanded_cards[card_key] = not is_expanded
                st.rerun()
        
        if is_expanded:
            st.markdown('<div class="detail-section">', unsafe_allow_html=True)
            
            has_alias = len(cn_list) > 1
            eng = [n for n in common if not has_chinese(n)][:3]
            has_eng = len(eng) > 0
            
            if has_alias or has_eng or wiki_link:
                name_html = '<div class="name-info-section">'
                
                if has_alias:
                    name_html += '<div class="section-title">📖 所有別名</div>'
                    name_html += '<div class="alias-container">'
                    for i, a in enumerate(cn_list):
                        star = "⭐ " if i == 0 else ""
                        name_html += f'<span class="badge">{star}{a}</span>'
                    name_html += '</div>'
                
                if has_eng:
                    name_html += f'<div class="english-names">英文名：{" · ".join(eng)}</div>'
                
                if wiki_link:
                    name_html += f'<a href="{wiki_link}" target="_blank" class="wiki-link">📚 查看維基百科</a>'
                
                name_html += '</div>'
                st.markdown(name_html, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2, gap="medium")
            
            with c1:
                st.markdown("#### 🌳 分類階層")
                gbif = get_gbif(sci)
                rows = [
                    ("門", gbif.get("phylum", "—")),
                    ("綱", gbif.get("class", "—")),
                    ("目", gbif.get("order", "—")),
                    ("科", gbif.get("family", "—")),
                    ("屬", gbif.get("genus", "—")),
                    ("種", gbif.get("species", sci)),
                ]
                html = ""
                for lbl, val in rows:
                    zh = TAXON_ZH.get(val, "")
                    zh_span = f'<span class="taxon-cn">（{zh}）</span>' if zh else ""
                    html += f'<tr><td class="taxon-label">{lbl}</td><td class="taxon-value">{val}{zh_span}</td></tr>'
                st.markdown(f'<table class="taxon-table">{html}</table>', unsafe_allow_html=True)
                
                wiki_title = cn_list[0] if cn_list else sci
                extract = get_wiki_extract(wiki_title) or get_wiki_extract(sci)
                if extract:
                    st.markdown("#### 📖 植物簡介")
                    st.markdown(f'<div class="wiki-extract">{extract}</div>', unsafe_allow_html=True)
            
            with c2:
                st.markdown("#### 🌱 照護指南")
                fam = gbif.get("family", family) or family or "DEFAULT"
                care = get_care(fam)
                dc = care.get("diff_c", "#c8b864")
                
                st.markdown(f'''
                <div style="margin-bottom:1rem;">
                    <span style="background:{dc}22;color:{dc};border:1px solid {dc}66;border-radius:20px;padding:0.35rem 1.1rem;font-weight:600;">
                        {care.get("diff", "中等")}
                    </span>
                    <span style="color:#3a6a48;font-size:0.8rem;margin-left:0.5rem;">照護難度</span>
                </div>
                ''', unsafe_allow_html=True)
                
                st.markdown(f'''
                <div class="char-card">
                    <div style="color:#5a8a6a;font-size:0.78rem;margin-bottom:0.5rem;">🌡️ 氣候條件</div>
                    <div class="char-row"><span class="char-key">適合氣溫</span><span class="char-val">{care.get("temp", "—")}</span></div>
                    <div class="char-row"><span class="char-key">耐寒區間</span><span class="char-val">Zone {care.get("zone", "—")}</span></div>
                    <div class="char-row"><span class="char-key">光照需求</span><span class="char-val">{care.get("sun", "—")}</span></div>
                </div>
                ''', unsafe_allow_html=True)
                
                st.markdown(f'''
                <div class="care-grid">
                    <div class="care-item"><div class="care-icon">💧</div><div class="care-title">澆水</div><div class="care-desc">{care.get("water", "—")}</div></div>
                    <div class="care-item"><div class="care-icon">🌿</div><div class="care-title">肥料</div><div class="care-desc">{care.get("fert", "—")}</div></div>
                    <div class="care-item"><div class="care-icon">✂️</div><div class="care-title">修剪</div><div class="care-desc">{care.get("prune", "—")}</div></div>
                    <div class="care-item"><div class="care-icon">🌱</div><div class="care-title">繁殖</div><div class="care-desc">{care.get("prop", "—")}</div></div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("")
    
    st.markdown("---")
    st.markdown("### 📤 匯出報告")
    
    best = top_results[0]
    best_sci = best.get('species', {}).get('scientificNameWithoutAuthor', '')
    best_score = best.get('score', 0) * 100
    best_cn = [n for n in best.get('species', {}).get('commonNames', []) if has_chinese(n)]
    best_name = best_cn[0] if best_cn else best_sci
    
    report = f"""🌿 植物辨識報告
{'='*40}
時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*40}

最佳匹配：{best_name}
學名：{best_sci}
信心：{best_score:.2f}%

候選結果：
"""
    for i, m in enumerate(top_results):
        sn = m.get('species', {}).get('scientificNameWithoutAuthor', '')
        sc = m.get('score', 0) * 100
        cn = [n for n in m.get('species', {}).get('commonNames', []) if has_chinese(n)]
        nm = cn[0] if cn else sn
        report += f"{i+1}. {nm}（{sn}）{sc:.2f}%\n"
    
    report += f"\n{'='*40}\nPlantNet + 維基百科 + GBIF"
    
    json_str = json.dumps({
        "time": datetime.now().isoformat(),
        "results": [
            {
                "rank": i+1,
                "name": m.get('species', {}).get('scientificNameWithoutAuthor', ''),
                "score": m.get('score', 0)
            }
            for i, m in enumerate(top_results)
        ]
    }, ensure_ascii=False, indent=2)
    
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "📄 下載文字報告",
            report.encode("utf-8"),
            f"植物辨識_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            "text/plain",
            use_container_width=True
        )
    with c2:
        st.download_button(
            "📊 下載 JSON",
            json_str.encode("utf-8"),
            f"plant_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            "application/json",
            use_container_width=True
        )

# ==========================================
# 10. 頁尾
# ==========================================
st.markdown("---")
st.markdown('''
<div style="text-align:center;color:#2d5c3a;font-size:0.8rem;padding:1rem 0;line-height:2;">
    🌿 <strong style="color:#4a7a56;">生態探索</strong> v3.0<br>
    PlantNet AI + 維基百科 + GBIF<br>
    <span style="font-size:0.72rem;">僅供參考，鑑定請諮詢專家</span>
</div>
''', unsafe_allow_html=True)
