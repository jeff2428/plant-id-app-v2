import streamlit as st
import requests
import re
from PIL import Image
import io, json
from datetime import datetime

# ══════════════════════════════════════════════════════
# 0. 頁面設定
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="🌿 生態探索｜植物辨識",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════
# 1. 全域 CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=Noto+Sans+TC:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family:'Noto Sans TC',sans-serif; background:#0e1a14; color:#d4e8d0; }
.main .block-container { padding:1.5rem 2rem 4rem; max-width:1100px; }

h1 { font-family:'Noto Serif TC',serif!important; font-size:2.4rem!important; font-weight:700!important;
     background:linear-gradient(135deg,#7ec98a,#3a9e5f,#a8d8a8); -webkit-background-clip:text;
     -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:.06em; margin-bottom:.2rem!important; }
h2,h3 { font-family:'Noto Serif TC',serif!important; color:#a8d8a8!important; }
.subtitle { color:#6a9b72; font-size:.9rem; letter-spacing:.12em; margin-bottom:1.5rem; font-weight:300; }

[data-testid="stFileUploader"] { border:2px dashed #2d5c3a!important; border-radius:16px!important;
    background:#111f16!important; padding:1.2rem!important; }
[data-testid="stFileUploaderDropzone"] button {
    background:transparent!important; border:1px solid #2d5c3a!important; border-radius:8px!important;
    padding:.3rem 1.2rem!important; font-size:0!important; color:transparent!important; }
[data-testid="stFileUploaderDropzone"] button::after {
    content:"📂 選擇檔案"; font-family:'Noto Sans TC',sans-serif; font-size:.85rem; color:#5a9a6a; }

.stButton>button { background:linear-gradient(135deg,#2d6e45,#1a4a2e)!important; color:#c8f0cc!important;
    border:1px solid #3a7a50!important; border-radius:12px!important; font-family:'Noto Sans TC',sans-serif!important;
    font-size:.95rem!important; font-weight:500!important; padding:.5rem 1.8rem!important;
    transition:all .25s!important; box-shadow:0 4px 16px rgba(58,158,95,.2)!important; }
.stButton>button:hover { background:linear-gradient(135deg,#3a8a56,#245c38)!important;
    box-shadow:0 6px 24px rgba(58,158,95,.4)!important; transform:translateY(-2px)!important; }

.detail-header { background:linear-gradient(145deg,#112018,#0e1a12); border:1.5px solid #4a9e5f;
    border-radius:20px; padding:1.5rem 1.8rem; position:relative; overflow:hidden; margin-bottom:.8rem; }
.detail-header::before { content:''; position:absolute; top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,#3a9e5f,#7ec98a,#3a9e5f); }
.plant-name { font-family:'Noto Serif TC',serif; font-size:1.9rem; font-weight:700; color:#8fd4a0; }
.sci-name   { font-style:italic; color:#5a8a6a; font-size:.95rem; margin:.25rem 0 .7rem; }

.info-card { background:#111a14; border:1px solid #1e3824; border-radius:14px; padding:1.1rem 1.3rem; margin:.5rem 0; }
.info-card-title { color:#5a9a6a; font-size:.74rem; letter-spacing:.1em; margin-bottom:.6rem; font-weight:600; }
.info-row { display:flex; justify-content:space-between; align-items:center; padding:.48rem 0;
    border-bottom:1px solid #162a1e; font-size:.85rem; }
.info-row:last-child { border-bottom:none; }
.info-key { color:#5a8a6a; flex-shrink:0; }
.info-val { color:#b0d8b8; font-weight:500; text-align:right; }

.care-grid { display:grid; grid-template-columns:1fr 1fr; gap:.65rem; margin:.65rem 0; }
.care-item { background:#0e1a12; border:1px solid #1e3824; border-radius:12px; padding:.85rem .95rem; }
.care-item-wide { grid-column:1/-1; background:#0e1a12; border:1px solid #1e3824; border-radius:12px; padding:.85rem .95rem; }
.care-icon  { font-size:1.25rem; margin-bottom:.2rem; }
.care-title { color:#7ec98a; font-size:.78rem; font-weight:600; margin-bottom:.12rem; }
.care-desc  { color:#90b898; font-size:.82rem; }

.pest-tag    { display:inline-block; background:#1e1010; color:#c87878; border:1px solid #3a2020;
    border-radius:20px; padding:.18rem .75rem; font-size:.76rem; margin:.18rem; }
.disease-tag { display:inline-block; background:#1a1e10; color:#b8c878; border:1px solid #2e3a20;
    border-radius:20px; padding:.18rem .75rem; font-size:.76rem; margin:.18rem; }

.faq-item { background:#0e1a12; border:1px solid #1e3824; border-radius:12px; padding:.85rem 1rem; margin:.45rem 0; }
.faq-q { color:#7ec98a; font-size:.86rem; font-weight:600; margin-bottom:.35rem; }
.faq-a { color:#8ab898; font-size:.82rem; line-height:1.75; }

.wiki-block { background:#0c1810; border-left:3px solid #2d6a40; border-radius:0 10px 10px 0;
    padding:.85rem 1.15rem; color:#8ab898; font-size:.83rem; line-height:1.8; margin:.55rem 0; }
.section-label { color:#5a9a6a; font-size:.74rem; letter-spacing:.1em; font-weight:600;
    margin:1rem 0 .4rem; display:block; }

.taxon-table { width:100%; border-collapse:collapse; }
.taxon-table tr { border-bottom:1px solid #1a3020; }
.taxon-table tr:last-child { border-bottom:none; }
.taxon-table td { padding:.55rem .4rem; font-size:.84rem; }
.tx-label { color:#5a8a6a; width:50px; font-weight:500; }
.tx-val   { color:#c0e0c8; font-style:italic; }
.tx-cn    { color:#7ec98a; font-style:normal; margin-left:.4rem; font-size:.78rem; }

.conf-wrap { background:#1a2e20; border-radius:8px; height:8px; overflow:hidden; margin:.35rem 0 .12rem; border:1px solid #2d4a35; }
.conf-bar  { height:100%; border-radius:8px; }

.hist-item { background:#111a14; border:1px solid #1e3824; border-radius:12px; padding:.65rem .95rem;
    margin:.32rem 0; display:flex; align-items:center; gap:.65rem; }

[data-testid="stMetricValue"] { color:#7ec98a!important; font-family:'Noto Serif TC',serif!important; }
[data-testid="stImage"] img   { border-radius:14px; border:1px solid #2d5c3a; box-shadow:0 8px 28px rgba(0,0,0,.4); }
[data-testid="stSidebar"]     { background:#0b1510!important; border-right:1px solid #1a3020!important; }
hr { border:none; border-top:1px solid #1e3824!important; margin:1rem 0!important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 2. API
# ══════════════════════════════════════════════════════
API_KEY      = "2b1004UqTrbWJn4mj5hqcaZN"
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# ══════════════════════════════════════════════════════
# 3. Session State
# ══════════════════════════════════════════════════════
for k, v in [("history",[]),("results",[]),("selected_idx",0),("uploaded_img",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════
# 4. 資料庫
# ══════════════════════════════════════════════════════
TAXON_ZH = {
    "Tracheophyta":"維管束植物門","Magnoliopsida":"木蘭綱（雙子葉）","Liliopsida":"百合綱（單子葉）",
    "Pinopsida":"松綱","Lamiales":"唇形目","Rosales":"薔薇目","Fabales":"豆目",
    "Asterales":"菊目","Poales":"禾本目","Malpighiales":"金虎尾目","Sapindales":"無患子目",
    "Malvales":"錦葵目","Myrtales":"桃金孃目","Lamiaceae":"唇形科","Rosaceae":"薔薇科",
    "Fabaceae":"豆科","Asteraceae":"菊科","Poaceae":"禾本科","Moraceae":"桑科",
    "Euphorbiaceae":"大戟科","Rutaceae":"芸香科","Meliaceae":"楝科",
    "Apocynaceae":"夾竹桃科","Rubiaceae":"茜草科","Plantae":"植物界",
}

DB = {
    "Lamiaceae":{"diff":"容易","diff_c":"#3fcf6e","temp":"-5 ~ 41°C","zone":"8-10",
        "water":"中等，表土乾後再澆","fert":"每月一次（生長期）","prune":"冬季或早春",
        "prop":"扦插","repot":"春季、秋季","sun":"全日照至半日照","soil":"排水良好壤土",
        "growth":"灌木","height":"0.5 ~ 3 m","spread":"0.5 ~ 2 m",
        "leaf":"落葉至常綠","plant_s":"春季、夏季",
        "diseases":["白粉病","根腐病","枯萎病"],"pests":["蚜蟲","紅蜘蛛","粉介殼蟲"],
        "uses":"廣泛用於香料、藥草及觀賞用途；如薄荷、薰衣草具有天然驅蟲及芳療功效，臭黃荊等本土種則為傳統藥用植物。"},
    "Rosaceae":{"diff":"中等","diff_c":"#c8b864","temp":"-15 ~ 35°C","zone":"5-9",
        "water":"規律澆水，避免積水","fert":"每2週一次（生長期）","prune":"早春休眠結束後",
        "prop":"扦插、嫁接","repot":"春季","sun":"全日照","soil":"肥沃排水良好土壤",
        "growth":"喬木或灌木","height":"1 ~ 10 m","spread":"1 ~ 6 m",
        "leaf":"落葉","plant_s":"春季、秋季",
        "diseases":["黑點病","白粉病","灰黴病"],"pests":["蚜蟲","薔薇葉蜂","紅蜘蛛"],
        "uses":"薔薇科涵蓋蘋果、梨、梅、李等重要果樹，及玫瑰、櫻花等觀賞花卉，具極高農業與文化價值。"},
    "Moraceae":{"diff":"容易","diff_c":"#3fcf6e","temp":"10 ~ 38°C","zone":"9-12",
        "water":"中等，避免過濕","fert":"每月一次","prune":"冬末輕剪",
        "prop":"扦插","repot":"春季","sun":"全日照至半日照","soil":"砂質壤土",
        "growth":"喬木或灌木","height":"3 ~ 15 m","spread":"3 ~ 10 m",
        "leaf":"落葉或半常綠","plant_s":"春季",
        "diseases":["炭疽病","葉斑病"],"pests":["介殼蟲","天牛幼蟲","桑毛蟲"],
        "uses":"桑科含桑樹（葉養蠶、椹可食）、無花果、榕樹等，在農業、傳統醫學及城市綠化中均廣泛應用。"},
    "Fabaceae":{"diff":"容易","diff_c":"#3fcf6e","temp":"5 ~ 40°C","zone":"7-11",
        "water":"耐旱，少量規律澆水","fert":"少量（可自行固氮）","prune":"開花後修剪",
        "prop":"播種","repot":"春季","sun":"全日照","soil":"各類土壤均適應",
        "growth":"喬木、灌木或草本","height":"0.3 ~ 20 m","spread":"0.5 ~ 10 m",
        "leaf":"落葉","plant_s":"春季、夏季",
        "diseases":["根腐病","鏽病"],"pests":["豆莢螟","蚜蟲","白蠅"],
        "uses":"豆科是重要糧食（大豆、花生、豌豆）與飼料作物，同時具固氮改善土壤的生態功能，部分種類提供珍貴木材或藥材。"},
    "Asteraceae":{"diff":"容易","diff_c":"#3fcf6e","temp":"0 ~ 35°C","zone":"6-10",
        "water":"中等","fert":"每2-4週一次","prune":"花後修剪促二次開花",
        "prop":"播種、分株","repot":"春季","sun":"全日照","soil":"一般壤土",
        "growth":"草本","height":"0.2 ~ 2 m","spread":"0.3 ~ 1.5 m",
        "leaf":"常綠或落葉草本","plant_s":"春季至秋季",
        "diseases":["白粉病","灰黴病"],"pests":["蚜蟲","薊馬","葉蟎"],
        "uses":"菊科用途廣泛：蔬菜（萵苣、菊苣）、油料（向日葵）、觀賞花卉（菊花、大麗花）及藥用（紫錐花、洋甘菊）均有。"},
    "Poaceae":{"diff":"容易","diff_c":"#3fcf6e","temp":"-10 ~ 45°C","zone":"5-12",
        "water":"規律澆水","fert":"生長期施氮肥","prune":"冬末剪除枯葉",
        "prop":"分株、播種","repot":"春季","sun":"全日照","soil":"各類土壤",
        "growth":"草本","height":"0.1 ~ 30 m","spread":"0.2 ~ 5 m",
        "leaf":"常綠至落葉草本","plant_s":"春季、夏季",
        "diseases":["鏽病","稻瘟病","紋枯病"],"pests":["薊馬","蝗蟲","螟蟲"],
        "uses":"禾本科是人類最重要糧食來源（稻、麥、玉米），同時提供竹材、蔗糖、牧草，廣泛應用於草坪及景觀植栽。"},
    "Euphorbiaceae":{"diff":"容易","diff_c":"#3fcf6e","temp":"10 ~ 38°C","zone":"9-12",
        "water":"耐旱，少量澆水","fert":"每季一次","prune":"視形狀需求修整",
        "prop":"扦插","repot":"春季","sun":"全日照","soil":"排水良好砂質土",
        "growth":"灌木至喬木","height":"0.3 ~ 20 m","spread":"0.5 ~ 8 m",
        "leaf":"常綠","plant_s":"春季",
        "diseases":["灰黴病","炭疽病"],"pests":["粉介殼蟲","紅蜘蛛"],
        "uses":"大戟科含橡膠樹（天然橡膠）、木薯（澱粉作物）、蓖麻（油料）及聖誕紅等觀賞植物；部分種類具毒性，需謹慎處理。"},
    "Rutaceae":{"diff":"中等","diff_c":"#c8b864","temp":"5 ~ 38°C","zone":"8-11",
        "water":"規律澆水","fert":"柑橘專用肥料","prune":"春季疏剪",
        "prop":"嫁接、扦插","repot":"春季","sun":"全日照","soil":"微酸性砂質壤土",
        "growth":"喬木或灌木","height":"2 ~ 10 m","spread":"2 ~ 6 m",
        "leaf":"常綠","plant_s":"春季",
        "diseases":["潰瘍病","黃龍病","炭疽病"],"pests":["柑橘鳳蝶幼蟲","粉蝨","介殼蟲"],
        "uses":"芸香科以柑橘類果樹著名（橙、柚、檸檬），富含維生素C；花卉（七里香）具香氣，亦有藥用及香料用途。"},
    "Apocynaceae":{"diff":"容易","diff_c":"#3fcf6e","temp":"15 ~ 40°C","zone":"10-12",
        "water":"少量（耐旱）","fert":"每月一次","prune":"花後修剪",
        "prop":"扦插","repot":"春季","sun":"全日照","soil":"排水良好砂質土",
        "growth":"灌木或藤本","height":"0.5 ~ 5 m","spread":"0.5 ~ 3 m",
        "leaf":"常綠","plant_s":"春季、夏季",
        "diseases":["根腐病","葉斑病"],"pests":["蚜蟲","粉介殼蟲"],
        "uses":"夾竹桃科多具觀賞價值（夾竹桃、雞蛋花、長春花），部分含抗癌生物鹼（長春花）；需注意部分種類有毒。"},
    "DEFAULT":{"diff":"中等","diff_c":"#c8b864","temp":"5 ~ 35°C","zone":"7-10",
        "water":"中等，依品種調整","fert":"每月一次（生長期）","prune":"春季",
        "prop":"扦插或播種","repot":"春季","sun":"全日照至半日照","soil":"排水良好壤土",
        "growth":"喬木、灌木或草本","height":"0.3 ~ 10 m","spread":"0.3 ~ 5 m",
        "leaf":"依品種而定","plant_s":"春季",
        "diseases":["白粉病","根腐病"],"pests":["蚜蟲","紅蜘蛛"],
        "uses":"本植物具有觀賞及生態價值，請參考專業文獻以獲取更詳細的用途說明。"},
}

# ══════════════════════════════════════════════════════
# 5. 工具函數
# ══════════════════════════════════════════════════════
def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search_wikipedia(sci_name):
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    headers  = {"User-Agent":"PlantExplorer/3.0"}
    try:
        sr = requests.get(wiki_url, params={"action":"query","list":"search",
            "srsearch":sci_name,"format":"json","utf8":1}, headers=headers, timeout=5).json()
        res = sr.get("query",{}).get("search",[])
        if not res: return None, None, None
        title = res[0].get("title","")
        if not has_chinese(title): return None, None, None
        rd = requests.get(wiki_url, params={"action":"query","titles":title,
            "prop":"redirects","rdlimit":"50","format":"json","utf8":1}, headers=headers, timeout=5).json()
        aliases = [title]
        for _, pi in rd.get("query",{}).get("pages",{}).items():
            for r in pi.get("redirects",[]):
                t = r["title"]
                if ":" not in t and has_chinese(t): aliases.append(t)
        aliases = list(dict.fromkeys(aliases))
        ex = requests.get(wiki_url, params={"action":"query","prop":"extracts",
            "exintro":True,"explaintext":True,"exsentences":4,
            "titles":title,"format":"json","utf8":1,"redirects":1}, headers=headers, timeout=5).json()
        extract = ""
        for _, p in ex.get("query",{}).get("pages",{}).items():
            if p.get("pageid",-1) != -1:
                extract = p.get("extract","").strip()[:420]
        link = f"https://zh.wikipedia.org/wiki/{title.replace(' ','_')}"
        return aliases, extract, link
    except Exception:
        return None, None, None

def get_gbif(sci_name):
    try:
        r = requests.get("https://api.gbif.org/v1/species/match",
            params={"name":sci_name,"verbose":False}, timeout=6).json()
        return {"phylum":r.get("phylum",""),"class":r.get("class",""),
                "order":r.get("order",""),"family":r.get("family",""),
                "genus":r.get("genus",""),"species":r.get("species",sci_name)}
    except: return {}

def get_care(family):
    return DB.get(family, DB["DEFAULT"])

def cc(s): return "#3fcf6e" if s>=80 else ("#c8b864" if s>=50 else "#c86464")
def cl(s): return ("高度吻合","🟢") if s>=80 else (("中度吻合","🟡") if s>=50 else ("低度吻合","🔴"))

# ══════════════════════════════════════════════════════
# 6. 詳細頁渲染
# ══════════════════════════════════════════════════════
def render_detail(match, img, all_results):
    sci      = match['species']['scientificNameWithoutAuthor']
    genus    = match['species'].get('genus',{}).get('scientificNameWithoutAuthor','')
    family   = match['species'].get('family',{}).get('scientificNameWithoutAuthor','')
    cn_list  = match['species'].get('commonNames',[])
    score    = match['score'] * 100
    color    = cc(score)
    lbl, ico = cl(score)

    with st.spinner("🔍 載入詳細資料…"):
        aliases, extract, wiki_link = search_wikipedia(sci)
        gbif = get_gbif(sci)

    if aliases:
        display = aliases[0]; all_aliases = aliases
    else:
        pn = [n for n in cn_list if has_chinese(n)]
        display = pn[0] if pn else sci; all_aliases = list(dict.fromkeys(pn))

    eng_names = [n for n in cn_list if not has_chinese(n)][:3]
    family_key = gbif.get("family","") or family or "DEFAULT"
    care = get_care(family_key)

    # ── 兩欄佈局 ──
    L, R = st.columns([1,1], gap="large")

    # ═══ 左欄 ═══
    with L:
        if img:
            st.image(img, use_container_width=True)

        # 標題
        alias_html = "".join([f'<span style="background:#1d3d28;color:#7ec98a;border:1px solid #2d5c3a;border-radius:20px;padding:.16rem .65rem;font-size:.74rem;margin:.14rem .08rem;display:inline-block;">{a}</span>' for a in all_aliases[:6]])
        eng_html = f'<div style="color:#3a6058;font-size:.8rem;margin-bottom:.5rem;">{" · ".join(eng_names)}</div>' if eng_names else ""
        st.markdown(f"""<div class="detail-header">
            <div class="plant-name">{display}</div>
            <div class="sci-name">{sci}</div>
            {eng_html}
            <div style="margin:.4rem 0 .7rem;">{alias_html}</div>
            <div style="display:flex;justify-content:space-between;font-size:.8rem;color:#5a8a6a;margin-bottom:.18rem;">
                <span>AI 信心指數</span><span style="color:{color}">{score:.1f}% · {ico} {lbl}</span>
            </div>
            <div class="conf-wrap"><div class="conf-bar" style="width:{score:.1f}%;background:linear-gradient(90deg,{color}88,{color});"></div></div>
        </div>""", unsafe_allow_html=True)

        # 基本資訊
        st.markdown('<span class="section-label">📋 基本資訊</span>', unsafe_allow_html=True)
        st.markdown(f"""<div class="info-card">
            <div class="info-row"><span class="info-key">生長形態</span><span class="info-val">{care['growth']}</span></div>
            <div class="info-row"><span class="info-key">最大高度</span><span class="info-val">{care['height']}</span></div>
            <div class="info-row"><span class="info-key">最大擴展</span><span class="info-val">{care['spread']}</span></div>
            <div class="info-row"><span class="info-key">葉　　型</span><span class="info-val">{care['leaf']}</span></div>
            <div class="info-row"><span class="info-key">種植季節</span><span class="info-val">{care['plant_s']}</span></div>
            {f'<div class="info-row"><span class="info-key">屬</span><span class="info-val" style="font-style:italic;">{genus}</span></div>' if genus else ''}
            {f'<div class="info-row"><span class="info-key">科</span><span class="info-val" style="font-style:italic;">{family}</span></div>' if family else ''}
        </div>""", unsafe_allow_html=True)

        # 分類階層
        st.markdown('<span class="section-label">🌳 分類階層</span>', unsafe_allow_html=True)
        rows = ""
        for lk, val in [("門",gbif.get("phylum","")),("綱",gbif.get("class","")),
                         ("目",gbif.get("order","")),("科",gbif.get("family","")),
                         ("屬",gbif.get("genus","")),("種",gbif.get("species",sci))]:
            if not val: continue
            zh = TAXON_ZH.get(val,"")
            zh_s = f'<span class="tx-cn">（{zh}）</span>' if zh else ""
            rows += f'<tr><td class="tx-label">{lk}</td><td class="tx-val">{val}{zh_s}</td></tr>'
        st.markdown(f'<div class="info-card"><table class="taxon-table">{rows}</table></div>', unsafe_allow_html=True)

    # ═══ 右欄 ═══
    with R:
        # 養護指南
        st.markdown('<span class="section-label">🌱 植物養護指南</span>', unsafe_allow_html=True)
        st.markdown(f"""<div class="info-card">
            <div style="margin-bottom:.85rem;">
                <span style="background:{care['diff_c']}22;color:{care['diff_c']};border:1px solid {care['diff_c']}55;
                    border-radius:20px;padding:.3rem .95rem;font-size:.88rem;font-weight:600;">{care['diff']}</span>
                <span style="color:#3a6a48;font-size:.76rem;margin-left:.6rem;">照護難度</span>
            </div>
            <div class="info-card-title">🌡️ 養護條件</div>
            <div class="info-row"><span class="info-key">光照需求</span><span class="info-val">{care['sun']}</span></div>
            <div class="info-row"><span class="info-key">土壤類型</span><span class="info-val">{care['soil']}</span></div>
            <div class="info-row"><span class="info-key">適合氣溫</span><span class="info-val">{care['temp']}</span></div>
            <div class="info-row"><span class="info-key">耐寒區間</span><span class="info-val">Zone {care['zone']}</span></div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<span class="section-label">💧 澆法指南</span>', unsafe_allow_html=True)
        st.markdown(f"""<div class="care-grid">
            <div class="care-item"><div class="care-icon">💧</div><div class="care-title">澆水</div><div class="care-desc">{care['water']}</div></div>
            <div class="care-item"><div class="care-icon">🌿</div><div class="care-title">肥料</div><div class="care-desc">{care['fert']}</div></div>
            <div class="care-item"><div class="care-icon">✂️</div><div class="care-title">修剪</div><div class="care-desc">{care['prune']}</div></div>
            <div class="care-item"><div class="care-icon">🌱</div><div class="care-title">繁殖方式</div><div class="care-desc">{care['prop']}</div></div>
            <div class="care-item-wide"><div class="care-icon">🪴</div><div class="care-title">翻盆移植</div><div class="care-desc">{care['repot']}</div></div>
        </div>""", unsafe_allow_html=True)

        # 疾病蟲害
        st.markdown('<span class="section-label">🦠 常見疾病蟲害</span>', unsafe_allow_html=True)
        d_html = "".join([f'<span class="disease-tag">🍃 {d}</span>' for d in care['diseases']])
        p_html = "".join([f'<span class="pest-tag">🐛 {p}</span>'   for p in care['pests']])
        st.markdown(f'<div class="info-card"><div class="info-card-title">病害</div><div style="margin-bottom:.7rem;">{d_html}</div><div class="info-card-title">蟲害</div><div>{p_html}</div></div>', unsafe_allow_html=True)

        # FAQ
        st.markdown('<span class="section-label">❓ 熱門問題</span>', unsafe_allow_html=True)
        for q, a in [
            (f"如何判斷{display}需要澆水？",
             f"觀察表土是否乾燥，手指插入約2公分感覺乾燥即可澆水。{display}偏好{care['water']}，避免根部積水。"),
            (f"{display}適合種在室內嗎？",
             f"建議放在{care['sun']}的位置。室內種植需確保充足光線，光線不足會導致徒長。"),
            (f"{display}何時進行修剪最佳？",
             f"建議在{care['prune']}進行修剪，可幫助塑形並促進新芽，使用消毒過的剪刀以避免感染。"),
        ]:
            st.markdown(f'<div class="faq-item"><div class="faq-q">Q：{q}</div><div class="faq-a">{a}</div></div>', unsafe_allow_html=True)

    # ═══ 全寬：用途 + 介紹 ═══
    st.markdown("---")
    W1, W2 = st.columns(2, gap="large")
    with W1:
        st.markdown('<span class="section-label">🌍 用途</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="wiki-block">{care["uses"]}</div>', unsafe_allow_html=True)
    with W2:
        if extract:
            st.markdown('<span class="section-label">📖 植物趣聞百科</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="wiki-block">{extract}</div>', unsafe_allow_html=True)
            if wiki_link:
                st.markdown(f'<a href="{wiki_link}" target="_blank" style="color:#4a9e6f;font-size:.8rem;text-decoration:none;">📚 閱讀維基百科完整介紹 →</a>', unsafe_allow_html=True)

    # ═══ 匯出 ═══
    st.markdown("---")
    st.markdown('<span class="section-label">📤 匯出報告</span>', unsafe_allow_html=True)
    report = f"""🌿 植物辨識報告\n{'='*38}
辨識時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
植物名稱：{display}
學　　名：{sci}
信心指數：{score:.2f}%
生長形態：{care['growth']} | 最大高度：{care['height']}
適合氣溫：{care['temp']} | 耐寒區間：Zone {care['zone']}
照護難度：{care['diff']} | 光照需求：{care['sun']}
澆水方式：{care['water']}
施肥頻率：{care['fert']}
修剪時機：{care['prune']}
繁殖方式：{care['prop']}
{'='*38}
所有候選結果：\n"""
    for i, m in enumerate(all_results):
        sn = m['species']['scientificNameWithoutAuthor']
        sc2 = m['score']*100
        cn2 = [n for n in m['species'].get('commonNames',[]) if has_chinese(n)]
        report += f"{i+1}. {cn2[0] if cn2 else sn}（{sn}）— {sc2:.2f}%\n"
    report += "\n資料來源：PlantNet API · GBIF · 中文維基百科"

    ec1, ec2 = st.columns(2)
    with ec1:
        st.download_button("⬇️ 下載文字報告", report.encode("utf-8"),
            f"植物辨識_{datetime.now().strftime('%Y%m%d_%H%M')}.txt","text/plain",use_container_width=True)
    with ec2:
        jd = json.dumps({"timestamp":datetime.now().isoformat(),"plant":display,"scientific":sci,
            "score":score,"care":care,"taxonomy":gbif},ensure_ascii=False,indent=2)
        st.download_button("⬇️ 下載 JSON 資料", jd.encode("utf-8"),
            f"plant_{datetime.now().strftime('%Y%m%d_%H%M')}.json","application/json",use_container_width=True)

# ══════════════════════════════════════════════════════
# 7. 側邊欄
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📋 辨識歷史")
    if not st.session_state.history:
        st.markdown('<p style="color:#3a6a48;font-size:.84rem;">尚無辨識紀錄</p>', unsafe_allow_html=True)
    else:
        for rec in reversed(st.session_state.history):
            st.markdown(f'<div class="hist-item"><span style="font-size:1.3rem;">🌿</span><div><div style="font-size:.84rem;color:#a0d0a8;font-weight:500;">{rec["name"]}</div><div style="font-size:.7rem;color:#4a7a56;">{rec["time"]} · {rec["score"]:.1f}%</div></div></div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.session_state.history and st.button("🗑️ 清除歷史"):
        st.session_state.history=[]; st.rerun()
    st.markdown("---")
    st.markdown("### ⚙️ 設定")
    top_n = st.slider("候選植物數", 1, 5, 3)
    st.markdown("---")
    st.markdown('<div style="color:#3a6a48;font-size:.74rem;line-height:2;">🌿 <strong style="color:#5a9a68;">生態探索</strong> v3.0<br>PlantNet · GBIF · 中文維基百科</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 8. 主頁面
# ══════════════════════════════════════════════════════
st.markdown("# 🌿 生態探索")
st.markdown('<p class="subtitle">植 物 智 能 辨 識 系 統 ｜ Powered by PlantNet AI</p>', unsafe_allow_html=True)
mc1,mc2,mc3 = st.columns(3)
mc1.metric("本次辨識", f"{len(st.session_state.history)} 種")
mc2.metric("平均信心", f"{(sum(r['score'] for r in st.session_state.history)/len(st.session_state.history)):.1f}%" if st.session_state.history else "—")
mc3.metric("資料庫涵蓋", "30,000+ 種")
st.markdown("---")

uc, pc = st.columns([1,1], gap="large")
with uc:
    st.markdown("### 📸 上傳植物照片")
    st.markdown('<p style="color:#4a7a56;font-size:.83rem;">建議清晰拍攝葉片、花朵或果實特徵以提高準確率</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg","jpeg","png","webp"], label_visibility="collapsed")
    if uploaded_file:
        st.markdown(f'<span style="background:#1d3d28;color:#7ec98a;border:1px solid #2d5c3a;border-radius:20px;padding:.16rem .65rem;font-size:.74rem;">📁 {uploaded_file.name}</span>&nbsp;<span style="background:#1d3d28;color:#7ec98a;border:1px solid #2d5c3a;border-radius:20px;padding:.16rem .65rem;font-size:.74rem;">{uploaded_file.size//1024} KB</span>', unsafe_allow_html=True)
with pc:
    if uploaded_file:
        st.image(Image.open(uploaded_file), caption="預覽", use_container_width=True)
    else:
        st.markdown('<div style="background:#0a1410;border:1px dashed #1e3820;border-radius:16px;height:220px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:.7rem;"><span style="font-size:3.2rem;">🍃</span><p style="color:#2d5c3a;font-size:.86rem;text-align:center;">上傳照片後<br>預覽將顯示於此</p></div>', unsafe_allow_html=True)

st.markdown("")
bc2,_ = st.columns([1,3])
with bc2:
    identify_btn = st.button("🔬 開始辨識", disabled=uploaded_file is None, use_container_width=True)

# ══════════════════════════════════════════════════════
# 9. 辨識
# ══════════════════════════════════════════════════════
if identify_btn and uploaded_file:
    with st.spinner("🌱 AI 辨識中…"):
        img_bytes = uploaded_file.getvalue()
        try:
            resp = requests.post(API_ENDPOINT,
                files={'images':('i.jpg',img_bytes,'image/jpeg')},
                data={'organs':['auto']}, timeout=30)
        except Exception as e:
            st.error(f"❌ 網路錯誤：{e}"); st.stop()
        if resp.status_code != 200:
            st.error(f"❌ API 錯誤 HTTP {resp.status_code}"); st.stop()
        results = resp.json().get('results',[])
        if not results:
            st.warning("⚠️ 未能辨識，請上傳更清晰的植物照片"); st.stop()
    st.session_state.results      = results[:top_n]
    st.session_state.selected_idx = 0
    st.session_state.uploaded_img = Image.open(io.BytesIO(img_bytes))
    best  = results[0]
    bname_list = [n for n in best['species'].get('commonNames',[]) if has_chinese(n)]
    bname = bname_list[0] if bname_list else best['species']['scientificNameWithoutAuthor']
    st.session_state.history.append({
        "name":bname,"sci":best['species']['scientificNameWithoutAuthor'],
        "score":best['score']*100,"time":datetime.now().strftime("%H:%M")
    })

# ══════════════════════════════════════════════════════
# 10. 候選選擇器 → 詳細頁
# ══════════════════════════════════════════════════════
if st.session_state.results:
    st.markdown("---")
    st.markdown("## 🎯 辨識結果")

    top_results = st.session_state.results
    n = len(top_results)
    cand_cols = st.columns(n, gap="small")

    for i, m in enumerate(top_results):
        sn  = m['species']['scientificNameWithoutAuthor']
        sc  = m['score']*100
        cn  = [x for x in m['species'].get('commonNames',[]) if has_chinese(x)]
        dn  = cn[0] if cn else sn
        c   = cc(sc)
        act = (i == st.session_state.selected_idx)
        bd  = "#7ec98a" if act else "#2d5c3a"
        bg  = "#152a1c" if act else "#111f16"
        glow= "box-shadow:0 0 0 2px #3a9e5f44;" if act else ""

        with cand_cols[i]:
            gold = "<span style='font-size:.66rem;color:#c8b864;background:#2a2a10;border:1px solid #5a5020;border-radius:10px;padding:.08rem .5rem;'>✨ 最佳</span><br>" if i==0 else ""
            st.markdown(f"""<div style="background:{bg};border:1.5px solid {bd};border-radius:14px;
                padding:.75rem .85rem;{glow}margin-bottom:.3rem;">
                {gold}
                <div style="font-family:'Noto Serif TC',serif;font-size:.92rem;color:#8fd4a0;font-weight:600;margin:.28rem 0 .12rem;">{dn}</div>
                <div style="font-style:italic;color:#4a7a56;font-size:.68rem;margin-bottom:.28rem;">{sn[:26]}{'…' if len(sn)>26 else ''}</div>
                <div style="color:{c};font-size:.76rem;font-weight:600;">{sc:.1f}%</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"{'📌 查看中' if act else '查看詳情'}", key=f"sel_{i}", use_container_width=True):
                st.session_state.selected_idx = i
                st.rerun()

    st.markdown("")
    render_detail(top_results[st.session_state.selected_idx],
                  st.session_state.uploaded_img, top_results)

# ══════════════════════════════════════════════════════
# 11. 頁腳
# ══════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<div style="text-align:center;color:#2d5c3a;font-size:.76rem;padding:.8rem 0;line-height:2;">🌿 <strong style="color:#4a7a56;">生態探索 Plant Explorer</strong> v3.0<br>PlantNet · GBIF · 中文維基百科<br><span style="font-size:.68rem;">本系統僅供參考，物種鑑定請諮詢專業植物學家</span></div>', unsafe_allow_html=True)
