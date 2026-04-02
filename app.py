import streamlit as st
import requests
import re
from PIL import Image

# ==========================================
# 1. 系統與 API 設定區塊
# ==========================================
API_KEY = "2b1004UqTrbWJn4mj5hqcaZN"
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# ==========================================
# 2. 核心功能函數區塊
# ==========================================
def has_chinese(text):
    """檢查字串中是否包含中文字元 (Unicode 範圍判定)"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search_wikipedia_for_chinese(scientific_name):
    """
    透過維基百科 API 進行模糊搜尋，並利用「重新導向 (Redirects)」功能抓取所有別名。
    """
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # 階段一：搜尋主條目名稱
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": scientific_name,
        "format": "json",
        "utf8": 1
    }
    
    try:
        search_res = requests.get(wiki_url, params=search_params, headers=headers).json()
        search_results = search_res.get("query", {}).get("search", [])
        if not search_results:
            return None
            
        main_title = search_results[0].get("title", "")
        if not has_chinese(main_title):
            return None
            
        # 階段二：抓取該條目的所有重新導向 (鄉土俗名或別名)
        redirect_params = {
            "action": "query",
            "titles": main_title,
            "prop": "redirects",
            "rdlimit": "50", # 最多抓取 50 個別名
            "format": "json",
            "utf8": 1
        }
        
        rd_res = requests.get(wiki_url, params=redirect_params, headers=headers).json()
        pages = rd_res.get("query", {}).get("pages", {})
        
        aliases = [main_title] # 將主名稱先放入清單
        
        # 解析回傳的重新導向名單
        for page_id, page_info in pages.items():
            if "redirects" in page_info:
                for rd in page_info["redirects"]:
                    title = rd["title"]
                    # 排除維基百科內部系統頁面(如含冒號的分類頁)並確保名稱含有中文
                    if ":" not in title and has_chinese(title):
                        aliases.append(title)
                        
        # 移除重複的名稱，並保持原始排序
        unique_aliases = list(dict.fromkeys(aliases))
        return unique_aliases
        
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
        with st.spinner("AI 辨識中，並同步深度檢索文獻與別名..."):
            
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
                    # 第二層檢索：觸發升級版的維基百科深度搜尋
                    wiki_names_list = search_wikipedia_for_chinese(scientific_name)
                    if wiki_names_list:
                        display_name = "、".join(wiki_names_list)
                        source = f"維基百科擴充 ({len(wiki_names_list)}筆名稱)"
                    else:
                        display_name = "【資料不足，無法確認】"
                        source = "無資料"
                
                # 輸出最終辨識結果
                st.success(f"🎯 辨識結果：**{display_name}**")
                st.markdown(f"**學名：** *{scientific_name}*")
                st.info(f"準確率: {score:.2f}% (中文來源: {source})")
                
            else:
                st.error("辨識失敗，請確認網路連線或 API Key 是否正確。")
