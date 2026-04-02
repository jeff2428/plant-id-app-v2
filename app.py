st.markdown("""
<style>
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

/* ===== 修復：隱藏上傳元件文字（手機+桌機都生效） ===== */
section[data-testid="stFileUploader"] label,
section[data-testid="stCameraInput"] label {
    display: none !important;
}
section[data-testid="stFileUploader"] small,
section[data-testid="stFileUploader"] p,
section[data-testid="stCameraInput"] small,
section[data-testid="stCameraInput"] p {
    display: none !important;
}
[data-testid="stFileUploader"] .stMarkdown,
[data-testid="stCameraInput"] .stMarkdown {
    display: none !important;
}

section[data-testid="stFileUploader"] section button {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 30px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

/* 其餘 CSS 不變 */
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

.upload-section {
    background: white;
    border-radius: 16px;
    padding: 20px 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 2px dashed #a5d6a7;
    margin-bottom: 20px;
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
}

@media screen and (max-width: 480px) {
    :root {
        --font-size-hero-title: 1.5em;
        --font-size-hero-subtitle: 0.85em;
        --padding-card: 15px;
    }
}
</style>
""", unsafe_allow_html=True)
