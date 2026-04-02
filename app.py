import streamlit as st
import requests
import re
from PIL import Image

# ==========================================
# 0. 頁面基本設定與自訂 CSS (美化介面 & 修復重疊 Bug)
# ==========================================
st.set_page_config(page_title="生態植物探索", page_icon="🌿", layout="centered")

# 使用 CSS 隱藏預設選單、優化卡片，並【修復手機版上傳按鈕文字重疊問題】
st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    
    /* 修復手機版上傳元件的文字重疊 (隱藏原生 input 文字) */
    .stFileUploader input[type="file"] {
        color: transparent !important;
    }
    .stFileUploader input::file-selector-button {
        display: none !important;
    }

    /* 數據卡片美化 */
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-title { font-size: 0.9rem; color: #6c757d; font-weight: 600; }
    .metric-value { font-size: 1.2rem; color: #198754; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 系統與 API 設定區塊
# ==========================================
# 請務必將下方的金鑰替換為你在 PlantNet 申請的真實 API Key
API_KEY = "在這裡填入你的_PlantNet_API_Key"
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# ==========================================
# 2. 核心功能函數區塊
# ==========================================
def has_chinese(text):
    """檢查字串中是否包含中文字元 (Unicode 範圍判定)"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search_wikidata_for_chinese(scientific_name):
    """
    透過全球 Wikidata (維基數據庫) 進行結構化精準檢索。
    能一併抓出該學名在兩岸三地所有的正式標籤 (labels) 與別名 (aliases)。
    """
    url = "https://www.wikidata.org/w/api.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    search_params = {
        "action": "wbsearchentities",
        "search": scientific_name,
        "language": "en",
        "format": "json",
        "type": "item"
    }
    
    try:
        search_res = requests.get(url, params=search_params, headers=headers).json()
        search_results = search_res.get("search", [])
        
        if not search_results:
            return None
            
        entity_id = search_results[0].get("id")
        
        get_params = {
            "action": "wbgetentities",
            "ids": entity_id,
            "languages": "zh|zh-tw|zh-hk|zh-cn|zh-hans|zh-hant", 
            "props": "labels|aliases",
            "format": "json"
        }
        
        entity_res = requests.get(url, params=get_params, headers=headers).json()
        entity_data = entity_res.get("entities", {}).get(entity_id, {})
        
        aliases_list = []
        
        # 1. 提取正式標籤 (Labels)
        labels = entity_data.get("labels", {})
        for lang, lang_data in labels.items():
            val = lang_data.get("value", "")
            if has_chinese(val):
                aliases_list.append(val)
                
        # 2. 提取所有別名 (Aliases)
        aliases = entity_data.get("aliases", {})
        for lang, lang_list in aliases.items():
            for alias_data in lang_list:
                val = alias_data.get("value", "")
                if has_chinese(val):
                    aliases_list.append(val)
        
        # 移除重複名稱並保持原有排序
        unique_aliases = list(dict.fromkeys(aliases_list))
        return unique_aliases if unique_aliases else None
        
    except Exception as e:
        return None

# ==========================================
# 3. 前端 UI 介面區塊
# ==========================================
st.title("🌿 生態探索雷達")
st.write("拍下身邊的植物，探索其生態價值與應用。")

# 上傳元件
uploaded_file = st.file_uploader("上傳照片 (支援相機即時拍攝)", type=["jpg", "jpeg", "png"])

# ==========================================
# 4. 主程式執行邏輯與卡片渲染
# ==========================================
if uploaded_file is not None:
    # 將圖片顯示置頂，模擬 APP 視覺
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)
    
    if st.button("✨ 開始深度辨識", use_container_width=True):
        with st.spinner("AI 模型分析與文獻檢索中..."):
            
            img_bytes = uploaded_file.getvalue()
            files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
            data = {'organs': ['auto']}
            
            response = requests.post(API_ENDPOINT, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                best_match = result['results'][0]
                
                # 提取分類資料
                scientific_name = best_match['species']['scientificNameWithoutAuthor']
                common_names = best_match['species'].get('commonNames', [])
                family_name = best_match['species'].get('family', {}).get('scientificNameWithoutAuthor', '未知')
                genus_name = best_match['species'].get('genus', {}).get('scientificNameWithoutAuthor', '未知')
                score = best_match['score'] * 100
                
                # 名稱檢索邏輯 (PlantNet -> Wikidata)
                chinese_names_list = [name for name in common_names if has_chinese(name)]
                unique_chinese_names = list(dict.fromkeys(chinese_names_list))
                
                if unique_chinese_names:
                    main_name = unique_chinese_names[0]
                    aliases_str = "、".join(unique_chinese_names[1:]) if len(unique_chinese_names) > 1 else "無其他紀錄"
                else:
                    wikidata_names_list = search_wikidata_for_chinese(scientific_name)
                    if wikidata_names_list:
                        main_name = wikidata_names_list[0]
                        aliases_str = "、".join(wikidata_names_list[1:]) if len(wikidata_names_list) > 1 else "無其他紀錄"
                    else:
                        main_name = "【資料不足，無法確認】"
                        aliases_str = "無"
                
                # ==========================================
                # 5. 分頁式卡片 UI 佈局呈現
                # ==========================================
                st.divider()
                
                # 標題與別名區塊
                st.markdown(f"## {main_name}")
                st.markdown(f"*{scientific_name}*")
                st.caption(f"**別名：** {aliases_str}")
                
                # 建立分頁標籤
                tab1, tab2 = st.tabs(["📝 總覽資訊", "🌱 生態與應用指南"])
                
                # [分頁 1]：總覽資訊
                with tab1:
                    # 警語提示區塊
                    st.warning("⚠️ **野外植物請注意！** 採集前請務必確認植物特性。若作為食材，請確保無毒性。")
                    
                    st.markdown("### 🧬 科學分類")
                    # 雙欄式數據卡片
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">科 (Family)</div><div class="metric-value">{family_name}</div></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="metric-card"><div class="metric-title">屬 (Genus)</div><div class="metric-value">{genus_name}</div></div>', unsafe_allow_html=True)
                    
                    st.markdown("### 📊 系統信心指數")
                    st.progress(int(score))
                    st.caption(f"AI 辨識準確率： {score:.2f}%")

                # [分頁 2]：生態與應用指南
                with tab2:
                    st.markdown("### 🛠️ 應用指南")
                    st.info("💡 **系統提示：** 以下為生態應用擴充版位。未來可串接專屬資料庫，自動帶入該植物在純素料理或自然工藝上的具體做法。")
                    
                    # 使用折疊面板呈現詳細指南
                    with st.expander("💧 澆水與環境 (範例版位)", expanded=True):
                        st.write("**光照需求：** 半日照至全日照。")
                        st.write("**水分管理：** 保持土壤微濕，避免積水。")
                    
                    with st.expander("✂️ 採集與修剪 (範例版位)"):
                        st.write("**適合季節：** 春季、秋季。")
                        st.write("**注意事項：** 採集時請保留母株生長空間，維護生態永續。")
                        
                    with st.expander("🍳 在地應用與料理 (範例版位)"):
                        st.write("**屬性：** 具備特定果膠或香氣。")
                        st.write("**料理建議：** 適合用於無五辛特色料理研發（如凝結豆腐、調味香草）。")

            else:
                st.error("辨識失敗，請確認網路連線或 API Key 是否正確。")
