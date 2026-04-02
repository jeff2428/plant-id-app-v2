import streamlit as st
import requests
import re
from PIL import Image
import io
import base64
import json
from datetime import datetime
from urllib.parse import quote

# ==========================================
# 0. 頁面基礎設定（必須最先執行）
# ==========================================
st.set_page_config(
    page_title="🌿 生態探索｜植物辨識",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. 全域 CSS 美化（深色自然系主題）
# ==========================================
st.markdown("""
<style>
/* ── 引入字型 ── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=Noto+Sans+TC:wght@300;400;500&display=swap');

/* ── 全域基底 ── */
html, body, [class*="css"] {
    font-family: 'Noto Sans TC', sans-serif;
    background-color: #0e1a14;
    color: #d4e8d0;
}

/* ── 主內容區 ── */
.main .block-container {
    padding: 2rem 3rem 4rem;
    max-width: 1100px;
}

/* ── 大標題 ── */
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

/* ── 副標語 ── */
.subtitle {
    color: #6a9b72;
    font-size: 0.95rem;
    letter-spacing: 0.12em;
    margin-bottom: 2rem;
    font-weight: 300;
}

/* ── 上傳區美化 ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #2d5c3a !important;
    border-radius: 16px !important;
    background: #111f16 !important;
    padding: 1.5rem !important;
    transition: border-color 0.3s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #4a9e5f !important;
}

/* ── 統一桌機／手機上傳按鈕 ── */
[data-testid="stFileUploaderDropzone"] button {
    background: transparent !important;
    border: 1px solid #2d5c3a !important;
    border-radius: 8px !important;
    padding: 0.3rem 1.2rem !important;
    font-size: 0 !important;
    color: transparent !important;
}
[data-testid="stFileUploaderDropzone"] button::after {
    content: "📂 選擇檔案";
    font-family: 'Noto Sans TC', sans-serif;
    font-size: 0.85rem;
    color: #5a9a6a;
    letter-spacing: 0.06em;
}
[data-testid="stFileUploaderDropzone"] button:hover::after {
    color: #7ec98a;
}

/* ── 隱藏上傳區多餘文字 ── */
[data-testid="stFileUploader"] small {
    display: none !important;
}
[data-testid="stFileUploader"] label {
    font-size: 0 !important;
}

/* ── 響應式調整 ── */
@media (max-width: 768px) {
    [data-testid="stFileUploader"] {
        padding: 1rem !important;
    }
    h1 {
        font-size: 2rem !important;
    }
    .main .block-container {
        padding: 1.5rem 1rem 3rem;
    }
}

/* ── 按鈕 ── */
.stButton > button {
    background: linear-gradient(135deg, #2d6e45, #1a4a2e) !important;
    color: #c8f0cc !important;
    border: 1px solid #3a7a50 !important;
    border-radius: 12px !important;
    font-family: 'Noto Sans TC', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    padding: 0.6rem 2.4rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(58,158,95,0.25) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3a8a56, #245c38) !important;
    box-shadow: 0 6px 28px rgba(58,158,95,0.45) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}

/* ── 結果卡片 ── */
.result-card {
    background: linear-gradient(145deg, #112018, #0e1a12);
    border: 1px solid #2d5c3a;
    border-radius: 20px;
    padding: 1.8rem 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(100,200,120,0.1);
}

/* ── 最佳結果卡片（金框） ── */
.result-card-best {
    background: linear-gradient(145deg, #141f12, #0e1a0c);
    border: 1.5px solid #4a9e5f;
    border-radius: 20px;
    padding: 2rem 2.2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 40px rgba(74,158,95,0.2), inset 0 1px 0 rgba(150,220,160,0.15);
    position: relative;
    overflow: hidden;
}
.result-card-best::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3a9e5f, #7ec98a, #3a9e5f);
}

/* ── 植物名稱大字 ── */
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
    letter-spacing: 0.04em;
    margin-bottom: 1rem;
}

/* ── 信心指標條 ── */
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
    transition: width 1s ease;
}

/* ── 標籤徽章 ── */
.badge {
    display: inline-block;
    background: #1d3d28;
    color: #7ec98a;
    border: 1px solid #2d5c3a;
    border-radius: 20px;
    padding: 0.22rem 0.85rem;
    font-size: 0.78rem;
    margin: 0.2rem;
    letter-spacing: 0.06em;
}
.badge-gold {
    background: #2a2a10;
    color: #c8b864;
    border-color: #5a5020;
}

/* ── 歷史記錄區 ── */
.history-item {
    background: #111a14;
    border: 1px solid #1e3824;
    border-radius: 12px;
    padding: 0.8rem 1.1rem;
    margin: 0.4rem 0;
    cursor: pointer;
    transition: border-color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.history-item:hover {
    border-color: #3a7a50;
}

/* ── 分隔線 ── */
hr {
    border: none;
    border-top: 1px solid #1e3824 !important;
    margin: 1.5rem 0 !important;
}

/* ── 側邊欄 ── */
[data-testid="stSidebar"] {
    background: #0b1510 !important;
    border-right: 1px solid #1a3020 !important;
}
[data-testid="stSidebar"] .stMarkdown {
    color: #7aab82 !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: #4a9e5f !important;
}

/* ── Info / Success / Warning / Error ── */
.stSuccess {
    background: #0e2016 !important;
    border-left-color: #3a9e5f !important;
    color: #a8e0b4 !important;
}
.stInfo {
    background: #0c1e24 !important;
    border-left-color: #2a7a9a !important;
    color: #90ccd8 !important;
}
.stWarning {
    background: #1e1a08 !important;
    border-left-color: #8a7a20 !important;
    color: #c8b864 !important;
}
.stError {
    background: #1e0c0c !important;
    border-left-color: #9a2a2a !important;
    color: #d89090 !important;
}

/* ── 照片框 ── */
[data-testid="stImage"] img {
    border-radius: 16px;
    border: 1px solid #2d5c3a;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}

/* ── Metric 數字 ── */
[data-testid="stMetricValue"] {
    color: #7ec98a !important;
    font-family: 'Noto Serif TC', serif !important;
}

/* ── 分類階層表格 ── */
.taxon-table { 
    width: 100%; 
    border-collapse: collapse; 
    margin: 0.5rem 0; 
}
.taxon-table tr { 
    border-bottom: 1px solid #1a3020; 
}
.taxon-table tr:last-child { 
    border-bottom: none; 
}
.taxon-table td { 
    padding: 0.65rem 0.5rem; 
    font-size: 0.88rem; 
}
.taxon-label { 
    color: #5a8a6a; 
    width: 60px; 
    font-weight: 500; 
}
.taxon-value { 
    color: #c0e0c8; 
    font-style: italic; 
}
.taxon-cn { 
    color: #7ec98a; 
    font-style: normal; 
    margin-left: 0.5rem; 
    font-size: 0.82rem; 
}

/* ── 特徵 & 照護卡片 ── */
.char-card { 
    background: #0e1a12; 
    border: 1px solid #1e3824; 
    border-radius: 14px; 
    padding: 1.2rem 1.4rem; 
    margin: 0.8rem 0; 
}
.char-row { 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    padding: 0.55rem 0; 
    border-bottom: 1px solid #1a2e1e; 
    font-size: 0.87rem; 
}
.char-row:last-child { 
    border-bottom: none; 
}
.char-key { 
    color: #5a8a6a; 
}
.char-val { 
    color: #b0d8b8; 
    font-weight: 500; 
}
.care-grid { 
    display: grid; 
    grid-template-columns: 1fr 1fr; 
    gap: 0.8rem; 
    margin: 0.8rem 0; 
}
.care-item { 
    background: #0e1a12; 
    border: 1px solid #1e3824; 
    border-radius: 12px; 
    padding: 1rem 1.1rem; 
}
.care-item-wide { 
    grid-column: 1 / -1; 
    background: #0e1a12; 
    border: 1px solid #1e3824; 
    border-radius: 12px; 
    padding: 1rem 1.1rem; 
}
.care-icon { 
    font-size: 1.4rem; 
    margin-bottom: 0.3rem; 
}
.care-title { 
    color: #7ec98a; 
    font-size: 0.82rem; 
    font-weight: 600; 
    margin-bottom: 0.2rem; 
}
.care-desc { 
    color: #90b898; 
    font-size: 0.85rem; 
}
.wiki-extract { 
    background: #0c1810; 
    border-left: 3px solid #2d6a40; 
    border-radius: 0 10px 10px 0; 
    padding: 0.9rem 1.2rem; 
    color: #8ab898; 
    font-size: 0.85rem; 
    line-height: 1.8; 
    margin: 0.8rem 0; 
}

/* ── 分享按鈕 ── */
.share-btn {
    display: block;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    text-align: center;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
    margin-bottom: 0.5rem;
}
.share-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

/* ── 手機響應式 ── */
@media (max-width: 768px) {
    .care-grid {
        grid-template-columns: 1fr;
    }
    .plant-name {
        font-size: 1.6rem;
    }
    .scientific-name {
        font-size: 0.95rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API 設定
# ==========================================
API_KEY = st.secrets.get("PLANTNET_API_KEY", "2b1004UqTrbWJn4mj5hqcaZN")
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# ==========================================
# 3. Session State 初始化（防禦性編程）
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []
if "total_identifications" not in st.session_state:
    st.session_state.total_identifications = 0

def validate_and_migrate_history():
    """驗證並修復歷史記錄格式，確保所有必要欄位存在"""
    valid_records = []
    for record in st.session_state.history:
        if isinstance(record, dict):
            try:
                # 確保必要欄位存在，提供預設值
                validated_record = {
                    'name': record.get('name', '未知植物'),
                    'sci': record.get('sci', record.get('scientific', '—')),
                    'score': float(record.get('score', 0.0)),
                    'time': record.get('time', '—'),
                    'emoji': record.get('emoji', '🌿')
                }
                valid_records.append(validated_record)
            except (ValueError, TypeError):
                # 跳過無效記錄
                continue
    st.session_state.history = valid_records

# 執行驗證
validate_and_migrate_history()

# ==========================================
# 4. 核心工具函數
# ==========================================
def has_chinese(text):
    """檢查文字是否包含中文字元"""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', text))

@st.cache_data(ttl=3600, show_spinner=False)
def search_wikipedia_for_chinese(scientific_name):
    """
    搜尋維基百科中文名稱（快取 1 小時）
    返回：(別名列表, 維基連結)
    """
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    headers = {"User-Agent": "PlantExplorer/2.1 (Educational)"}
    try:
        # 第一步：搜尋主條目
        search_res = requests.get(wiki_url, params={
            "action": "query", 
            "list": "search",
            "srsearch": scientific_name, 
            "format": "json", 
            "utf8": 1
        }, headers=headers, timeout=5).json()
        
        results = search_res.get("query", {}).get("search", [])
        if not results:
            return None, None
        
        main_title = results[0].get("title", "")
        if not has_chinese(main_title):
            return None, None
        
        # 第二步：取得重定向（別名）
        rd_res = requests.get(wiki_url, params={
            "action": "query", 
            "titles": main_title,
            "prop": "redirects", 
            "rdlimit": "50",
            "format": "json", 
            "utf8": 1
        }, headers=headers, timeout=5).json()
        
        pages = rd_res.get("query", {}).get("pages", {})
        aliases = [main_title]
        
        for _, page_info in pages.items():
            for rd in page_info.get("redirects", []):
                t = rd.get("title", "")
                if ":" not in t and has_chinese(t):
                    aliases.append(t)
        
        unique = list(dict.fromkeys(aliases))
        wiki_link = f"https://zh.wikipedia.org/wiki/{quote(main_title)}"
        return unique, wiki_link
        
    except Exception:
        return None, None

@st.cache_data(ttl=3600, show_spinner=False)
def get_gbif_taxonomy(scientific_name):
    """透過 GBIF API 取得完整分類階層（快取 1 小時）"""
    try:
        res = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": scientific_name, "verbose": False},
            timeout=6
        ).json()
        return {
            "phylum":    res.get("phylum", ""),
            "class":     res.get("class", ""),
            "order":     res.get("order", ""),
            "family":    res.get("family", ""),
            "genus":     res.get("genus", ""),
            "species":   res.get("species", scientific_name),
            "status":    res.get("status", ""),
            "matchType": res.get("matchType", ""),
        }
    except Exception:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def get_wikipedia_extract(title):
    """取得中文維基百科摘要（前3句，快取 1 小時）"""
    try:
        res = requests.get(
            "https://zh.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "exsentences": 3,
                "titles": title,
                "format": "json",
                "utf8": 1,
                "redirects": 1
            },
            headers={"User-Agent": "PlantExplorer/2.1"},
            timeout=5
        ).json()
        
        for pid, page in res.get("query", {}).get("pages", {}).items():
            if pid != "-1":
                txt = page.get("extract", "").strip()
                if txt and len(txt) > 30:
                    return txt[:350]
    except Exception:
        pass
    return None

def get_confidence_color(score):
    """根據信心指數返回顏色"""
    if score >= 80:
        return "#3fcf6e"
    elif score >= 50:
        return "#c8b864"
    else:
        return "#c86464"

def get_confidence_label(score):
    """根據信心指數返回標籤與表情符號"""
    if score >= 80:
        return "高度吻合", "🟢"
    elif score >= 50:
        return "中度吻合", "🟡"
    else:
        return "低度吻合", "🔴"

def render_confidence_bar(score, color):
    """渲染信心指標條"""
    st.markdown(f"""
    <div class="confidence-bar-wrap">
        <div class="confidence-bar" style="width:{score:.1f}%;background:linear-gradient(90deg,{color}88,{color});"></div>
    </div>
    <p style="color:{color};font-size:0.82rem;margin:0;text-align:right;">{score:.2f}%</p>
    """, unsafe_allow_html=True)

def compress_image(image, max_width=1920):
    """壓縮大尺寸圖片以加快上傳速度"""
    try:
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # 轉換為 RGB（處理 PNG 透明背景）
        if image.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                bg.paste(image, mask=image.split()[-1])
            else:
                bg.paste(image)
            image = bg
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception:
        return image

# ── 分類階層翻譯對照 ──
TAXON_ZH = {
    "Tracheophyta": "維管束植物門", 
    "Magnoliopsida": "木蘭綱（雙子葉）",
    "Liliopsida": "百合綱（單子葉）", 
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
    "Myrtales": "桃金孃目",
    "Gentianales": "龍膽目",
    "Solanales": "茄目",
    "Caryophyllales": "石竹目",
    "Lamiaceae": "唇形科", 
    "Rosaceae": "薔薇科", 
    "Fabaceae": "豆科",
    "Asteraceae": "菊科", 
    "Poaceae": "禾本科", 
    "Moraceae": "桑科",
    "Euphorbiaceae": "大戟科", 
    "Rutaceae": "芸香科", 
    "Meliaceae": "楝科",
    "Apocynaceae": "夾竹桃科", 
    "Rubiaceae": "茜草科",
    "Solanaceae": "茄科",
    "Brassicaceae": "十字花科",
    "Orchidaceae": "蘭科",
    "Araceae": "天南星科",
    "Plantae": "植物界", 
    "Viridiplantae": "綠色植物界",
}

# ── 按科別建立照護資料庫 ──
FAMILY_CARE = {
    "Lamiaceae": {
        "diff": "容易", "diff_c": "#3fcf6e",
        "temp": "-5 ~ 41°C", "zone": "8-10",
        "water": "中等", "fert": "每月一次（生長期）",
        "prune": "冬季、早春", "prop": "扦插",
        "repot": "春季、秋季", "sun": "全日照至半日照"
    },
    "Rosaceae": {
        "diff": "中等", "diff_c": "#c8b864",
        "temp": "-15 ~ 35°C", "zone": "5-9",
        "water": "規律澆水", "fert": "每2週一次",
        "prune": "早春休眠後", "prop": "扦插、嫁接",
        "repot": "春季", "sun": "全日照"
    },
    "Moraceae": {
        "diff": "容易", "diff_c": "#3fcf6e",
        "temp": "10 ~ 38°C", "zone": "9-12",
        "water": "中等", "fert": "每月一次",
        "prune": "冬末", "prop": "扦插",
        "repot": "春季", "sun": "全日照至半日照"
    },
    "Fabaceae": {
        "diff": "容易", "diff_c": "#3fcf6e",
        "temp": "5 ~ 40°C", "zone": "7-11",
        "water": "少量", "fert": "少量（可自行固氮）",
        "prune": "開花後", "prop": "播種",
        "repot": "春季", "sun": "全日照"
    },
    "Asteraceae": {
        "diff": "容易", "diff_c": "#3fcf6e",
        "temp": "0 ~ 35°C", "zone": "6-10",
        "water": "中等", "fert": "每2-4週一次",
        "prune": "花後修剪", "prop": "播種、分株",
        "repot": "春季", "sun": "全日照"
    },
    "Poaceae": {
        "diff": "容易", "diff_c": "#3fcf6e",
        "temp": "-10 ~ 45°C", "zone": "5-12",
        "water": "規律", "fert": "生長期施氮肥",
        "prune": "冬末", "prop": "分株、播種",
        "repot": "春季", "sun": "全日照"
    },
    "Euphorbiaceae": {
        "diff": "容易", "diff_c": "#3fcf6e",
        "temp": "10 ~ 38°C", "zone": "9-12",
        "water": "少量（耐旱）", "fert": "每季一次",
        "prune": "視需要", "prop": "扦插",
        "repot": "春季", "sun": "全日照"
    },
    "Rutaceae": {
        "diff": "中等", "diff_c": "#c8b864",
        "temp": "5 ~ 38°C", "zone": "8-11",
        "water": "規律", "fert": "柑橘專用肥",
        "prune": "春季", "prop": "嫁接、扦插",
        "repot": "春季", "sun": "全日照"
    },
    "Apocynaceae": {
        "diff": "容易", "diff_c": "#3fcf6e",
        "temp": "15 ~ 40°C", "zone": "10-12",
        "water": "少量", "fert": "每月一次",
        "prune": "花後", "prop": "扦插",
        "repot": "春季", "sun": "全日照"
    },
    "Orchidaceae": {
        "diff": "困難", "diff_c": "#c86464",
        "temp": "15 ~ 30°C", "zone": "10-12",
        "water": "少量、高濕度", "fert": "蘭花專用肥",
        "prune": "花後剪花梗", "prop": "分株",
        "repot": "花後", "sun": "散射光"
    },
    "Araceae": {
        "diff": "容易", "diff_c": "#3fcf6e",
        "temp": "15 ~ 35°C", "zone": "10-12",
        "water": "保持濕潤", "fert": "每月一次",
        "prune": "清除枯葉", "prop": "分株、扦插",
        "repot": "春季", "sun": "半日照"
    },
    "DEFAULT": {
        "diff": "中等", "diff_c": "#c8b864",
        "temp": "5 ~ 35°C", "zone": "7-10",
        "water": "中等", "fert": "每月一次",
        "prune": "春季", "prop": "扦插、播種",
        "repot": "春季", "sun": "全日照至半日照"
    },
}

def get_care_info(family):
    """依科別查詢照護建議，找不到時回傳預設值"""
    return FAMILY_CARE.get(family, FAMILY_CARE["DEFAULT"])

def render_taxonomy_section(gbif, display_name, sci_name):
    """渲染分類階層卡片"""
    rows = [
        ("門", gbif.get("phylum", "—")),
        ("綱", gbif.get("class", "—")),
        ("目", gbif.get("order", "—")),
        ("科", gbif.get("family", "—")),
        ("屬", gbif.get("genus", "—")),
        ("種", gbif.get("species", sci_name)),
    ]
    rows_html = ""
    for label, val in rows:
        zh = TAXON_ZH.get(val, "")
        zh_span = f'<span class="taxon-cn">（{zh}）</span>' if zh else ""
        rows_html += f'<tr><td class="taxon-label">{label}</td><td class="taxon-value">{val}{zh_span}</td></tr>'
    
    st.markdown(f"""
    <div class="result-card">
        <div style="color:#5a9a6a;font-size:0.78rem;letter-spacing:0.1em;margin-bottom:0.8rem;">🌳 分類階層</div>
        <div style="font-size:1.1rem;color:#8fd4a0;font-weight:600;margin-bottom:0.3rem;">{display_name}</div>
        <div style="color:#4a7a56;font-style:italic;font-size:0.85rem;margin-bottom:1rem;">{sci_name}</div>
        <table class="taxon-table">{rows_html}</table>
    </div>
    """, unsafe_allow_html=True)

def render_care_section(care, family):
    """渲染照護指南卡片"""
    diff_color = care.get("diff_c", "#c8b864")
    st.markdown(f"""
    <div class="result-card">
        <div style="color:#5a9a6a;font-size:0.78rem;letter-spacing:0.1em;margin-bottom:0.8rem;">🌱 植物照護指南</div>
        <div style="margin-bottom:1rem;">
            <span style="background:{diff_color}22;color:{diff_color};border:1px solid {diff_color}66;
                         border-radius:20px;padding:0.35rem 1.1rem;font-size:0.92rem;font-weight:600;">
                {care.get('diff', '中等')}
            </span>
            <span style="color:#3a6a48;font-size:0.8rem;margin-left:0.8rem;">照護難度（依 {family} 科估算）</span>
        </div>
        <div class="char-card" style="margin-bottom:0.8rem;">
            <div style="color:#5a8a6a;font-size:0.78rem;letter-spacing:0.08em;margin-bottom:0.5rem;">🌡️ 氣候條件</div>
            <div class="char-row"><span class="char-key">適合氣溫</span><span class="char-val">{care.get('temp', '—')}</span></div>
            <div class="char-row"><span class="char-key">耐寒區間</span><span class="char-val">Zone {care.get('zone', '—')}</span></div>
            <div class="char-row"><span class="char-key">光照需求</span><span class="char-val">{care.get('sun', '—')}</span></div>
        </div>
        <div class="care-grid">
            <div class="care-item">
                <div class="care-icon">💧</div>
                <div class="care-title">澆水</div>
                <div class="care-desc">{care.get('water', '—')}</div>
            </div>
            <div class="care-item">
                <div class="care-icon">🌿</div>
                <div class="care-title">肥料</div>
                <div class="care-desc">{care.get('fert', '—')}</div>
            </div>
            <div class="care-item">
                <div class="care-icon">✂️</div>
                <div class="care-title">修剪</div>
                <div class="care-desc">{care.get('prune', '—')}</div>
            </div>
            <div class="care-item">
                <div class="care-icon">🌱</div>
                <div class="care-title">繁殖方式</div>
                <div class="care-desc">{care.get('prop', '—')}</div>
            </div>
            <div class="care-item-wide">
                <div class="care-icon">🪴</div>
                <div class="care-title">翻盆 / 移植</div>
                <div class="care-desc">{care.get('repot', '—')}</div>
            </div>
        </div>
        <p style="color:#2d5040;font-size:0.72rem;margin-top:0.5rem;">
            ※ 照護資料依植物科別估算，實際情況請參考專業文獻
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 側邊欄：辨識歷史與設定
# ==========================================
with st.sidebar:
    st.markdown("## 📋 辨識歷史")
    
    if not st.session_state.history:
        st.markdown('<p style="color:#3a6a48;font-size:0.85rem;">尚無辨識紀錄</p>', unsafe_allow_html=True)
    else:
        # 🔧 安全遍歷歷史記錄，使用 .get() 避免 KeyError
        for i, record in enumerate(reversed(st.session_state.history[-10:])):
            try:
                emoji = record.get('emoji', '🌿')
                name = record.get('name', '未知植物')
                time_str = record.get('time', '—')
                score = record.get('score', 0.0)
                
                # 確保 score 是數字
                if not isinstance(score, (int, float)):
                    score = 0.0
                
                st.markdown(f"""
                <div class="history-item">
                    <span style="font-size:1.5rem;">{emoji}</span>
                    <div style="flex:1;">
                        <div style="font-size:0.88rem;color:#a0d0a8;font-weight:500;">{name}</div>
                        <div style="font-size:0.72rem;color:#4a7a56;">{time_str} · {score:.1f}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                # 忽略任何錯誤的記錄
                continue
    
    st.markdown("---")
    
    if st.session_state.history:
        if st.button("🗑️ 清除所有歷史", use_container_width=True):
            st.session_state.history = []
            st.session_state.total_identifications = 0
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ⚙️ 辨識設定")
    
    top_n = st.slider(
        "顯示候選結果數",
        min_value=1,
        max_value=5,
        value=3,
        help="顯示最多幾個可能的物種"
    )
    
    show_wiki = st.toggle(
        "顯示維基百科連結",
        value=True,
        help="啟用後會顯示維基百科連結"
    )
    
    show_all_names = st.toggle(
        "自動展開所有別名",
        value=False,
        help="預設收合，勾選後自動展開"
    )
    
    st.markdown("---")
    st.markdown("""
    <div style="color:#3a6a48;font-size:0.78rem;line-height:1.8;">
    🌿 <strong style="color:#5a9a68;">生態探索 v2.1</strong><br>
    資料來源：<br>
    · PlantNet API<br>
    · 中文維基百科<br>
    · GBIF 分類資料庫<br>
    <br>
    <small style="color:#2d5040;">
    ※ 本系統僅供參考<br>
    正式鑑定請諮詢專家
    </small>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. 主頁面標題
# ==========================================
st.markdown("# 🌿 生態探索")
st.markdown('<p class="subtitle">植 物 智 能 辨 識 系 統 ｜ Powered by PlantNet AI</p>', unsafe_allow_html=True)

# 統計數據
col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1:
    st.metric("本次已辨識", f"{st.session_state.total_identifications} 種")
with col_stats2:
    if st.session_state.history:
        try:
            scores = [r.get('score', 0) for r in st.session_state.history if isinstance(r.get('score'), (int, float))]
            avg_score = sum(scores) / len(scores) if scores else 0
            st.metric("平均信心度", f"{avg_score:.1f}%")
        except Exception:
            st.metric("平均信心度", "—")
    else:
        st.metric("平均信心度", "—")
with col_stats3:
    st.metric("資料庫涵蓋", "30,000+ 種")

st.markdown("---")

# ==========================================
# 7. 上傳與辨識區
# ==========================================
col_upload, col_preview = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown("### 📸 上傳植物照片")
    st.markdown('''
    <p style="color:#4a7a56;font-size:0.85rem;">
    建議清晰拍攝葉片、花朵或果實特徵以提高辨識準確率
    </p>
    ''', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "拖曳圖片至此，或點擊選擇檔案",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        help="支援 JPG、PNG、WebP 格式，建議大小 < 10MB"
    )
    
    if uploaded_file:
        file_size_kb = uploaded_file.size // 1024
        file_size_mb = file_size_kb / 1024
        
        size_display = f"📦 {file_size_mb:.1f} MB" if file_size_mb >= 1 else f"📦 {file_size_kb} KB"
        st.markdown(f"""
        <div class="badge">📁 {uploaded_file.name}</div>
        <div class="badge">{size_display}</div>
        """, unsafe_allow_html=True)

with col_preview:
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            image = compress_image(image)
            st.image(image, caption="📸 預覽圖片", use_container_width=True)
        except Exception as e:
            st.error(f"❌ 圖片載入失敗：{str(e)}")
            image = None
    else:
        st.markdown("""
        <div style="background:#0a1410;border:1px dashed #1e3820;border-radius:16px;
                    height:280px;display:flex;align-items:center;justify-content:center;
                    flex-direction:column;gap:1rem;">
            <span style="font-size:4rem;">🍃</span>
            <p style="color:#2d5c3a;font-size:0.9rem;text-align:center;">
                上傳照片後<br>預覽將顯示於此
            </p>
        </div>
        """, unsafe_allow_html=True)
        image = None

st.markdown("")
btn_col, _ = st.columns([1, 3])
with btn_col:
    identify_btn = st.button(
        "🔬 開始辨識",
        disabled=(uploaded_file is None),
        use_container_width=True,
        help="點擊開始辨識植物"
    )

# ==========================================
# 8. 辨識執行邏輯
# ==========================================
if identify_btn and uploaded_file and image:
    with st.spinner("🌱 AI 辨識中，同步深度檢索文獻與別名..."):
        
        # 準備圖片資料
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', quality=85)
        img_bytes = img_buffer.getvalue()
        
        files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
        data = {'organs': ['auto']}
        
        # 發送 API 請求
        try:
            response = requests.post(
                API_ENDPOINT,
                files=files,
                data=data,
                timeout=30
            )
            response.raise_for_status()
            
        except requests.exceptions.Timeout:
            st.error("⏱️ 請求逾時（超過30秒），請檢查網路連線。")
            st.info("💡 建議：嘗試使用較小的圖片或檢查網路環境。")
            st.stop()
            
        except requests.exceptions.ConnectionError:
            st.error("🌐 無法連接到 PlantNet 伺服器，請稍後再試。")
            st.stop()
            
        except requests.exceptions.HTTPError:
            if response.status_code == 429:
                st.error("⚠️ API 請求次數已達上限（每日 500 次），請明天再試。")
            elif response.status_code == 401:
                st.error("🔑 API Key 無效或已過期。")
            else:
                st.error(f"❌ HTTP 錯誤：{response.status_code}")
            st.stop()
            
        except Exception as e:
            st.error(f"❌ 未知錯誤：{str(e)}")
            st.stop()
        
        # 解析 API 回應
        try:
            result = response.json()
        except json.JSONDecodeError:
            st.error("❌ API 回應格式錯誤。")
            st.stop()
        
        all_results = result.get('results', [])
        
        if not all_results:
            st.warning("⚠️ 未能辨識出植物，請嘗試以下方法：")
            st.markdown("""
            - 📸 拍攝更清晰的照片
            - 🌸 對準花朵或葉片特徵
            - ☀️ 確保光線充足
            - 🎯 避免複雜背景
            """)
            st.stop()
        
        # ══════════════════════════════════════
        # 辨識成功，處理結果
        # ══════════════════════════════════════
        st.markdown("---")
        st.markdown("## 🎯 辨識結果")
        
        top_results = all_results[:top_n]
        
        # 處理每個候選結果
        for idx, match in enumerate(top_results):
            sci_name = match.get('species', {}).get('scientificNameWithoutAuthor', '未知')
            genus = match.get('species', {}).get('genus', {}).get('scientificNameWithoutAuthor', '')
            family = match.get('species', {}).get('family', {}).get('scientificNameWithoutAuthor', '')
            common_names = match.get('species', {}).get('commonNames', [])
            score = match.get('score', 0) * 100
            
            conf_color = get_confidence_color(score)
            conf_label, conf_emoji = get_confidence_label(score)
            
            # 處理中文名稱
            chinese_list = list(dict.fromkeys([n for n in common_names if has_chinese(n)]))
            wiki_link = None
            
            if not chinese_list:
                wiki_names, wiki_link = search_wikipedia_for_chinese(sci_name)
                if wiki_names:
                    chinese_list = wiki_names
                    name_source = f"維基百科 ({len(chinese_list)} 筆)"
                else:
                    name_source = "無中文資料"
            else:
                name_source = f"PlantNet ({len(chinese_list)} 筆)"
                if show_wiki:
                    _, wiki_link = search_wikipedia_for_chinese(sci_name)
            
            display_name = chinese_list[0] if chinese_list else "【資料不足】"
            card_class = "result-card-best" if idx == 0 else "result-card"
            
            # 加入歷史記錄（僅第一筆）
            if idx == 0:
                st.session_state.history.append({
                    'name': display_name,
                    'sci': sci_name,
                    'score': score,
                    'time': datetime.now().strftime("%H:%M"),
                    'emoji': '🌿'
                })
                st.session_state.total_identifications += 1
            
            # 渲染結果卡片
            with st.container():
                if idx == 0:
                    rank_badge = '<span class="badge badge-gold">✨ 最佳匹配</span>'
                else:
                    rank_badge = f'<span class="badge">候選 #{idx+1}</span>'
                
                genus_html = f"<span style='color:#4a7a56;font-size:0.85rem;'>🌱 屬：{genus}</span>" if genus else ""
                family_html = f"<span style='color:#4a7a56;font-size:0.85rem;'>🌾 科：{family}</span>" if family else ""
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">
                        <div>
                            {rank_badge}
                            <span class="badge">{conf_emoji} {conf_label}</span>
                        </div>
                        <span style="color:#3a6a48;font-size:0.8rem;">{name_source}</span>
                    </div>
                    <div class="plant-name">{display_name}</div>
                    <div class="scientific-name">{sci_name}</div>
                    <div style="display:flex;gap:1.5rem;margin-bottom:1rem;flex-wrap:wrap;">
                        {genus_html}
                        {family_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 信心指標
                st.markdown(f"**信心指標** — `{score:.2f}%`")
                render_confidence_bar(score, conf_color)
                
                # 別名展示
                if len(chinese_list) > 1:
                    with st.expander(
                        f"📖 查看所有別名（共 {len(chinese_list)} 個）",
                        expanded=show_all_names
                    ):
                        cols = st.columns(3)
                        for i, alias in enumerate(chinese_list):
                            star = "⭐ " if i == 0 else ""
                            cols[i % 3].markdown(
                                f'<span class="badge">{star}{alias}</span>',
                                unsafe_allow_html=True
                            )
                
                # Wikipedia 連結
                if show_wiki and wiki_link:
                    st.markdown(
                        f'<a href="{wiki_link}" target="_blank" '
                        f'style="color:#4a9e6f;font-size:0.85rem;text-decoration:none;">'
                        f'📚 在維基百科查看更多資訊 →</a>',
                        unsafe_allow_html=True
                    )
                
                # 英文名稱
                eng_names = [n for n in common_names if not has_chinese(n)][:3]
                if eng_names:
                    st.markdown(
                        f'<p style="color:#3a6058;font-size:0.82rem;margin-top:0.5rem;">'
                        f'英文俗名：{" · ".join(eng_names)}</p>',
                        unsafe_allow_html=True
                    )
                
                if idx < len(top_results) - 1:
                    st.markdown("")
        
        # ══════════════════════════════════════
        # 最佳匹配的深度資訊
        # ══════════════════════════════════════
        best_match = top_results[0]
        best_sci = best_match.get('species', {}).get('scientificNameWithoutAuthor', '')
        best_family = best_match.get('species', {}).get('family', {}).get('scientificNameWithoutAuthor', '')
        best_cn = list(dict.fromkeys([n for n in best_match.get('species', {}).get('commonNames', []) if has_chinese(n)]))
        best_display = best_cn[0] if best_cn else best_sci
        
        st.markdown("---")
        info_col1, info_col2 = st.columns(2, gap="medium")
        
        with info_col1:
            with st.spinner("🔍 載入分類階層..."):
                gbif = get_gbif_taxonomy(best_sci)
            render_taxonomy_section(gbif, best_display, best_sci)
            
            # Wikipedia 摘要
            wiki_title = best_cn[0] if best_cn else best_sci
            extract = get_wikipedia_extract(wiki_title)
            if not extract and best_cn:
                extract = get_wikipedia_extract(best_sci)
            if extract:
                st.markdown(f'<div class="wiki-extract">📖 {extract}</div>', unsafe_allow_html=True)
        
        with info_col2:
            family_for_care = gbif.get("family", best_family) or best_family or "DEFAULT"
            care = get_care_info(family_for_care)
            render_care_section(care, family_for_care)
        
        # ══════════════════════════════════════
        # 匯出與分享
        # ══════════════════════════════════════
        st.markdown("---")
        st.markdown("### 📤 匯出與分享")
        
        best = top_results[0]
        best_sci_export = best.get('species', {}).get('scientificNameWithoutAuthor', '')
        best_score_export = best.get('score', 0) * 100
        best_common_export = list(dict.fromkeys([n for n in best.get('species', {}).get('commonNames', []) if has_chinese(n)]))
        best_name_export = best_common_export[0] if best_common_export else best_sci_export
        
        # 文字報告
        report_text = f"""🌿 植物辨識報告
{'='*40}
辨識時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*40}

【最佳匹配】
中文名稱：{best_name_export}
學　　名：{best_sci_export}
信心指數：{best_score_export:.2f}%
屬：{best.get('species', {}).get('genus', {}).get('scientificNameWithoutAuthor', '—')}
科：{best.get('species', {}).get('family', {}).get('scientificNameWithoutAuthor', '—')}

【所有候選結果】
"""
        for i, m in enumerate(top_results):
            sn = m.get('species', {}).get('scientificNameWithoutAuthor', '')
            sc = m.get('score', 0) * 100
            cn = [n for n in m.get('species', {}).get('commonNames', []) if has_chinese(n)]
            cn_str = cn[0] if cn else sn
            report_text += f"{i+1}. {cn_str}（{sn}）— {sc:.2f}%\n"
        
        report_text += f"\n{'='*40}\n資料來源：PlantNet API + 中文維基百科 + GBIF"
        
        # JSON 資料
        json_data = json.dumps({
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "rank": i+1,
                    "scientific_name": m.get('species', {}).get('scientificNameWithoutAuthor', ''),
                    "common_names": m.get('species', {}).get('commonNames', []),
                    "score": m.get('score', 0),
                    "genus": m.get('species', {}).get('genus', {}).get('scientificNameWithoutAuthor', ''),
                    "family": m.get('species', {}).get('family', {}).get('scientificNameWithoutAuthor', '')
                } for i, m in enumerate(top_results)
            ]
        }, ensure_ascii=False, indent=2)
        
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            st.download_button(
                label="⬇️ 下載文字報告 (.txt)",
                data=report_text.encode("utf-8"),
                file_name=f"植物辨識_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with exp_col2:
            st.download_button(
                label="⬇️ 下載 JSON 資料",
                data=json_data.encode("utf-8"),
                file_name=f"plant_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown("")
        
        # 分享功能
        st.markdown("### 📣 分享結果")
        share_text = f"我用「生態探索」辨識出：{best_name_export}（{best_sci_export}）！準確度 {best_score_export:.1f}%"
        
        share_col1, share_col2, share_col3 = st.columns(3)
        
        with share_col1:
            twitter_url = f"https://twitter.com/intent/tweet?text={quote(share_text)}"
            st.markdown(f"""
                <a href="{twitter_url}" target="_blank" class="share-btn" 
                   style="background:#1DA1F2;color:white;">
                    🐦 分享到 Twitter
                </a>
            """, unsafe_allow_html=True)
        
        with share_col2:
            fb_url = f"https://www.facebook.com/sharer/sharer.php?quote={quote(share_text)}"
            st.markdown(f"""
                <a href="{fb_url}" target="_blank" class="share-btn" 
                   style="background:#4267B2;color:white;">
                    📘 分享到 Facebook
                </a>
            """, unsafe_allow_html=True)
        
        with share_col3:
            if st.button("📋 複製辨識結果", use_container_width=True):
                st.code(share_text, language=None)
                st.success("✅ 已顯示文字，請手動複製")

# ==========================================
# 9. 底部說明
# ==========================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#2d5c3a;font-size:0.8rem;padding:1rem 0;line-height:2;">
    🌿 <strong style="color:#4a7a56;">生態探索 Plant Explorer</strong> v2.1<br>
    植物辨識 by PlantNet AI · 別名擴充 by 中文維基百科 · 分類資料 by GBIF<br>
    <span style="font-size:0.72rem;">本系統僅供參考，物種鑑定請諮詢專業植物學家</span>
</div>
""", unsafe_allow_html=True)
