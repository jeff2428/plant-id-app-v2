import streamlit as st
import requests
import re
from PIL import Image
from datetime import datetime

# ==========================================
# 頁面設定
# ==========================================
st.set_page_config(
    page_title="🌿 植物辨識系統",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS 樣式
# ==========================================
def load_css():
    css = '''
    :root {
        --font-size-hero-title: 2.8em;
        --font-size-hero-subtitle: 1.15em;
        --padding-card: 30px;
        --padding-hero: 40px 30px;
        --border-radius: 20px;
    }

    .stApp {
        background: linear-gradient(160deg, #e8f5e9 0%, #f1f8e9 30%, #fff8e1 70%, #e8f5e9 100%);
    }

    #MainMenu, footer, header {visibility: hidden;}

    /* ========================================
       上傳區塊美化（核心修改）
       ======================================== */

    /* 隱藏 Streamlit 內建副文字 */
    section[data-testid="stFileUploader"] small,
    section[data-testid="stCameraInput"] small {
        display: none !important;
    }

    /* 上傳區域外框 — 綠色虛線卡片 */
    section[data-testid="stFileUploader"] > div > div {
        border: 3px dashed #81c784 !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, rgba(232,245,233,0.6), rgba(241,248,233,0.6)) !important;
        padding: 30px 20px !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* 滑鼠懸停效果 */
    section[data-testid="stFileUploader"] > div > div:hover {
        border-color: #2e7d32 !important;
        background: linear-gradient(135deg, rgba(200,230,201,0.8), rgba(220,237,200,0.8)) !important;
        box-shadow: 0 8px 30px rgba(46,125,50,0.15) !important;
        transform: translateY(-2px) !important;
    }

    /* Label 樣式（上傳區標題） */
    section[data-testid="stFileUploader"] label {
        font-size: 1.15em !important;
        font-weight: 700 !important;
        color: #2e7d32 !important;
        text-align: center !important;
        display: block !important;
        margin-bottom: 10px !important;
    }

    /* Browse 按鈕 — 綠色漸層膠囊 */
    section[data-testid="stFileUploader"] section button {
        background: linear-gradient(135deg, #2e7d32, #43a047) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 12px 40px !important;
        font-weight: 700 !important;
        font-size: 1em !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(46,125,50,0.35) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        margin-top: 10px !important;
    }

    /* 按鈕懸停 */
    section[data-testid="stFileUploader"] section button:hover {
        background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
        box-shadow: 0 6px 25px rgba(46,125,50,0.5) !important;
        transform: translateY(-2px) !important;
    }

    /* 按鈕按下 */
    section[data-testid="stFileUploader"] section button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 10px rgba(46,125,50,0.3) !important;
    }

    /* 上傳區內的分隔線隱藏 */
    section[data-testid="stFileUploader"] hr {
        display: none !important;
    }

    /* 相機輸入美化 */
    section[data-testid="stCameraInput"] > div > div {
        border: 3px dashed #81c784 !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, rgba(232,245,233,0.6), rgba(241,248,233,0.6)) !important;
        padding: 30px 20px !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
    }

    section[data-testid="stCameraInput"] > div > div:hover {
        border-color: #2e7d32 !important;
        box-shadow: 0 8px 30px rgba(46,125,50,0.15) !important;
    }

    section[data-testid="stCameraInput"] label {
        font-size: 1.15em !important;
        font-weight: 700 !important;
        color: #2e7d32 !important;
        text-align: center !important;
        display: block !important;
    }

    /* ========================================
       其他元件樣式
       ======================================== */

    .hero-container {
        background: linear-gradient(135deg, #1b5e20, #2e7d32, #388e3c, #43a047, #66bb6a);
        border-radius: var(--border-radius);
        padding: var(--padding-hero);
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(27,94,32,0.3);
    }

    .hero-title {
        color: white;
        font-size: var(--font-size-hero-title);
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        line-height: 1.2;
    }

    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: var(--font-size-hero-subtitle);
        line-height: 1.5;
        margin-top: 10px;
    }

    .tip-card {
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border-left: 5px solid #43a047;
        border-radius: 0 12px 12px 0;
        padding: 18px 22px;
        margin: 12px 0;
        color: #2e7d32;
    }

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
        to   { opacity: 1; transform: translateY(0); }
    }

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
    }

    .stat-card {
        background: white;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 3px 15px rgba(0,0,0,0.06);
        transition: transform 0.2s;
    }

    .stat-card:hover {
        transform: translateY(-3px);
    }

    .stat-number {
        font-size: 2em;
        font-weight: 800;
        color: #2e7d32;
    }

    .stat-label {
        color: #757575;
        font-size: 0.9em;
        margin-top: 4px;
    }

    .history-item {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 12px 15px;
        margin: 8px 0;
        border-left: 3px solid #81c784;
        font-size: 0.9em;
    }

    .stButton > button {
        background: linear-gradient(135deg, #2e7d32, #43a047) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 35px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(46,125,50,0.3) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #1b5e20, #2e7d32) !important;
        transform: translateY(-2px);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 100%);
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }

    @media screen and (max-width: 767px) {
        :root {
            --font-size-hero-title: 1.8em;
            --font-size-hero-subtitle: 0.95em;
            --padding-card: 20px;
            --padding-hero: 30px 20px;
        }
        section[data-testid="stFileUploader"] > div > div {
            padding: 20px 15px !important;
        }
        section[data-testid="stFileUploader"] section button {
            padding: 10px 30px !important;
            font-size: 0.9em !important;
        }
    }

    @media screen and (max-width: 480px) {
        :root {
            --font-size-hero-title: 1.5em;
            --font-size-hero-subtitle: 0.85em;
            --padding-card: 15px;
        }
    }
    '''
    st.markdown('<style>' + css + '</style>', unsafe_allow_html=True)

load_css()

# ==========================================
# API 設定
# ==========================================
API_KEY = st.secrets.get("PLANTNET_API_KEY", "2b1004UqTrbWJn4mj5hqcaZN")
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

ORGAN_MAP = {
    "🤖 自動判斷": "auto",
    "🌸 花朵": "flower",
    "🍃 葉片": "leaf",
    "🍎 果實": "fruit",
    "🌳 樹皮": "bark",
}

# ==========================================
# Session State
# ==========================================
if "history" not in st.session_state:
    st.session_state.history = []
if "total_scans" not in st.session_state:
    st.session_state.total_scans = 0

# ==========================================
# 核心功能
# ==========================================
def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search_wikipedia_for_chinese(scientific_name):
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    headers = {"User-Agent": "PlantIdentifierApp/1.0 (Educational)"}
    try:
        params = {
            "action": "query",
            "titles": scientific_name,
            "prop": "redirects",
            "rdlimit": "50",
            "format": "json"
        }
        res = requests.get(wiki_url, params=params, headers=headers, timeout=8).json()
        pages = res.get("query", {}).get("pages", {})
        page_id = next(iter(pages))

        if page_id != "-1":
            page = pages[page_id]
            aliases = []
            main_title = page.get("title", "")
            if has_chinese(main_title):
                aliases.append(main_title)
            for rd in page.get("redirects", []):
                title = rd.get("title", "")
                if ":" not in title and has_chinese(title):
                    aliases.append(title)
            if aliases:
                return list(dict.fromkeys(aliases))

        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": scientific_name,
            "srlimit": 3,
            "format": "json"
        }
        search_res = requests.get(wiki_url, params=search_params, headers=headers, timeout=8).json()
        for result in search_res.get("query", {}).get("search", []):
            title = result.get("title", "")
            if has_chinese(title):
                return [title]
    except Exception:
        pass
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
# 側邊欄
# ==========================================
with st.sidebar:
    st.markdown("## 🌿 控制面板")
    st.markdown("---")

    st.markdown("### 📸 拍攝部位")
    selected_organ_label = st.selectbox(
        "選擇植物部位",
        list(ORGAN_MAP.keys()),
        label_visibility="collapsed"
    )
    selected_organ = ORGAN_MAP[selected_organ_label]

    st.markdown("---")
    st.markdown("### 📈 使用統計")
    st.metric("辨識次數", st.session_state.total_scans)

    st.markdown("---")
    st.markdown("### 🕐 辨識紀錄")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(
                '<div class="history-item">'
                '<b>' + item['name'] + '</b><br>'
                '<small>' + item['time'] + ' | ' + str(round(item['score'], 1)) + '%</small>'
                '</div>',
                unsafe_allow_html=True
            )
        if st.button("🗑️ 清除紀錄"):
            st.session_state.history = []
            st.session_state.total_scans = 0
            st.rerun()
    else:
        st.info("尚無紀錄")

    st.markdown("---")
    st.markdown("### ℹ️ 關於")
    st.markdown(
        '<small>'
        '🔬 引擎：Pl@ntNet API<br>'
        '📚 資料：維基百科<br>'
        '🛠️ 框架：Streamlit<br>'
        '📌 版本：2.3.0'
        '</small>',
        unsafe_allow_html=True
    )

