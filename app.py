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
# 2. 自訂 CSS 美化樣式
# ==========================================
st.markdown("""
<style>
/* ===== 全域背景 ===== */
.stApp {
    background: linear-gradient(160deg, #e8f5e9 0%, #f1f8e9 30%, #fff8e1 70%, #e8f5e9 100%);
}

/* ===== 隱藏預設元素 ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ===== 主標題區塊 ===== */
.hero-container {
    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 25%, #388e3c 50%, #43a047 75%, #66bb6a 100%);
    border-radius: 20px;
    padding: 40px 30px;
    text-align: center;
    margin-bottom: 30px;
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
    font-size: 2.8em;
    font-weight: 800;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    position: relative;
    z-index: 1;
}
.hero-subtitle {
    color: rgba(255,255,255,0.9);
    font-size: 1.15em;
    position: relative;
    z-index: 1;
}

/* ===== 上傳區塊 ===== */
.upload-section {
    background: white;
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 2px dashed #a5d6a7;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}
.upload-section:hover {
    border-color: #43a047;
    box-shadow: 0 6px 30px rgba(67,160,71,0.15);
}

/* ===== 提示小卡 ===== */
.tip-card {
    background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
    border-left: 5px solid #43a047;
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    margin: 12px 0;
    font-size: 0.95em;
    color: #2e7d32;
}

/* ===== 辨識結果主卡片 ===== */
.result-card {
    background: white;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    border-top: 5px solid #43a047;
    margin: 20px 0;
    animation: slideUp 0.5s ease-out;
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ===== 信心指數條 ===== */
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

/* ===== 候選清單項目 ===== */
.candidate-card {
    background: #fafafa;
    border-radius: 12px;
    padding: 18px 22px;
    margin: 10px 0;
    border-left: 4px solid #81c784;
    transition: all 0.2s ease;
}
.candidate-card:hover {
    background: #f1f8e9;
    transform: translateX(5px);
}

/* ===== 側邊欄歷史紀錄 ===== */
.history-item {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 12px 15px;
    margin: 8px 0;
    border-left: 3px solid #81c784;
    transition: background 0.2s;
}
.history-item:hover {
    background: rgba(255,255,255,0.2);
}

/* ===== 統計資訊小卡 ===== */
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

/* ===== 器官選擇按鈕組 ===== */
.organ-btn {
    display: inline-block;
    padding: 8px 18px;
    margin: 4px;
    border-radius: 20px;
    font-size: 0.9em;
    cursor: pointer;
    transition: all 0.2s;
}

/* ===== 頁尾 ===== */
.custom-footer {
    text-align: center;
    padding: 30px;
    color: #9e9e9e;
    font-size: 0.85em;
    margin-top: 40px;
}

/* ===== Streamlit 元件微調 ===== */
.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #43a047);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 35px;
    font-size: 1.1em;
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

/* ===== 側邊欄樣式 ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 100%);
}
section[data-testid="stSidebar"] .stMarkdown {
    color: white;
}
section[data-testid="stSidebar"] label {
    color: white !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label {
    color: white !important;
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
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
    """取得維基百科摘要（前兩段）"""
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

    # 器官選擇
    st.markdown("### 📸 拍攝部位")
    selected_organ_label = st.selectbox(
        "請選擇植物拍攝部位以提升準確度",
        list(ORGAN_MAP.keys()),
        index=0,
        label_visibility="collapsed"
    )
    selected_organ = ORGAN_MAP[selected_organ_label]

    st.markdown("")

    # 顯示幾筆結果
    st.markdown("### 📊 顯示候選數量")
    top_k = st.slider("", 1, 5, 3, label_visibility="collapsed")

    st.markdown("---")

    # 使用統計
    st.markdown("### 📈 使用統計")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("辨識次數", st.session_state.total_scans)
    with col_s2:
        st.metric("發現物種", len(st.session_state.species_found))

    st.markdown("---")

    # 歷史紀錄
    st.markdown("### 🕐 辨識紀錄")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
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
        st.info("尚無紀錄，快來辨識第一株植物吧！")

    st.markdown("---")
    st.markdown("### ℹ️ 關於")
    st.markdown(
        """<small>
        🔬 辨識引擎：Pl@ntNet API<br>
        📚 中文資料：維基百科<br>
        🛠️ 介面框架：Streamlit<br>
        📌 版本：2.0.0
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
            <div class="stat-label">AI 深度學習引擎</div>
        </div>""",
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        """<div class="stat-card">
            <div class="stat-number">📚</div>
            <div class="stat-label">維基百科自動擴充</div>
        </div>""",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 9. 圖片上傳 / 相機拍照 區塊
# ==========================================
st.markdown(
    """<div class="upload-section">
        <h3 style="text-align:center; color:#2e7d32; margin-bottom:5px;">
            📤 上傳植物照片
        </h3>
        <p style="text-align:center; color:#757575; font-size:0.9em;">
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

# 拍攝建議
st.markdown(
    """<div class="tip-card">
        💡 <b>拍攝小技巧：</b>
        盡量讓主體清晰、背景單純，建議分別拍攝
        <b>葉片、花朵、果實、樹皮</b>等特徵部位，可大幅提升辨識準確度。
    </div>""",
    unsafe_allow_html=True
)

# ==========================================
# 10. 主程式邏輯 — 辨識 + 結果顯示
# ==========================================
if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # 顯示照片（置中、適當尺寸）
    col_img_l, col_img_c, col_img_r = st.columns([1, 2, 1])
    with col_img_c:
        st.image(image, caption="📸 已上傳照片", use_container_width=True)

    # 辨識按鈕
    col_btn_l, col_btn_c, col_btn_r = st.columns([1, 1, 1])
    with col_btn_c:
        start = st.button("🔍  開始辨識", use_container_width=True)

    if start:
        # 進度條動畫
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
                st.error("❌ 無法辨識此圖片，請嘗試更換照片或拍攝角度。")
            else:
                progress.progress(70, text="📚 檢索中文名稱與文獻...")

                # 最佳結果
                best = all_results[0]
                sci_name = best['species']['scientificNameWithoutAuthor']
                common_names = best['species'].get('commonNames', [])
                score = best['score'] * 100
                family = best['species'].get('family', {}).get('scientificNameWithoutAuthor', '未知')
                genus = best['species'].get('genus', {}).get('scientificNameWithoutAuthor', '未知')

                # 取得中文名
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

                # 嘗試取得維基簡介
                if display_name and has_chinese(display_name):
                    wiki_summary = search_wiki_summary(display_name)

                progress.progress(100, text="✅ 辨識完成！")
                import time; time.sleep(0.3)
                progress.empty()

                # 更新統計
                st.session_state.total_scans += 1
                st.session_state.species_found.add(sci_name)
                st.session_state.history.append({
                    "name": display_name,
                    "scientific": sci_name,
                    "score": score,
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "family": family,
                })

                # ===== 結果卡片 =====
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
                        <p style="text-align:center; color:#616161; font-size:1.1em;">
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

                # 詳細資訊分欄
                st.markdown("<br>", unsafe_allow_html=True)
                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:
                    st.markdown("#### 🧬 分類資訊")
                    st.markdown(f"- **科 (Family)：** {family}")
                    st.markdown(f"- **屬 (Genus)：** {genus}")
                    st.markdown(f"- **學名：** *{sci_name}*")
                    st.markdown(f"- **中文來源：** {source}")
                    if all_names and all_names != "無中文資料":
                        st.markdown(f"- **所有中文名稱：** {all_names}")

                with detail_col2:
                    st.markdown("#### 📖 植物簡介")
                    if wiki_summary:
                        st.info(wiki_summary)
                        if has_chinese(display_name):
                            wiki_link = f"https://zh.wikipedia.org/wiki/{display_name}"
                            st.markdown(f"[🔗 查看完整維基百科條目]({wiki_link})")
                    else:
                        st.warning("暫無中文維基百科摘要。")
                        search_link = f"https://www.google.com/search?q={sci_name}+植物"
                        st.markdown(f"[🔍 用 Google 搜尋此植物]({search_link})")

                # ===== 其他候選結果 =====
                if len(all_results) > 1 and top_k > 1:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### 🏅 其他可能的物種")

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
                                &nbsp;&nbsp;
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

                # ===== 匯出報告 =====
                st.markdown("<br>", unsafe_allow_html=True)
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
                    "",
                    "🏅 其他候選物種：",
                ]
                for idx, res in enumerate(all_results[1:top_k], start=2):
                    r_sci = res['species']['scientificNameWithoutAuthor']
                    r_score = res['score'] * 100
                    r_cn = res['species'].get('commonNames', [])
                    r_cn_zh = [n for n in r_cn if has_chinese(n)]
                    r_name = r_cn_zh[0] if r_cn_zh else r_sci
                    report_lines.append(f"  #{idx} {r_name} ({r_sci}) - {r_score:.2f}%")

                report_text = "\n".join(report_lines)

                col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
                with col_dl2:
                    st.download_button(
                        label="📄 下載辨識報告",
                        data=report_text,
                        file_name=f"plant_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        else:
            progress.empty()
            st.error(f"❌ API 連線失敗（狀態碼：{response.status_code}），請稍後再試。")

# ==========================================
# 11. 頁尾
# ==========================================
st.markdown(
    """<div class="custom-footer">
        🌿 植物辨識系統 v2.0 ｜ Powered by Pl@ntNet & Wikipedia
        <br>
        Made with 💚 for nature lovers
    </div>""",
    unsafe_allow_html=True
)
