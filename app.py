import streamlit as st
import requests
import re
from PIL import Image
import io
import base64
import json
from datetime import datetime

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

/* ── 統一桌機／手機上傳按鈕：消除原生文字，注入自訂標籤 ── */
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
@media (max-width: 768px) {
    [data-testid="stFileUploader"] {
        padding: 1rem !important;
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

/* ── Info / Success / Warning ── */
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
.taxon-table { width:100%; border-collapse:collapse; margin:0.5rem 0; }
.taxon-table tr { border-bottom:1px solid #1a3020; }
.taxon-table tr:last-child { border-bottom:none; }
.taxon-table td { padding:0.65rem 0.5rem; font-size:0.88rem; }
.taxon-label { color:#5a8a6a; width:60px; font-weight:500; }
.taxon-value { color:#c0e0c8; font-style:italic; }
.taxon-cn { color:#7ec98a; font-style:normal; margin-left:0.5rem; font-size:0.82rem; }

/* ── 特徵 & 照護卡片 ── */
.char-card { background:#0e1a12; border:1px solid #1e3824; border-radius:14px; padding:1.2rem 1.4rem; margin:0.8rem 0; }
.char-row { display:flex; justify-content:space-between; align-items:center; padding:0.55rem 0; border-bottom:1px solid #1a2e1e; font-size:0.87rem; }
.char-row:last-child { border-bottom:none; }
.char-key { color:#5a8a6a; }
.char-val { color:#b0d8b8; font-weight:500; }
.care-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; margin:0.8rem 0; }
.care-item { background:#0e1a12; border:1px solid #1e3824; border-radius:12px; padding:1rem 1.1rem; }
.care-item-wide { grid-column:1/-1; background:#0e1a12; border:1px solid #1e3824; border-radius:12px; padding:1rem 1.1rem; }
.care-icon { font-size:1.4rem; margin-bottom:0.3rem; }
.care-title { color:#7ec98a; font-size:0.82rem; font-weight:600; margin-bottom:0.2rem; }
.care-desc { color:#90b898; font-size:0.85rem; }
.wiki-extract { background:#0c1810; border-left:3px solid #2d6a40; border-radius:0 10px 10px 0; padding:0.9rem 1.2rem; color:#8ab898; font-size:0.85rem; line-height:1.8; margin:0.8rem 0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API 設定
# ==========================================
API_KEY = "2b1004UqTrbWJn4mj5hqcaZN"
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# ==========================================
# 3. Session State 初始化
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================
# 4. 核心工具函數
# ==========================================
def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search_wikipedia_for_chinese(scientific_name):
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    headers = {"User-Agent": "PlantExplorer/2.0"}
    try:
        search_res = requests.get(wiki_url, params={
            "action": "query", "list": "search",
            "srsearch": scientific_name, "format": "json", "utf8": 1
        }, headers=headers, timeout=5).json()
        results = search_res.get("query", {}).get("search", [])
        if not results:
            return None, None
        main_title = results[0].get("title", "")
        if not has_chinese(main_title):
            return None, None
        rd_res = requests.get(wiki_url, params={
            "action": "query", "titles": main_title,
            "prop": "redirects", "rdlimit": "50",
            "format": "json", "utf8": 1
        }, headers=headers, timeout=5).json()
        pages = rd_res.get("query", {}).get("pages", {})
        aliases = [main_title]
        for _, page_info in pages.items():
            for rd in page_info.get("redirects", []):
                t = rd["title"]
                if ":" not in t and has_chinese(t):
                    aliases.append(t)
        unique = list(dict.fromkeys(aliases))
        wiki_link = f"https://zh.wikipedia.org/wiki/{main_title.replace(' ', '_')}"
        return unique, wiki_link
    except Exception:
        return None, None

def get_confidence_color(score):
    if score >= 80:
        return "#3fcf6e"
    elif score >= 50:
        return "#c8b864"
    else:
        return "#c86464"

def get_confidence_label(score):
    if score >= 80:
        return "高度吻合", "🟢"
    elif score >= 50:
        return "中度吻合", "🟡"
    else:
        return "低度吻合", "🔴"

def image_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def render_confidence_bar(score, color):
    st.markdown(f"""
    <div class="confidence-bar-wrap">
        <div class="confidence-bar" style="width:{score:.1f}%;background:linear-gradient(90deg,{color}88,{color});"></div>
    </div>
    <p style="color:{color};font-size:0.82rem;margin:0;text-align:right;">{score:.2f}%</p>
    """, unsafe_allow_html=True)

# ── 分類階層翻譯對照 ──
TAXON_ZH = {
    "Tracheophyta": "維管束植物門", "Magnoliopsida": "木蘭綱（雙子葉）",
    "Liliopsida": "百合綱（單子葉）", "Pinopsida": "松綱",
    "Lamiales": "唇形目", "Rosales": "薔薇目", "Fabales": "豆目",
    "Asterales": "菊目", "Poales": "禾本目", "Malpighiales": "金虎尾目",
    "Sapindales": "無患子目", "Malvales": "錦葵目", "Myrtales": "桃金孃目",
    "Lamiaceae": "唇形科", "Rosaceae": "薔薇科", "Fabaceae": "豆科",
    "Asteraceae": "菊科", "Poaceae": "禾本科", "Moraceae": "桑科",
    "Euphorbiaceae": "大戟科", "Rutaceae": "芸香科", "Meliaceae": "楝科",
    "Apocynaceae": "夾竹桃科", "Rubiaceae": "茜草科",
    "Plantae": "植物界", "Viridiplantae": "綠色植物界",
}

# ── 按科別建立照護資料庫 ──
FAMILY_CARE = {
    "Lamiaceae":    {"diff":"容易","diff_c":"#3fcf6e","temp":"-5 ~ 41°C","zone":"8-10","water":"中等","fert":"每月一次（生長期）","prune":"冬季、早春","prop":"扦插","repot":"春季、秋季","sun":"全日照至半日照"},
    "Rosaceae":     {"diff":"中等","diff_c":"#c8b864","temp":"-15 ~ 35°C","zone":"5-9","water":"規律澆水","fert":"每2週一次","prune":"早春休眠後","prop":"扦插、嫁接","repot":"春季","sun":"全日照"},
    "Moraceae":     {"diff":"容易","diff_c":"#3fcf6e","temp":"10 ~ 38°C","zone":"9-12","water":"中等","fert":"每月一次","prune":"冬末","prop":"扦插","repot":"春季","sun":"全日照至半日照"},
    "Fabaceae":     {"diff":"容易","diff_c":"#3fcf6e","temp":"5 ~ 40°C","zone":"7-11","water":"少量","fert":"少量（可自行固氮）","prune":"開花後","prop":"播種","repot":"春季","sun":"全日照"},
    "Asteraceae":   {"diff":"容易","diff_c":"#3fcf6e","temp":"0 ~ 35°C","zone":"6-10","water":"中等","fert":"每2-4週一次","prune":"花後修剪","prop":"播種、分株","repot":"春季","sun":"全日照"},
    "Poaceae":      {"diff":"容易","diff_c":"#3fcf6e","temp":"-10 ~ 45°C","zone":"5-12","water":"規律","fert":"生長期施氮肥","prune":"冬末","prop":"分株、播種","repot":"春季","sun":"全日照"},
    "Euphorbiaceae":{"diff":"容易","diff_c":"#3fcf6e","temp":"10 ~ 38°C","zone":"9-12","water":"少量（耐旱）","fert":"每季一次","prune":"視需要","prop":"扦插","repot":"春季","sun":"全日照"},
    "Rutaceae":     {"diff":"中等","diff_c":"#c8b864","temp":"5 ~ 38°C","zone":"8-11","water":"規律","fert":"柑橘專用肥","prune":"春季","prop":"嫁接、扦插","repot":"春季","sun":"全日照"},
    "Apocynaceae":  {"diff":"容易","diff_c":"#3fcf6e","temp":"15 ~ 40°C","zone":"10-12","water":"少量","fert":"每月一次","prune":"花後","prop":"扦插","repot":"春季","sun":"全日照"},
    "DEFAULT":      {"diff":"中等","diff_c":"#c8b864","temp":"5 ~ 35°C","zone":"7-10","water":"中等","fert":"每月一次","prune":"春季","prop":"扦插、播種","repot":"春季","sun":"全日照至半日照"},
}

def get_gbif_taxonomy(scientific_name):
    """透過 GBIF API 取得完整分類階層"""
    try:
        res = requests.get(
            "https://api.gbif.org/v1/species/match",
            params={"name": scientific_name, "verbose": False},
            timeout=6
        ).json()
        return {
            "phylum":   res.get("phylum", ""),
            "class":    res.get("class", ""),
            "order":    res.get("order", ""),
            "family":   res.get("family", ""),
            "genus":    res.get("genus", ""),
            "species":  res.get("species", scientific_name),
            "status":   res.get("status", ""),
            "matchType":res.get("matchType", ""),
        }
    except Exception:
        return {}

def get_wikipedia_extract(title):
    """取得中文維基百科前3句摘要"""
    try:
        res = requests.get(
            "https://zh.wikipedia.org/w/api.php",
            params={"action":"query","prop":"extracts","exintro":True,
                    "explaintext":True,"exsentences":3,
                    "titles":title,"format":"json","utf8":1,"redirects":1},
            headers={"User-Agent":"PlantExplorer/2.0"},
            timeout=5
        ).json()
        for pid, page in res.get("query",{}).get("pages",{}).items():
            if pid != "-1":
                txt = page.get("extract","").strip()
                if txt and len(txt) > 30:
                    return txt[:350]
    except Exception:
        pass
    return None

def get_care_info(family):
    """依科別查詢照護建議，找不到時回傳預設值"""
    return FAMILY_CARE.get(family, FAMILY_CARE["DEFAULT"])

def render_taxonomy_section(gbif, display_name, sci_name):
    """渲染分類階層卡片"""
    rows = [
        ("門", gbif.get("phylum","—")),
        ("綱", gbif.get("class","—")),
        ("目", gbif.get("order","—")),
        ("科", gbif.get("family","—")),
        ("屬", gbif.get("genus","—")),
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
    diff_color = care["diff_c"]
    st.markdown(f"""
    <div class="result-card">
        <div style="color:#5a9a6a;font-size:0.78rem;letter-spacing:0.1em;margin-bottom:0.8rem;">🌱 植物照護指南</div>
        <div style="margin-bottom:1rem;">
            <span style="background:{diff_color}22;color:{diff_color};border:1px solid {diff_color}66;
                         border-radius:20px;padding:0.35rem 1.1rem;font-size:0.92rem;font-weight:600;">
                {care['diff']}
            </span>
            <span style="color:#3a6a48;font-size:0.8rem;margin-left:0.8rem;">照護難度（依 {family} 科估算）</span>
        </div>
        <div class="char-card" style="margin-bottom:0.8rem;">
            <div style="color:#5a8a6a;font-size:0.78rem;letter-spacing:0.08em;margin-bottom:0.5rem;">🌡️ 氣候條件</div>
            <div class="char-row"><span class="char-key">適合氣溫</span><span class="char-val">{care['temp']}</span></div>
            <div class="char-row"><span class="char-key">耐寒區間</span><span class="char-val">Zone {care['zone']}</span></div>
            <div class="char-row"><span class="char-key">光照需求</span><span class="char-val">{care['sun']}</span></div>
        </div>
        <div class="care-grid">
            <div class="care-item">
                <div class="care-icon">💧</div>
                <div class="care-title">澆水</div>
                <div class="care-desc">{care['water']}</div>
            </div>
            <div class="care-item">
                <div class="care-icon">🌿</div>
                <div class="care-title">肥料</div>
                <div class="care-desc">{care['fert']}</div>
            </div>
            <div class="care-item">
                <div class="care-icon">✂️</div>
                <div class="care-title">修剪</div>
                <div class="care-desc">{care['prune']}</div>
            </div>
            <div class="care-item">
                <div class="care-icon">🌱</div>
                <div class="care-title">繁殖方式</div>
                <div class="care-desc">{care['prop']}</div>
            </div>
            <div class="care-item-wide">
                <div class="care-icon">🪴</div>
                <div class="care-title">翻盆 / 移植</div>
                <div class="care-desc">{care['repot']}</div>
            </div>
        </div>
        <p style="color:#2d5040;font-size:0.72rem;margin-top:0.5rem;">
            ※ 照護資料依植物科別估算，實際情況請參考專業文獻
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 側邊欄：辨識歷史
# ==========================================
with st.sidebar:
    st.markdown("## 📋 辨識歷史")
    if not st.session_state.history:
        st.markdown('<p style="color:#3a6a48;font-size:0.85rem;">尚無辨識紀錄</p>', unsafe_allow_html=True)
    else:
        for i, record in enumerate(reversed(st.session_state.history)):
            st.markdown(f"""
            <div class="history-item">
                <span style="font-size:1.5rem;">{record['emoji']}</span>
                <div>
                    <div style="font-size:0.88rem;color:#a0d0a8;font-weight:500;">{record['name']}</div>
                    <div style="font-size:0.72rem;color:#4a7a56;">{record['time']} · {record['score']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.history and st.button("🗑️ 清除歷史"):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ 辨識設定")
    top_n = st.slider("顯示候選結果數", 1, 5, 3)
    show_wiki = st.toggle("顯示維基百科連結", value=True)
    show_all_names = st.toggle("展開所有別名", value=False)

    st.markdown("---")
    st.markdown("""
    <div style="color:#3a6a48;font-size:0.78rem;line-height:1.8;">
    🌿 <strong style="color:#5a9a68;">生態探索</strong><br>
    資料來源：PlantNet API<br>
    別名擴充：中文維基百科<br>
    v2.0 · 深色自然系
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. 主頁面標題
# ==========================================
st.markdown("# 🌿 生態探索")
st.markdown('<p class="subtitle">植 物 智 能 辨 識 系 統 ｜ Powered by PlantNet AI</p>', unsafe_allow_html=True)

col_stats1, col_stats2, col_stats3 = st.columns(3)
with col_stats1:
    st.metric("本次已辨識", f"{len(st.session_state.history)} 種")
with col_stats2:
    avg_score = (sum(r['score'] for r in st.session_state.history) / len(st.session_state.history)) if st.session_state.history else 0
    st.metric("平均信心度", f"{avg_score:.1f}%" if avg_score else "—")
with col_stats3:
    st.metric("資料庫涵蓋", "30,000+ 種")

st.markdown("---")

# ==========================================
# 7. 上傳與辨識區
# ==========================================
col_upload, col_preview = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown("### 📸 上傳植物照片")
    st.markdown('<p style="color:#4a7a56;font-size:0.85rem;">建議清晰拍攝葉片、花朵或果實特徵以提高辨識準確率</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "拖曳圖片至此，或點擊選擇檔案",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.markdown(f"""
        <div class="badge">📁 {uploaded_file.name}</div>
        <div class="badge">{uploaded_file.size // 1024} KB</div>
        """, unsafe_allow_html=True)

with col_preview:
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="預覽", use_container_width=True)
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

st.markdown("")
btn_col, _ = st.columns([1, 3])
with btn_col:
    identify_btn = st.button("🔬 開始辨識", disabled=uploaded_file is None, use_container_width=True)

# ==========================================
# 8. 辨識執行邏輯
# ==========================================
if identify_btn and uploaded_file:
    with st.spinner("🌱 AI 辨識中，同步深度檢索文獻與別名..."):
        img_bytes = uploaded_file.getvalue()
        files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
        data = {'organs': ['auto']}
        
        try:
            response = requests.post(API_ENDPOINT, files=files, data=data, timeout=30)
        except requests.exceptions.Timeout:
            st.error("⏱️ 請求逾時，請檢查網路連線後再試。")
            st.stop()
        except Exception as e:
            st.error(f"❌ 網路錯誤：{e}")
            st.stop()
        
        if response.status_code != 200:
            st.error(f"❌ 辨識失敗（HTTP {response.status_code}），請確認 API Key 是否正確。")
            st.stop()
        
        result = response.json()
        all_results = result.get('results', [])
        
        if not all_results:
            st.warning("⚠️ 未能辨識出植物，請嘗試更清晰的照片。")
            st.stop()
        
        # ── 最佳結果 ──
        st.markdown("---")
        st.markdown("## 🎯 辨識結果")
        
        top_results = all_results[:top_n]
        
        for idx, match in enumerate(top_results):
            sci_name = match['species']['scientificNameWithoutAuthor']
            genus = match['species'].get('genus', {}).get('scientificNameWithoutAuthor', '')
            family = match['species'].get('family', {}).get('scientificNameWithoutAuthor', '')
            common_names = match['species'].get('commonNames', [])
            score = match['score'] * 100
            
            conf_color = get_confidence_color(score)
            conf_label, conf_emoji = get_confidence_label(score)
            
            # ── 處理中文名稱 ──
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
            
            display_name = chinese_list[0] if chinese_list else "【資料不足，無法確認】"
            card_class = "result-card-best" if idx == 0 else "result-card"
            
            # ── 加入歷史（僅第一筆）──
            if idx == 0:
                st.session_state.history.append({
                    "name": display_name,
                    "sci": sci_name,
                    "score": score,
                    "time": datetime.now().strftime("%H:%M"),
                    "emoji": "🌿"
                })
            
            with st.container():
                if idx == 0:
                    rank_badge = '<span class="badge badge-gold">✨ 最佳匹配</span>'
                else:
                    rank_badge = f'<span class="badge">候選 #{idx+1}</span>'
                
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
                        {"<span style='color:#4a7a56;font-size:0.85rem;'>🌱 屬：" + genus + "</span>" if genus else ""}
                        {"<span style='color:#4a7a56;font-size:0.85rem;'>🌾 科：" + family + "</span>" if family else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 信心指標（用 Streamlit 元件避免 HTML 執行問題）
                st.markdown(f"**信心指標** — `{score:.2f}%`")
                render_confidence_bar(score, conf_color)
                
                # ── 別名展示 ──
                if len(chinese_list) > 1:
                    with st.expander(f"📖 查看所有別名（共 {len(chinese_list)} 個）", expanded=show_all_names):
                        cols = st.columns(3)
                        for i, alias in enumerate(chinese_list):
                            cols[i % 3].markdown(f'<span class="badge">{"⭐ " if i==0 else ""}{alias}</span>', unsafe_allow_html=True)
                
                # ── Wikipedia 連結 ──
                if show_wiki and wiki_link:
                    st.markdown(f'<a href="{wiki_link}" target="_blank" style="color:#4a9e6f;font-size:0.85rem;text-decoration:none;">📚 在維基百科查看更多資訊 →</a>', unsafe_allow_html=True)
                
                # ── 非學名英文名 ──
                eng_names = [n for n in common_names if not has_chinese(n)][:3]
                if eng_names:
                    st.markdown(f'<p style="color:#3a6058;font-size:0.82rem;margin-top:0.5rem;">英文俗名：{" · ".join(eng_names)}</p>', unsafe_allow_html=True)
                
                if idx < len(top_results) - 1:
                    st.markdown("")
        
        # ══════════════════════════════════════
        # 最佳匹配的深度資訊（分類 + 照護）
        # ══════════════════════════════════════
        best_match = top_results[0]
        best_sci   = best_match['species']['scientificNameWithoutAuthor']
        best_family= best_match['species'].get('family', {}).get('scientificNameWithoutAuthor', '')
        best_cn    = list(dict.fromkeys([n for n in best_match['species'].get('commonNames',[]) if has_chinese(n)]))
        best_display = best_cn[0] if best_cn else best_sci
        
        st.markdown("---")
        info_col1, info_col2 = st.columns(2, gap="medium")
        
        with info_col1:
            # ── 取得 GBIF 完整分類 ──
            with st.spinner("🔍 載入分類階層..."):
                gbif = get_gbif_taxonomy(best_sci)
            render_taxonomy_section(gbif, best_display, best_sci)
            
            # ── Wikipedia 摘要 ──
            wiki_title = best_cn[0] if best_cn else best_sci
            extract = get_wikipedia_extract(wiki_title)
            if not extract and best_cn:
                extract = get_wikipedia_extract(best_sci)
            if extract:
                st.markdown(f'<div class="wiki-extract">📖 {extract}</div>', unsafe_allow_html=True)
        
        with info_col2:
            # ── 照護指南 ──
            family_for_care = gbif.get("family", best_family) or best_family or "DEFAULT"
            care = get_care_info(family_for_care)
            render_care_section(care, family_for_care)
        
        # ── 匯出功能 ──
        st.markdown("---")
        st.markdown("### 📤 匯出辨識報告")
        
        best = top_results[0]
        best_sci = best['species']['scientificNameWithoutAuthor']
        best_score = best['score'] * 100
        best_common = list(dict.fromkeys([n for n in best['species'].get('commonNames', []) if has_chinese(n)]))
        best_name = best_common[0] if best_common else best_sci
        
        report_text = f"""🌿 植物辨識報告
{'='*40}
辨識時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*40}

【最佳匹配】
中文名稱：{best_name}
學　　名：{best_sci}
信心指數：{best_score:.2f}%
屬：{best['species'].get('genus', {}).get('scientificNameWithoutAuthor', '—')}
科：{best['species'].get('family', {}).get('scientificNameWithoutAuthor', '—')}

【所有候選結果】
"""
        for i, m in enumerate(top_results):
            sn = m['species']['scientificNameWithoutAuthor']
            sc = m['score'] * 100
            cn = [n for n in m['species'].get('commonNames', []) if has_chinese(n)]
            cn_str = cn[0] if cn else sn
            report_text += f"{i+1}. {cn_str}（{sn}）— {sc:.2f}%\n"
        
        report_text += f"\n{'='*40}\n資料來源：PlantNet API + 中文維基百科"
        
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
            json_data = json.dumps({
                "timestamp": datetime.now().isoformat(),
                "results": [
                    {
                        "rank": i+1,
                        "scientific_name": m['species']['scientificNameWithoutAuthor'],
                        "common_names": m['species'].get('commonNames', []),
                        "score": m['score'],
                        "genus": m['species'].get('genus', {}).get('scientificNameWithoutAuthor', ''),
                        "family": m['species'].get('family', {}).get('scientificNameWithoutAuthor', '')
                    } for i, m in enumerate(top_results)
                ]
            }, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ 下載 JSON 資料",
                data=json_data.encode("utf-8"),
                file_name=f"plant_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )

# ==========================================
# 9. 底部說明
# ==========================================
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#2d5c3a;font-size:0.8rem;padding:1rem 0;line-height:2;">
    🌿 <strong style="color:#4a7a56;">生態探索 Plant Explorer</strong> v2.0<br>
    植物辨識 by PlantNet AI · 別名擴充 by 中文維基百科<br>
    <span style="font-size:0.72rem;">本系統僅供參考，物種鑑定請諮詢專業植物學家</span>
</div>
""", unsafe_allow_html=True)
