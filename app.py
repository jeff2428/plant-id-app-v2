import streamlit as st
import requests
import re
from PIL import Image
import io
from datetime import datetime

# ==========================================
# 1. 頁面基礎設定
# ==========================================
st.set_page_config(
    page_title="🌿 植物辨識系統",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 自訂 CSS 美化樣式 (含響應式設計)
# ==========================================
st.markdown("""
<style>
/* ========================================
   基礎變數設定 (CSS Variables)
   ======================================== */
:root {
    --font-size-hero-title: 2.8em;
    --font-size-hero-subtitle: 1.15em;
    --font-size-section-title: 1.5em;
    --font-size-body: 1em;
    --font-size-small: 0.9em;
    --font-size-stat-number: 2em;
    --font-size-button: 1.1em;
    --font-size-result-name: 2.2em;
    --font-size-result-sci: 1.1em;
    --padding-card: 30px;
    --padding-hero: 40px 30px;
    --border-radius: 20px;
    --spacing-section: 30px;
}

/* ========================================
   全域背景與基礎設定
   ======================================== */
.stApp {
    background: linear-gradient(160deg, #e8f5e9 0%, #f1f8e9 30%, #fff8e1 70%, #e8f5e9 100%);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ========================================
   主標題區塊 (Hero)
   ======================================== */
.hero-container {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 25%, #388e3c 50%, #43a047 75%, #66bb6a 100%);
    border-radius: var(--border-radius);
    padding: var(--padding-hero);
    text-align: center;
    margin-bottom: var(--spacing-section);
    box-shadow: 0 10px 40px rgba(27,94,32,0.3);
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: shimmer 8s ease-in-out infinite;
}

@keyframes shimmer {
    0%, 100% { transform: translate(-30%, -30%) rotate(0deg); }
    50% { transform: translate(10%, 10%) rotate(180deg); }
}

.hero-title {
    color: white;
    font-size: var(--font-size-hero-title);
    font-weight: 800;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    position: relative;
    z-index: 1;
    line-height: 1.2;
}

.hero-subtitle {
    color: rgba(255,255,255,0.9);
    font-size: var(--font-size-hero-subtitle);
    position: relative;
    z-index: 1;
    line-height: 1.5;
}

/* ========================================
   上傳區塊
   ======================================== */
.upload-section {
    background: white;
    border-radius: 16px;
    padding: var(--padding-card);
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 2px dashed #a5d6a7;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}

.upload-section:hover {
    border-color: #43a047;
    box-shadow: 0 6px 30px rgba(67,160,71,0.15);
}

.upload-section h3 {
    font-size: var(--font-size-section-title);
}

.upload-section p {
    font-size: var(--font-size-small);
}

/* ========================================
   提示小卡
   ======================================== */
.tip-card {
    background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
    border-left: 5px solid #43a047;
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    margin: 12px 0;
    font-size: var(--font-size-small);
    color: #2e7d32;
    line-height: 1.6;
}

/* ========================================
   辨識結果主卡片
   ======================================== */
.result-card {
    background: white;
    border-radius: var(--border-radius);
    padding: var(--padding-card);
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    border-top: 5px solid #43a047;
    margin: 20px 0;
    animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.result-card h2 {
    font-size: var(--font-size-section-title);
}

.result-card h1 {
    font-size: var(--font-size-result-name);
    word-break: keep-all;
    overflow-wrap: break-word;
}

.result-card .scientific-name {
    font-size: var(--font-size-result-sci);
}

/* ========================================
   信心指數條
   ======================================== */
.confidence-bar-bg {
    background: #e0e0e0;
    border-radius: 12px;
    height: 28px;
    overflow: hidden;
    margin: 8px 0;
}

.confidence-bar-fill {
    height: 100%;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 0.85em;
    transition: width 1s ease-out;
    white-space: nowrap;
    padding: 0 10px;
}

/* ========================================
   候選清單項目
   ======================================== */
.candidate-card {
    background: #fafafa;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 10px 0;
    border-left: 4px solid #81c784;
    transition: all 0.2s ease;
    font-size: var(--font-size-body);
}

.candidate-card:hover {
    background: #f1f8e9;
    transform: translateX(5px);
}

.candidate-card b {
    font-size: 1.05em;
    display: block;
    margin-bottom: 5px;
}

.candidate-card i {
    font-size: var(--font-size-small);
    word-break: break-all;
}

/* ========================================
   統計資訊小卡
   ======================================== */
.stat-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 3px 15px rgba(0,0,0,0.06);
    transition: transform 0.2s;
    min-height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.stat-card:hover {
    transform: translateY(-3px);
}

.stat-number {
    font-size: var(--font-size-stat-number);
    font-weight: 800;
    color: #2e7d32;
}

.stat-label {
    color: #757575;
    font-size: var(--font-size-small);
    margin-top: 4px;
}

/* ========================================
   歷史紀錄項目
   ======================================== */
.history-item {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 12px 15px;
    margin: 8px 0;
    border-left: 3px solid #81c784;
    transition: background 0.2s;
    font-size: var(--font-size-small);
}

.history-item:hover {
    background: rgba(255,255,255,0.2);
}

/* ========================================
   頁尾
   ======================================== */
.custom-footer {
    text-align: center;
    padding: 30px 15px;
    color: #9e9e9e;
    font-size: var(--font-size-small);
    margin-top: 40px;
    line-height: 1.8;
}

/* ========================================
   Streamlit 元件微調
   ======================================== */
.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #43a047);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 35px;
    font-size: var(--font-size-button);
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(46,125,50,0.3);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    box-shadow: 0 6px 25px rgba(46,125,50,0.4);
    transform: translateY(-2px);
    color: white;
}

div[data-testid="stFileUploader"] {
    background: transparent;
}

/* ========================================
   側邊欄樣式
   ======================================== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 100%);
}

section[data-testid="stSidebar"] .stMarkdown {
    color: white;
}

section[data-testid="stSidebar"] label {
    color: white !important;
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-size: 1.1em !important;
}

/* ==========================================
   📱 響應式設計 - 平板 (768px - 1024px)
   ========================================== */
@media screen and (max-width: 1024px) {
    :root {
        --font-size-hero-title: 2.2em;
        --font-size-hero-subtitle: 1.05em;
        --font-size-section-title: 1.3em;
        --font-size-body: 0.95em;
        --font-size-small: 0.85em;
        --font-size-stat-number: 1.7em;
        --font-size-button: 1em;
        --font-size-result-name: 1.9em;
        --font-size-result-sci: 1em;
        --padding-card: 25px;
        --padding-hero: 35px 25px;
        --spacing-section: 25px;
    }
    
    .hero-container {
        border-radius: 16px;
    }
    
    .stat-card {
        padding: 15px;
        min-height: 90px;
    }
    
    .confidence-bar-bg {
        height: 24px;
    }
    
    .confidence-bar-fill {
        font-size: 0.8em;
    }
    
    .candidate-card {
        padding: 15px 18px;
    }
}

/* ==========================================
   📱 響應式設計 - 大手機 (481px - 767px)
   ========================================== */
@media screen and (max-width: 767px) {
    :root {
        --font-size-hero-title: 1.8em;
        --font-size-hero-subtitle: 0.95em;
        --font-size-section-title: 1.2em;
        --font-size-body: 0.9em;
        --font-size-small: 0.8em;
        --font-size-stat-number: 1.5em;
        --font-size-button: 0.95em;
        --font-size-result-name: 1.6em;
        --font-size-result-sci: 0.95em;
        --padding-card: 20px;
        --padding-hero: 30px 20px;
        --border-radius: 16px;
        --spacing-section: 20px;
    }
    
    .hero-container {
        border-radius: 14px;
        margin-left: 5px;
        margin-right: 5px;
    }
    
    .hero-title {
        line-height: 1.3;
    }
    
    .stat-card {
        padding: 12px;
        min-height: 80px;
        border-radius: 10px;
    }
    
    .upload-section {
        padding: 20px 15px;
        border-radius: 12px;
    }
    
    .result-card {
        padding: 20px 15px;
        border-radius: 14px;
    }
    
    .confidence-bar-bg {
        height: 22px;
    }
    
    .confidence-bar-fill {
        font-size: 0.75em;
        padding: 0 8px;
    }
    
    .candidate-card {
        padding: 14px 16px;
        border-radius: 10px;
    }
    
    .candidate-card b {
        font-size: 1em;
    }
    
    .tip-card {
        padding: 14px 16px;
        font-size: 0.85em;
    }
    
    .history-item {
        padding: 10px 12px;
        font-size: 0.8em;
    }
    
    .custom-footer {
        padding: 20px 10px;
        font-size: 0.8em;
    }
    
    .stButton > button {
        padding: 10px 25px;
        border-radius: 10px;
    }
}

/* ==========================================
   📱 響應式設計 - 小手機 (≤480px)
   ========================================== */
@media screen and (max-width: 480px) {
    :root {
        --font-size-hero-title: 1.5em;
        --font-size-hero-subtitle: 0.85em;
        --font-size-section-title: 1.1em;
        --font-size-body: 0.85em;
        --font-size-small: 0.75em;
        --font-size-stat-number: 1.3em;
        --font-size-button: 0.9em;
        --font-size-result-name: 1.4em;
        --font-size-result-sci: 0.85em;
        --padding-card: 15px;
        --padding-hero: 25px 15px;
        --border-radius: 12px;
        --spacing-section: 15px;
    }
    
    .hero-container {
        border-radius: 12px;
        margin: 0 3px;
        padding: 20px 12px;
    }
    
    .hero-title {
        font-size: 1.4em;
        line-height: 1.35;
        margin-bottom: 8px;
    }
    
    .hero-subtitle {
        font-size: 0.85em;
        line-height: 1.5;
        padding: 0 5px;
    }
    
    .stat-card {
        padding: 10px 8px;
        min-height: 70px;
        border-radius: 8px;
    }
    
    .stat-number {
        font-size: 1.2em;
    }
    
    .stat-label {
        font-size: 0.7em;
    }
    
    .upload-section {
        padding: 15px 12px;
        border-radius: 10px;
    }
    
    .upload-section h3 {
        font-size: 1.1em !important;
    }
    
    .upload-section p {
        font-size: 0.8em !important;
    }
    
    .result-card {
        padding: 15px 12px;
        border-radius: 12px;
        margin: 15px 0;
    }
    
    .result-card h2 {
        font-size: 1.1em !important;
    }
    
    .result-card h1 {
        font-size: 1.35em !important;
        margin: 8px 0 !important;
    }
    
    .confidence-bar-bg {
        height: 20px;
        border-radius: 10px;
    }
    
    .confidence-bar-fill {
        font-size: 0.7em;
        padding: 0 6px;
        border-radius: 10px;
    }
    
    .candidate-card {
        padding: 12px 14px;
        border-radius: 8px;
        margin: 8px 0;
    }
    
    .candidate-card b {
        font-size: 0.95em;
    }
    
    .candidate-card i {
        font-size: 0.75em;
    }
    
    .candidate-card .confidence-bar-bg {
        height: 16px;
    }
    
    .candidate-card .confidence-bar-fill {
        font-size: 0.65em;
    }
    
    .tip-card {
        padding: 12px 14px;
        font-size: 0.8em;
        border-left-width: 4px;
        border-radius: 0 10px 10px 0;
        line-height: 1.5;
    }
    
    .history-item {
        padding: 8px 10px;
        font-size: 0.75em;
        border-radius: 8px;
    }
    
    .custom-footer {
        padding: 15px 10px;
        font-size: 0.75em;
        margin-top: 25px;
    }
    
    .stButton > button {
        padding: 10px 20px;
        font-size: 0.9em;
        border-radius: 10px;
    }
    
    /* 側邊欄手機版調整 */
    section[data-testid="stSidebar"] {
        min-width: 250px !important;
    }
    
    section[data-testid="stSidebar"] h2 {
        font-size: 1em !important;
    }
    
    section[data-testid="stSidebar"] h3 {
        font-size: 0.9em !important;
    }
}

/* ==========================================
   📱 超小螢幕 (≤360px)
   ========================================== */
@media screen and (max-width: 360px) {
    .hero-title {
        font-size: 1.25em;
    }
    
    .hero-subtitle {
        font-size: 0.78em;
    }
    
    .stat-number {
        font-size: 1.1em;
    }
    
    .stat-label {
        font-size: 0.65em;
    }
    
    .result-card h1 {
        font-size: 1.2em !important;
    }
    
    .tip-card {
        font-size: 0.75em;
        padding: 10px 12px;
    }
    
    .confidence-bar-fill {
        font-size: 0.65em;
    }
}

/* ==========================================
   🖥️ 大螢幕優化 (≥1400px)
   ========================================== */
@media screen and (min-width: 1400px) {
    :root {
        --font-size-hero-title: 3.2em;
        --font-size-hero-subtitle: 1.25em;
        --font-size-section-title: 1.6em;
        --font-size-body: 1.05em;
        --font-size-stat-number: 2.3em;
        --font-size-result-name: 2.5em;
        --font-size-result-sci: 1.2em;
        --padding-card: 35px;
        --padding-hero: 50px 40px;
    }
    
    .hero-container {
        border-radius: 24px;
    }
    
    .stat-card {
        padding: 25px;
        border-radius: 16px;
    }
    
    .result-card {
        border-radius: 24px;
    }
}

/* ==========================================
   🖨️ 列印樣式
   ========================================== */
@media print {
    .stApp {
        background: white !important;
    }
    
    .hero-container {
        background: #2e7d32 !important;
        box-shadow: none !important;
    }
    
    .hero-container::before {
        display: none;
    }
    
    .stat-card, .result-card, .candidate-card {
        box-shadow: none !important;
        border: 1px solid #ddd !important;
    }
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    .stButton {
        display: none !important;
    }
}

/* ==========================================
   🌙 系統深色模式支援 (可選)
   ========================================== */
@media (prefers-color-scheme: dark) {
    /* 若需要支援深色模式，可在此添加樣式 */
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. API 與全域常數
# ==========================================
API_KEY = "2b1004UqTrbWJn4mj5hqcaZN"
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

ORGAN_MAP = {
    "🤖 自動判斷": "auto",
    "🌸 花朵": "flower",
    "🍃 葉片": "leaf",
    "🍎 果實": "fruit",
    "🌳 樹皮": "bark",
    "🌱 整株習性": "habit",
}

# ==========================================
# 4. Session State 初始化
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []
if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0
if "species_found" not in st.session_state:
    st.session_state.species_found = set()

# ==========================================
# 5. 核心功能函數
# ==========================================
def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search_wikipedia_for_chinese(scientific_name):
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    search_params = {
        "action": "query", "list": "search",
        "srsearch": scientific_name, "format": "json", "utf8": 1
    }
    try:
        search_res = requests.get(wiki_url, params=search_params, headers=headers).json()
        results = search_res.get("query", {}).get("search", [])
        if not results:
            return None
        main_title = results[0].get("title", "")
        if not has_chinese(main_title):
            return None
        rd_params = {
            "action": "query", "titles": main_title,
            "prop": "redirects", "rdlimit": "50",
            "format": "json", "utf8": 1
        }
        rd_res = requests.get(wiki_url, params=rd_params, headers=headers).json()
        pages = rd_res.get("query", {}).get("pages", {})
        aliases = [main_title]
        for pid, pinfo in pages.items():
            if "redirects" in pinfo:
                for rd in pinfo["redirects"]:
                    t = rd["title"]
                    if ":" not in t and has_chinese(t):
                        aliases.append(t)
        return list(dict.fromkeys(aliases))
    except:
        return None

def search_wiki_summary(title):
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {
        "action": "query", "titles": title,
        "prop": "extracts", "exintro": True,
        "explaintext": True, "format": "json", "utf8": 1
    }
    try:
        res = requests.get(wiki_url, params=params, headers=headers).json()
        pages = res.get("query", {}).get("pages", {})
        for pid, pinfo in pages.items():
            extract = pinfo.get("extract", "")
            if extract:
                sentences = extract.split("。")
                short = "。".join(sentences[:4])
                return short + "。" if short else None
        return None
    except:
        return None

def get_confidence_color(score):
    if score >= 80:
        return "#2e7d32"
    elif score >= 50:
        return "#f9a825"
    else:
        return "#c62828"

def get_confidence_label(score):
    if score >= 80:
        return "✅ 高度吻合"
    elif score >= 50:
        return "⚠️ 中度吻合"
    else:
        return "❓ 低度吻合"

# ==========================================
# 6. 側邊欄 (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("## 🌿 控制面板")
    st.markdown("---")
    
    st.markdown("### 📸 拍攝部位")
    selected_organ_label = st.selectbox(
        "選擇植物拍攝部位",
        list(ORGAN_MAP.keys()),
        index=0,
        label_visibility="collapsed"
    )
    selected_organ = ORGAN_MAP[selected_organ_label]
    
    st.markdown("")
    st.markdown("### 📊 候選數量")
    top_k = st.slider("", 1, 5, 3, label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### 📈 使用統計")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("辨識次數", st.session_state.total_scans)
    with col_s2:
        st.metric("發現物種", len(st.session_state.species_found))
    
    st.markdown("---")
    st.markdown("### 🕐 辨識紀錄")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-10:]):
            st.markdown(
                f"""<div class="history-item">
                    <b>{item['name']}</b><br>
                    <small>🔬 {item['scientific']}</small><br>
                    <small>📅 {item['time']} ｜ 🎯 {item['score']:.1f}%</small>
                </div>""",
                unsafe_allow_html=True
            )
        if st.button("🗑️ 清除紀錄"):
            st.session_state.history = []
            st.session_state.total_scans = 0
            st.session_state.species_found = set()
            st.rerun()
    else:
        st.info("尚無紀錄")
    
    st.markdown("---")
    st.markdown("### ℹ️ 關於")
    st.markdown(
        """<small>
        🔬 辨識引擎：Pl@ntNet<br>
        📚 中文資料：維基百科<br>
        📌 版本：2.1.0
        </small>""",
        unsafe_allow_html=True
    )

# ==========================================
# 7. 主頁面 — Hero 區塊
# ==========================================
st.markdown(
    """<div class="hero-container">
        <div class="hero-title">🌿 生態探索：植物辨識系統</div>
        <div class="hero-subtitle">
            上傳一張植物照片，AI 為你辨識物種、查詢中文名稱與生態資料
        </div>
    </div>""",
    unsafe_allow_html=True
)

# ==========================================
# 8. 統計小卡
# ==========================================
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """<div class="stat-card">
            <div class="stat-number">45,000+</div>
            <div class="stat-label">可辨識物種</div>
        </div>""",
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        """<div class="stat-card">
            <div class="stat-number">🔬</div>
            <div class="stat-label">AI 深度學習</div>
        </div>""",
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        """<div class="stat-card">
            <div class="stat-number">📚</div>
            <div class="stat-label">維基百科擴充</div>
        </div>""",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 9. 圖片上傳區塊
# ==========================================
st.markdown(
    """<div class="upload-section">
        <h3 style="text-align:center; color:#2e7d32; margin-bottom:5px;">
            📤 上傳植物照片
        </h3>
        <p style="text-align:center; color:#757575;">
            支援 JPG、JPEG、PNG 格式
        </p>
    </div>""",
    unsafe_allow_html=True
)

input_method = st.radio(
    "選擇圖片來源",
    ["📁 上傳圖片", "📷 相機拍照"],
    horizontal=True,
    label_visibility="collapsed"
)

uploaded_file = None
if input_method == "📁 上傳圖片":
    uploaded_file = st.file_uploader(
        "選擇圖片", type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )
else:
    cam_photo = st.camera_input("拍攝植物照片", label_visibility="collapsed")
    if cam_photo:
        uploaded_file = cam_photo

st.markdown(
    """<div class="tip-card">
        💡 <b>拍攝小技巧：</b>
        盡量讓主體清晰、背景單純，建議分別拍攝
        <b>葉片、花朵、果實、樹皮</b>等特徵部位。
    </div>""",
    unsafe_allow_html=True
)

# ==========================================
# 10. 辨識主邏輯與分頁呈現
# ==========================================
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col_img_l, col_img_c, col_img_r = st.columns([1, 2, 1])
    with col_img_c:
        st.image(image, caption="📸 已上傳照片", use_container_width=True)
    
    col_btn_l, col_btn_c, col_btn_r = st.columns([1, 1, 1])
    with col_btn_c:
        start = st.button("🔍  開始辨識", use_container_width=True)
    
    if start:
        progress = st.progress(0, text="🌱 正在連接 AI 辨識引擎...")
        progress.progress(20, text="📡 上傳影像資料中...")
        
        img_bytes = uploaded_file.getvalue()
        files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
        data = {'organs': [selected_organ]}
        
        response = requests.post(API_ENDPOINT, files=files, data=data)
        progress.progress(50, text="🤖 AI 模型分析中...")
        
        if response.status_code == 200:
            result = response.json()
            all_results = result.get('results', [])
            
            if not all_results:
                st.error("❌ 無法辨識此圖片，請嘗試更換照片。")
            else:
                progress.progress(70, text="📚 檢索中文名稱...")
                
                best = all_results[0]
                sci_name = best['species']['scientificNameWithoutAuthor']
                common_names = best['species'].get('commonNames', [])
                score = best['score'] * 100
                family = best['species'].get('family', {}).get('scientificNameWithoutAuthor', '未知')
                genus = best['species'].get('genus', {}).get('scientificNameWithoutAuthor', '未知')
                
                cn_list = [n for n in common_names if has_chinese(n)]
                cn_list = list(dict.fromkeys(cn_list))
                source = ""
                wiki_summary = None
                
                if cn_list:
                    display_name = cn_list[0]
                    all_names = "、".join(cn_list)
                    source = f"PlantNet 圖鑑（{len(cn_list)} 筆）"
                else:
                    wiki_result = search_wikipedia_for_chinese(sci_name)
                    if wiki_result:
                        display_name = wiki_result[0]
                        all_names = "、".join(wiki_result)
                        source = f"維基百科擴充（{len(wiki_result)} 筆）"
                    else:
                        display_name = sci_name
                        all_names = "無中文資料"
                        source = "無資料"
                
                if display_name and has_chinese(display_name):
                    wiki_summary = search_wiki_summary(display_name)
                
                progress.progress(100, text="✅ 辨識完成！")
                import time; time.sleep(0.3)
                progress.empty()
                
                st.session_state.total_scans += 1
                st.session_state.species_found.add(sci_name)
                st.session_state.history.append({
                    "name": display_name,
                    "scientific": sci_name,
                    "score": score,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "family": family,
                })
                
                conf_color = get_confidence_color(score)
                conf_label = get_confidence_label(score)
                
                st.markdown(
                    f"""<div class="result-card">
                        <h2 style="text-align:center; color:#2e7d32; margin-bottom:5px;">
                            🎯 辨識結果
                        </h2>
                        <h1 style="text-align:center; color:#1b5e20; margin:10px 0;">
                            {display_name}
                        </h1>
                        <p class="scientific-name" style="text-align:center; color:#616161;">
                            <i>{sci_name}</i>
                        </p>
                        <div class="confidence-bar-bg">
                            <div class="confidence-bar-fill"
                                 style="width:{score}%; background:{conf_color};">
                                {score:.1f}% {conf_label}
                            </div>
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ==========================================
                # 大眾通用版 - 進階分頁結構
                # ==========================================
                tab_overview, tab_care, tab_usage = st.tabs(["📝 總覽資訊", "🌱 養護指南", "⚠️ 安全與用途"])
                
                # [分頁 1]：總覽資訊
                with tab_overview:
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.markdown(f'<div class="stat-card" style="min-height:80px; padding:15px;"><div class="stat-label">科 (Family)</div><div class="stat-number" style="font-size:1.5em; color:#1b5e20;">{family}</div></div>', unsafe_allow_html=True)
                    with col_dl2:
                        st.markdown(f'<div class="stat-card" style="min-height:80px; padding:15px;"><div class="stat-label">屬 (Genus)</div><div class="stat-number" style="font-size:1.5em; color:#1b5e20;">{genus}</div></div>', unsafe_allow_html=True)
                    
                    st.markdown("#### 📖 植物簡介")
                    if wiki_summary:
                        st.info(wiki_summary)
                        if has_chinese(display_name):
                            wiki_link = f"https://zh.wikipedia.org/wiki/{display_name}"
                            st.markdown(f"[🔗 查看維基百科完整條目]({wiki_link})")
                    else:
                        st.write("暫無中文簡介。")
                        search_link = f"https://www.google.com/search?q={sci_name}+植物"
                        st.markdown(f"[🔍 使用 Google 搜尋相關資訊]({search_link})")
                        
                    st.markdown(f"**中文來源：** {source}")
                    if all_names != "無中文資料":
                        st.markdown(f"**所有已知別名：** {all_names}")

                # [分頁 2]：植物養護指南 (大眾版位預留)
                with tab_care:
                    st.info("💡 **功能解鎖提示：** 此區塊未來可整合植物養護資料庫，提供精準照護建議。")
                    with st.expander("💧 基礎養護條件 (展示範例)", expanded=True):
                        st.write("- **日照需求**：全日照 / 半日照")
                        st.write("- **澆水頻率**：土乾澆透 (預設)")
                        st.write("- **適宜溫度**：15°C - 30°C")
                    with st.expander("✂️ 種植與修剪 (展示範例)"):
                        st.write("- **生長週期**：多年生 / 一年生")
                        st.write("- **修剪建議**：春季或花期後進行")

                # [分頁 3]：安全警示與常見用途 (大眾版位預留)
                with tab_usage:
                    st.warning("⚠️ **野外接觸與採集注意：** 在野外遇到不熟悉的植物時，請避免隨意觸碰或摘食，以免發生過敏或中毒。")
                    with st.expander("🛡️ 毒性與安全性 (展示範例)", expanded=True):
                        st.write("- **寵物友善**：(待資料庫建檔)")
                        st.write("- **人體毒性**：(待資料庫建檔)")
                    with st.expander("💡 常見生活用途 (展示範例)"):
                        st.write("- **園藝觀賞**：適合庭院造景或室內盆栽")
                        st.write("- **其他用途**：(待資料庫建檔)")
                
                # ==========================================
                # 其他可能物種與報告下載
                # ==========================================
                if len(all_results) > 1 and top_k > 1:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 🏅 其他可能物種")
                    
                    for idx, res in enumerate(all_results[1:top_k], start=2):
                        r_sci = res['species']['scientificNameWithoutAuthor']
                        r_score = res['score'] * 100
                        r_cn = res['species'].get('commonNames', [])
                        r_cn_zh = [n for n in r_cn if has_chinese(n)]
                        r_display = r_cn_zh[0] if r_cn_zh else r_sci
                        r_color = get_confidence_color(r_score)
                        
                        st.markdown(
                            f"""<div class="candidate-card">
                                <b>#{idx}　{r_display}</b>
                                <i style="color:#757575;">{r_sci}</i>
                                <div class="confidence-bar-bg" style="height:18px; margin-top:8px;">
                                    <div class="confidence-bar-fill"
                                         style="width:{r_score}%; background:{r_color};
                                                font-size:0.75em; height:100%;">
                                        {r_score:.1f}%
                                    </div>
                                </div>
                            </div>""",
                            unsafe_allow_html=True
                        )
                
                st.markdown("---")
                report_lines = [
                    "=" * 40,
                    "  🌿 植物辨識報告",
                    "=" * 40,
                    f"辨識時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    f"中文名稱：{display_name}",
                    f"學　　名：{sci_name}",
                    f"科　　別：{family}",
                    f"屬　　別：{genus}",
                    f"信心指數：{score:.2f}%",
                    f"中文來源：{source}",
                    f"所有名稱：{all_names}",
                    "",
                    "📖 植物簡介：",
                    wiki_summary if wiki_summary else "無資料",
                ]
                report_text = "\n".join(report_lines)
                
                col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
                with col_dl2:
                    st.download_button(
                        label="📄 下載報告",
                        data=report_text,
                        file_name=f"plant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
        else:
            progress.empty()
            st.error(f"❌ API 連線失敗（{response.status_code}）")

# ==========================================
# 11. 頁尾
# ==========================================
st.markdown(
    """<div class="custom-footer">
        🌿 植物辨識系統 v2.1 ｜ Powered by Pl@ntNet & Wikipedia
        <br>
        Made with 💚 for nature lovers
    </div>""",
    unsafe_allow_html=True
)