# ==========================================
# 主頁面
# ==========================================
st.markdown(
    '<div class="hero-container">'
    '<div class="hero-title">🌿 生態探索：植物辨識系統</div>'
    '<div class="hero-subtitle">'
    '上傳一張植物照片，AI 為你辨識物種、查詢中文名稱與生態資料'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# 統計卡片
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        '<div class="stat-card">'
        '<div class="stat-number">45,000+</div>'
        '<div class="stat-label">可辨識物種</div>'
        '</div>',
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        '<div class="stat-card">'
        '<div class="stat-number">🔬</div>'
        '<div class="stat-label">AI 深度學習</div>'
        '</div>',
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        '<div class="stat-card">'
        '<div class="stat-number">📚</div>'
        '<div class="stat-label">維基百科擴充</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 上傳區塊（已美化）
# ==========================================
input_method = st.radio(
    "選擇來源",
    ["📁 從相簿選擇", "📷 開啟相機"],
    horizontal=True,
    label_visibility="collapsed"
)

uploaded_file = None
if input_method == "📁 從相簿選擇":
    uploaded_file = st.file_uploader(
        "🌿 點擊上傳或拖放植物照片",
        type=["jpg", "jpeg", "png"]
    )
else:
    cam = st.camera_input("📷 點擊拍攝植物照片")
    if cam:
        uploaded_file = cam

st.markdown(
    '<div class="tip-card">'
    '💡 <b>拍攝小技巧：</b>'
    '盡量讓主體清晰、背景單純，建議分別拍攝葉片、花朵、果實等特徵部位。'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# 辨識邏輯
# ==========================================
if uploaded_file:
    image = Image.open(uploaded_file)

    col_img = st.columns([1, 2, 1])
    with col_img[1]:
        st.image(image, caption="📸 已上傳照片", use_container_width=True)

    col_btn = st.columns([1, 1, 1])
    with col_btn[1]:
        if st.button("🔍  開始辨識", use_container_width=True):
            progress = st.progress(0, text="🌱 正在連接 AI...")

            try:
                progress.progress(30, text="📡 上傳圖片中...")

                img_bytes = uploaded_file.getvalue()
                files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
                data = {'organs': [selected_organ]}

                progress.progress(60, text="🤖 AI 分析中...")

                response = requests.post(API_ENDPOINT, files=files, data=data, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    results = result.get('results', [])

                    if results:
                        progress.progress(90, text="📚 查詢中文名稱...")

                        best = results[0]
                        sci_name = best['species']['scientificNameWithoutAuthor']
                        common = best['species'].get('commonNames', [])
                        score = best['score'] * 100
                        family = best['species'].get('family', {}).get('scientificNameWithoutAuthor', '未知')

                        cn_list = [n for n in common if has_chinese(n)]
                        if cn_list:
                            name = cn_list[0]
                            source = "PlantNet 圖鑑"
                        else:
                            wiki = search_wikipedia_for_chinese(sci_name)
                            if wiki:
                                name = wiki[0]
                                source = "維基百科"
                            else:
                                name = sci_name
                                source = "無中文資料"

                        progress.progress(100, text="✅ 完成！")
                        progress.empty()

                        st.session_state.total_scans += 1
                        st.session_state.history.append({
                            "name": name,
                            "score": score,
                            "time": datetime.now().strftime("%H:%M")
                        })

                        color = get_confidence_color(score)
                        label = get_confidence_label(score)

                        st.markdown(
                            '<div class="result-card">'
                            '<h2 style="text-align:center; color:#2e7d32; margin-bottom:5px;">'
                            '🎯 辨識結果'
                            '</h2>'
                            '<h1 style="text-align:center; color:#1b5e20; margin:10px 0; font-size:2em;">'
                            + name +
                            '</h1>'
                            '<p style="text-align:center; color:#616161; font-size:1.1em;">'
                            '<i>' + sci_name + '</i>'
                            '</p>'
                            '<div class="confidence-bar-bg">'
                            '<div class="confidence-bar-fill" style="width:' + str(score) + '%; background:' + color + ';">'
                            + str(round(score, 1)) + '% ' + label +
                            '</div>'
                            '</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        col_info1, col_info2 = st.columns(2)
                        with col_info1:
                            st.markdown("#### 🧬 分類資訊")
                            st.markdown("- **科：** " + family)
                            st.markdown("- **學名：** *" + sci_name + "*")
                            st.markdown("- **來源：** " + source)

                        with col_info2:
                            st.markdown("#### 🔗 延伸資訊")
                            if has_chinese(name):
                                wiki_link = "https://zh.wikipedia.org/wiki/" + name
                                st.markdown("[📖 查看維基百科](" + wiki_link + ")")
                            search_link = "https://www.google.com/search?q=" + sci_name + "+植物"
                            st.markdown("[🔍 Google 搜尋](" + search_link + ")")

                        st.success("✅ 辨識完成！")

                    else:
                        progress.empty()
                        st.error("❌ 無法辨識此圖片，請嘗試更換照片或拍攝角度")
                else:
                    progress.empty()
                    st.error("❌ API 連線失敗（狀態碼：" + str(response.status_code) + "）")

            except requests.exceptions.Timeout:
                progress.empty()
                st.error("❌ 請求超時，請檢查網路連線")
            except Exception as e:
                progress.empty()
                st.error("❌ 發生錯誤：" + str(e))

# 頁尾
st.markdown(
    '<div style="text-align:center; padding:30px; color:#9e9e9e; font-size:0.85em; margin-top:40px;">'
    '🌿 植物辨識系統 v2.3 ｜ Powered by Pl@ntNet &amp; Wikipedia<br>'
    'Made with 💚 for nature lovers'
    '</div>',
    unsafe_allow_html=True
)
