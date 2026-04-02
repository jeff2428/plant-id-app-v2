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
# 【安全登入檢查】避免 AttributeError
# ==========================================
def is_logged_in():
    """安全的登入狀態檢查"""
    try:
        return bool(getattr(st.user, "is_logged_in", False))
    except (AttributeError, NameError):
        return False

def get_user_email():
    """安全的取得 email"""
    try:
        if is_logged_in():
            return st.user.email
        return None
    except (AttributeError, NameError):
        return None

def get_user_name():
    """安全的取得名稱"""
    try:
        if is_logged_in():
            return st.user.name
        return "訪客"
    except (AttributeError, NameError):
        return "訪客"

# ==========================================
# 1. CSS 樣式（原樣保留）
# ==========================================
st.markdown("""
<style>
/* ... 你原本完整的 CSS 全部貼在這裡（為了篇幅我省略，實際複製時請保留你原本的 CSS）... */
.user-badge {
    background: #2d5c3a;
    color: #c8f0cc;
    padding: 0.3rem 0.8rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. API 設定
# ==========================================
API_KEY = st.secrets.get("PLANTNET_API_KEY", "2b1004UqTrbWJn4mj5hqcaZN")
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
if "my_plants_per_user" not in st.session_state:
    st.session_state.my_plants_per_user = {}

# ==========================================
# 4~5. 工具函數、CARE_DATA、TAXON_ZH 等全部保留（省略以節省篇幅）
# ==========================================
# （請把你原本 app.py 中第 4~5 區塊的全部工具函數、get_care、TAXON_ZH、CARE_DATA 等原封不動貼上）

# ==========================================
# 6. 側邊欄（已修正登入顯示）
# ==========================================
with st.sidebar:
    st.markdown("## 👤 帳號")
    if is_logged_in():
        st.markdown(f'<div class="user-badge">✅ {get_user_name()}<br><span style="font-size:0.75rem;">{get_user_email()}</span></div>', unsafe_allow_html=True)
        if st.button("🚪 登出 Google 帳號", use_container_width=True):
            st.logout()
            st.rerun()
    else:
        st.button("🔑 使用 Google 登入", on_click=st.login, use_container_width=True)
        st.caption("登入後植物園將永久與 Google 帳號綁定")

    # 以下歷史、設定區塊完全不變（請貼上你原本的側邊欄歷史與設定程式碼）

# ==========================================
# 7. 主畫面分頁（已修正所有登入檢查）
# ==========================================
tab1, tab2 = st.tabs(["🌿 辨識工具", "🪴 我的植物園"])

with tab1:
    # ... 你原本的辨識工具全部程式碼（metric、上傳、辨識邏輯、結果顯示）原封不動 ...
    # 只在「加入我的植物園」按鈕處改成下面這樣：

    if st.session_state.get('show_results') and st.session_state.get('identification_results'):
        # ... 原有結果顯示 ...

        if is_logged_in():
            if st.button("🪴 加入我的植物園（綁定 Google 帳號）", type="primary", use_container_width=True):
                # ... 原有加入植物的程式碼（使用 get_user_email() 作為 key）...
                email = get_user_email()
                if email:
                    if email not in st.session_state.my_plants_per_user:
                        st.session_state.my_plants_per_user[email] = {}
                    # 加入植物資料（與之前相同）
                    st.success("✅ 已加入你的個人植物園！")
                    st.rerun()
        else:
            st.warning("🔑 請先登入 Google 帳號，才能將植物加入個人植物園")

with tab2:
    st.markdown("## 🪴 我的植物園")
    if not is_logged_in():
        st.error("🔑 請先從側邊欄使用 **Google 登入**，才能查看與管理你的個人植物園")
        st.stop()
    
    email = get_user_email()
    my_plants = st.session_state.my_plants_per_user.get(email, {})
    # ... 後面植物園顯示程式碼與之前完全相同 ...

# ==========================================
# 頁尾
# ==========================================
st.markdown("---")
st.markdown('<div style="text-align:center;color:#2d5c3a;font-size:0.8rem;padding:1rem 0;line-height:2;">🌿 <strong style="color:#4a7a56;">生態探索 v2.8</strong><br>PlantNet AI + Google 登入 + 個人植物園<br><span style="font-size:0.72rem;">已加入安全防錯機制</span></div>', unsafe_allow_html=True)
