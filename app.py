import streamlit as st
import requests
import re
from PIL import Image

# ==========================================
# 1. 系統與 API 設定區塊
# ==========================================
# 請將下方的金鑰替換為你在 PlantNet 申請的真實 API Key
API_KEY = "2b1004UqTrbWJn4mj5hqcaZN"
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
    
    # 階段一：透過學名尋找 Wikidata 中的物種專屬 ID (例如 Q11100523)
    search_params = {
        "action": "wbsearchentities",
        "search": scientific_name,
        "language": "en", # 學名以英文/拉丁文檢索最準確
        "format": "json",
        "type": "item"
    }
    
    try:
        search_res = requests.get(url, params=search_params, headers=headers).json()
        search_results = search_res.get("search", [])
        
        if not search_results:
            return None
            
        entity_id = search_results[0].get("id")
        
        # 階段二：透過物種 ID，一口氣抓出所有中文語系的名稱
        get_params = {
            "action": "wbgetentities",
            "ids": entity_id,
            # 涵蓋繁體、簡體、台灣、香港等所有中文變體
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
st.title("🌿 生態探索：植物辨識系統")
st.write("請上傳植物照片（建議清晰拍攝葉片、花朵或果實特徵）")

uploaded_file = st.file_uploader("選擇圖片", type=["jpg", "jpeg", "png"])

# ==========================================
# 4. 主程式執行邏輯
# ==========================================
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='已上傳照片', use_container_width=True)
    
    if st.button("開始辨識"):
        with st.spinner("AI 辨識中，並同步連線全球維基數據庫檢索別名..."):
            
            img_bytes = uploaded_file.getvalue()
            files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
            data = {'organs': ['auto']}
            
            response = requests.post(API_ENDPOINT, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                best_match = result['results'][0]
                
                scientific_name = best_match['species']['scientificNameWithoutAuthor']
                common_names = best_match['species'].get('commonNames', [])
                score = best_match['score'] * 100
                
                display_name = ""
                source = ""
                
                # 第一層檢索：PlantNet 內建圖鑑
                chinese_names_list = [name for name in common_names if has_chinese(name)]
                unique_chinese_names = list(dict.fromkeys(chinese_names_list))
                
                if unique_chinese_names:
                    display_name = "、".join(unique_chinese_names)
                    source = f"內建圖鑑 ({len(unique_chinese_names)}筆名稱)"
                else:
                    # 第二層檢索：觸發 Wikidata 全球結構化資料庫搜尋
                    wikidata_names_list = search_wikidata_for_chinese(scientific_name)
                    if wikidata_names_list:
                        display_name = "、".join(wikidata_names_list)
                        source = f"全球維基數據庫 ({len(wikidata_names_list)}筆名稱)"
                    else:
                        display_name = "【資料不足，無法確認】"
                        source = "無資料"
                
                # 輸出最終辨識結果
                st.success(f"🎯 辨識結果：**{display_name}**")
                st.markdown(f"**學名：** *{scientific_name}*")
                st.info(f"準確率: {score:.2f}% (中文來源: {source})")
                
            else:
                st.error("辨識失敗，請確認網路連線或 API Key 是否正確。")
