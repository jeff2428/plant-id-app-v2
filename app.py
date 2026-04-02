import streamlit as st
import requests
import re
from PIL import Image
import io
import json
from datetime import datetime
from urllib.parse import quote

# ==========================================
# 0. 頁面設定 + Google 登入說明
# ==========================================
st.set_page_config(
    page_title="🌿 生態探索｜植物辨識",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== 【重要】Google 登入設定說明 ======================
st.markdown("""
<div style="background:#1a3020;border:1px solid #4a9e5f;border-radius:12px;padding:1rem;margin-bottom:1.5rem;">
<strong>🌟 Google 帳號登入已啟用！</strong><br>
1. 請在 <code>.streamlit/secrets.toml</code> 中新增以下內容（需先到 Google Cloud Console 建立 OAuth 2.0 Client ID）<br>
<pre style="background:#0e1a14;padding:0.8rem;border-radius:8px;font-size:0.85rem;overflow:auto;">
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"   # 本地測試用；上線後改成你的 Streamlit Cloud URL + /oauth2callback
cookie_secret = "你的隨機安全字串（至少32位）"
client_id = "你的 Google Client ID"
client_secret = "你的 Google Client Secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
</pre>
2. Google Cloud Console 操作：
   - 建立專案 → APIs & Services → Credentials → Create OAuth client ID（Web application）
   - Authorized redirect URIs 加入你的 redirect_uri
3. 完成後重新啟動 app，即可使用 Google 帳號登入。
</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. CSS 樣式（原樣保留 + 小調整）
# ==========================================
st.markdown("""
<style>
/* ...（你的原 CSS 全部保留，此處省略以保持簡潔，實際複製時請貼上你原本完整的 CSS）... */
.myplant-card {
    background: linear-gradient(145deg, #112018, #0e1a12);
    border: 1px solid #2d5c3a;
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}
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
# 2. API 設定（原樣）
# ==========================================
API_KEY = st.secrets.get("PLANTNET_API_KEY", "2b1004UqTrbWJn4mj5hqcaZN")
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# ==========================================
# 3. Session State（改用 per-user 儲存植物園）
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
if "my_plants_per_user" not in st.session_state:   # ← 改成 per-user
    st.session_state.my_plants_per_user = {}

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
# 4. 工具函數（全部原樣保留）
# ==========================================
def has_chinese(text):
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', text))

@st.cache_data(ttl=3600, show_spinner=False)
def search_wikipedia(scientific_name):
    url = "https://zh.wikipedia.org/w/api.php"
    headers = {"User-Agent": "PlantExplorer/2.7"}
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
        link = f"https://zh.wikipedia.org/wiki/{quote(title)}"
        return list(dict.fromkeys(aliases)), link
    except:
        return None, None

@st.cache_data(ttl=3600, show_spinner=False)
def get_gbif(scientific_name):
    try:
        res = requests.get("https://api.gbif.org/v1/species/match", params={"name": scientific_name}, timeout=6).json()
        return {"phylum": res.get("phylum", ""), "class": res.get("class", ""), "order": res.get("order", ""), "family": res.get("family", ""), "genus": res.get("genus", ""), "species": res.get("species", scientific_name)}
    except:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def get_wiki_extract(title):
    try:
        res = requests.get("https://zh.wikipedia.org/w/api.php", params={"action": "query", "prop": "extracts", "exintro": True, "explaintext": True, "exsentences": 3, "titles": title, "format": "json", "utf8": 1, "redirects": 1}, headers={"User-Agent": "PlantExplorer/2.7"}, timeout=5).json()
        for pid, page in res.get("query", {}).get("pages", {}).items():
            if pid != "-1":
                txt = page.get("extract", "").strip()
                if txt and len(txt) > 30:
                    return txt[:350]
    except:
        pass
    return None

def get_color(score):
    if score >= 80: return "#3fcf6e"
    elif score >= 50: return "#c8b864"
    return "#c86464"

def get_label(score):
    if score >= 80: return "高度吻合", "🟢"
    elif score >= 50: return "中度吻合", "🟡"
    return "低度吻合", "🔴"

def render_bar(score, color):
    st.markdown(f'<div class="confidence-bar-wrap"><div class="confidence-bar" style="width:{score:.1f}%;background:linear-gradient(90deg,{color}88,{color});"></div></div><p style="color:{color};font-size:0.82rem;margin:0;text-align:right;">{score:.2f}%</p>', unsafe_allow_html=True)

def compress_image(img, max_w=1920):
    try:
        if img.width > max_w:
            ratio = max_w / img.width
            img = img.resize((max_w, int(img.height * ratio)), Image.Resampling.LANCZOS)
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA': bg.paste(img, mask=img.split()[-1])
            else: bg.paste(img)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except:
        return img

TAXON_ZH = {"Tracheophyta": "維管束植物門", "Magnoliopsida": "木蘭綱", "Liliopsida": "百合綱", "Lamiales": "唇形目", "Rosales": "薔薇目", "Fabales": "豆目", "Asterales": "菊目", "Poales": "禾本目", "Lamiaceae": "唇形科", "Rosaceae": "薔薇科", "Fabaceae": "豆科", "Asteraceae": "菊科", "Poaceae": "禾本科", "Moraceae": "桑科", "Orchidaceae": "蘭科", "Araceae": "天南星科"}
CARE_DATA = {
    "Lamiaceae": {"diff": "容易", "diff_c": "#3fcf6e", "temp": "-5~41°C", "zone": "8-10", "water": "中等", "fert": "每月一次", "prune": "冬季", "prop": "扦插", "sun": "全日照"},
    "Rosaceae": {"diff": "中等", "diff_c": "#c8b864", "temp": "-15~35°C", "zone": "5-9", "water": "規律", "fert": "每2週", "prune": "早春", "prop": "扦插嫁接", "sun": "全日照"},
    "Fabaceae": {"diff": "容易", "diff_c": "#3fcf6e", "temp": "5~40°C", "zone": "7-11", "water": "少量", "fert": "少量", "prune": "花後", "prop": "播種", "sun": "全日照"},
    "Orchidaceae": {"diff": "困難", "diff_c": "#c86464", "temp": "15~30°C", "zone": "10-12", "water": "少量", "fert": "蘭花肥", "prune": "花後", "prop": "分株", "sun": "散射光"},
    "DEFAULT": {"diff": "中等", "diff_c": "#c8b864", "temp": "5~35°C", "zone": "7-10", "water": "中等", "fert": "每月一次", "prune": "春季", "prop": "扦插播種", "sun": "全日照"},
}
def get_care(family):
    return CARE_DATA.get(family, CARE_DATA["DEFAULT"])

# ==========================================
# 5. 側邊欄（新增 Google 登入/登出）
# ==========================================
with st.sidebar:
    st.markdown("## 👤 帳號")
    if st.user.is_logged_in:
        st.markdown(f'<div class="user-badge">✅ {st.user.name}<br><span style="font-size:0.75rem;">{st.user.email}</span></div>', unsafe_allow_html=True)
        if st.button("🚪 登出 Google 帳號", use_container_width=True):
            st.logout()
            st.rerun()
    else:
        st.button("🔑 使用 Google 登入", on_click=st.login, use_container_width=True)
        st.caption("登入後你的植物園將與 Google 帳號綁定")

    st.markdown("---")
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
                if not isinstance(score, (int, float)): score = 0
                st.markdown(f'<div class="history-item"><span style="font-size:1.5rem;">{emoji}</span><div><div style="font-size:0.88rem;color:#a0d0a8;font-weight:500;">{name}</div><div style="font-size:0.72rem;color:#4a7a56;">{time_str} | {score:.1f}%</div></div></div>', unsafe_allow_html=True)
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
    st.markdown('<div style="color:#3a6a48;font-size:0.78rem;line-height:1.8;">🌿 <strong style="color:#5a9a68;">生態探索 v2.7</strong><br>PlantNet + Google 登入 + 個人植物園</div>', unsafe_allow_html=True)

# ==========================================
# 6. 主畫面分頁
# ==========================================
tab1, tab2 = st.tabs(["🌿 辨識工具", "🪴 我的植物園"])

# ====================== TAB 1：辨識工具 ======================
with tab1:
    st.markdown("# 🌿 生態探索")
    st.markdown('<p class="subtitle">植物智能辨識系統 Powered by PlantNet AI</p>', unsafe_allow_html=True)
    
    if st.user.is_logged_in:
        st.success(f"👋 歡迎回來，{st.user.name}！你的植物園已與 Google 帳號綁定")
    else:
        st.warning("🔑 請先從側邊欄使用 Google 登入，才能將植物加入個人植物園")
    
    # （以下所有辨識工具內容與之前完全相同，此處省略重複程式碼以節省篇幅）
    # ... 請將你原本 tab1 的全部程式碼（metric、col_up、col_prev、start_btn、辨識邏輯、顯示結果）原封不動貼在此處 ...
    # 唯一修改：在「加入我的植物園」按鈕外面加上 if st.user.is_logged_in: 判斷
    
    # 【修改重點】加入植物園按鈕（只在已登入時顯示）
    if st.session_state.get('show_results') and st.session_state.get('identification_results'):
        # ... 原有結果顯示程式碼 ...
        
        if st.user.is_logged_in and st.button("🪴 加入我的植物園（綁定 Google 帳號）", type="primary", use_container_width=True):
            best = st.session_state.identification_results[0]
            sci = best.get('species', {}).get('scientificNameWithoutAuthor', '')
            common = best.get('species', {}).get('commonNames', [])
            cn_list = [n for n in common if has_chinese(n)]
            display = cn_list[0] if cn_list else sci
            fam = get_gbif(sci).get("family", "") or ""
            care = get_care(fam)
            
            email = st.user.email
            if email not in st.session_state.my_plants_per_user:
                st.session_state.my_plants_per_user[email] = {}
            
            plant_id = f"plant_{int(datetime.now().timestamp())}"
            st.session_state.my_plants_per_user[email][plant_id] = {
                "name": display,
                "sci": sci,
                "score": best.get('score', 0) * 100,
                "emoji": "🌿",
                "add_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "last_water": None,
                "last_fert": None,
                "image": uploaded.getvalue() if uploaded else None,
                "care": care
            }
            st.success(f"✅ 已將「{display}」加入你的個人植物園！")
            st.rerun()

# ====================== TAB 2：我的植物園 ======================
with tab2:
    st.markdown("## 🪴 我的植物園")
    if not st.user.is_logged_in:
        st.error("🔑 請先從側邊欄使用 **Google 登入**，才能查看與管理你的個人植物園")
        st.stop()
    
    email = st.user.email
    my_plants = st.session_state.my_plants_per_user.get(email, {})
    
    if not my_plants:
        st.info("🌱 你的植物園目前是空的。\n\n請到「🌿 辨識工具」分頁辨識植物後，點擊「加入我的植物園」即可儲存")
    else:
        st.metric("🌿 我的植物總數", f"{len(my_plants)} 株")
        for pid, plant in list(my_plants.items()):
            with st.expander(f"{plant['emoji']} {plant['name']}　｜　{plant['last_water'] or '尚未澆水'}", expanded=False):
                # （照護打卡與顯示內容與之前完全相同）
                col_a, col_b, col_c = st.columns([1, 2, 2])
                with col_a:
                    if plant.get("image"):
                        try:
                            st.image(io.BytesIO(plant["image"]), width=140)
                        except:
                            st.write("🌿")
                with col_b:
                    st.metric("信心度", f"{plant['score']:.1f}%")
                    st.write(f"**學名**：{plant['sci']}")
                    st.caption(f"加入時間：{plant['add_time']}")
                    if st.button("💧 今天已澆水", key=f"water_{pid}", use_container_width=True):
                        plant['last_water'] = datetime.now().strftime("%Y-%m-%d")
                        st.success("已記錄")
                        st.rerun()
                    if st.button("🌱 今天已施肥", key=f"fert_{pid}", use_container_width=True):
                        plant['last_fert'] = datetime.now().strftime("%Y-%m-%d")
                        st.success("已記錄")
                        st.rerun()
                with col_c:
                    st.markdown("#### 🌱 照護提醒")
                    care = plant["care"]
                    st.markdown(f'<span style="background:{care.get("diff_c","#c8b864")}22;color:{care.get("diff_c","#c8b864")};border:1px solid {care.get("diff_c","#c8b864")}66;border-radius:20px;padding:0.35rem 1.1rem;font-weight:600;">{care.get("diff","中等")}</span>', unsafe_allow_html=True)
                    if plant.get('last_water'):
                        days = (datetime.now() - datetime.strptime(plant['last_water'], "%Y-%m-%d")).days
                        st.info(f"💧 上次澆水：{days} 天前")
                    if plant.get('last_fert'):
                        days_fert = (datetime.now() - datetime.strptime(plant['last_fert'], "%Y-%m-%d")).days
                        st.info(f"🌱 上次施肥：{days_fert} 天前")
                    if st.button("🗑️ 移除這株植物", key=f"del_{pid}", use_container_width=True):
                        del my_plants[pid]
                        st.success("已移除")
                        st.rerun()

# ==========================================
# 10. 頁尾
# ==========================================
st.markdown("---")
st.markdown('<div style="text-align:center;color:#2d5c3a;font-size:0.8rem;padding:1rem 0;line-height:2;">🌿 <strong style="color:#4a7a56;">生態探索 v2.7</strong><br>PlantNet AI + Google 帳號登入 + 個人化植物園<br><span style="font-size:0.72rem;">資料以 Google 帳號永久區分（目前 session 階段保存，未來可接 Firestore 永久化）</span></div>', unsafe_allow_html=True)
