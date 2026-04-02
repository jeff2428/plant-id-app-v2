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
       上傳區塊美化 + 重複字體修復（核心）
       ======================================== */

    /* 精準隱藏所有多餘重複文字（桌面+手機全覆蓋，絕不誤傷按鈕/標題） */
    section[data-testid="stFileUploader"] small,
    section[data-testid="stCameraInput"] small,
    section[data-testid="stFileUploader"] hr,
    /* 隱藏手機版重複渲染的輔助文字容器 */
    section[data-testid="stFileUploader"] > div > div > div:not([data-testid]):not(section):not(label),
    section[data-testid="stFileUploader"] div[data-testid="stCaptionContainer"] {
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

    /* Label 樣式（上傳區標題，強制保留不被隱藏） */
    section[data-testid="stFileUploader"] label {
        font-size: 1.15em !important;
        font-weight: 700 !important;
        color: #2e7d32 !important;
        text-align: center !important;
        display: block !important;
        margin-bottom: 10px !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Browse 按鈕 — 綠色漸層膠囊（強制保留文字不被隱藏） */
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
        visibility: visible !important;
        opacity: 1 !important;
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

    /* 手機版響應式調整，完全不碰隱藏規則，只調整尺寸 */
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
        section[data-testid="stFileUploader"] label {
            font-size: 1em !important;
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
