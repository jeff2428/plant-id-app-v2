import streamlit as st
import requests
import re
from PIL import Image

# 1. 設置 API Key (請記得替換為你的金鑰)
API_KEY = "2b1004UqTrbWJn4mj5hqcaZN"
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# 【新增功能】：檢查字串中是否包含中文字元
def has_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

# 【升級功能】：維基百科搜尋函數 (改用 Search API 提高命中率)
def search_wikipedia_for_chinese(scientific_name):
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",             # 改用搜尋功能，而非死板的標題比對
        "srsearch": scientific_name,  # 直接把拉丁學名丟進去維基搜尋引擎
        "format": "json",
        "utf8": 1
    }
    try:
        res = requests.get(wiki_url, params=params).json()
        search_results = res.get("query", {}).get("search", [])
        if search_results:
            # 抓取第一筆搜尋結果的標題
            first_title = search_results[0].get("title", "")
            # 確保維基百科找出來的標題是中文
            if has_chinese(first_title):
                return first_title
    except Exception as e:
        return None
    return None

st.title("🌿 生態探索：植物辨識系統")
st.write("請上傳植物照片（建議清晰拍攝葉片或花朵）")

# 2. 建立上傳介面
uploaded_file = st.file_uploader("選擇圖片", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='已上傳照片', use_container_width=True)
    
    if st.button("開始辨識"):
        with st.spinner("AI 辨識中，並同步檢索文獻..."):
            # 3. 發送辨識請求
            img_bytes = uploaded_file.getvalue()
            files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
            data = {'organs': ['auto']}
            
            response = requests.post(API_ENDPOINT, files=files, data=data)
            
            # 4. 嚴格雙層驗證邏輯
            if response.status_code == 200:
                result = response.json()
                best_match = result['results'][0]
                scientific_name = best_match['species']['scientificNameWithoutAuthor']
                common_names = best_match['species'].get('commonNames', [])
                score = best_match['score'] * 100
                
                display_name = ""
                source = ""
                
                # 第一層：檢查 PlantNet API 回傳的清單中，有沒有「真正的中文」
                # (使用 next 尋找第一個有中文字元的俗名)
                plantnet_chinese_name = next((name for name in common_names if has_chinese(name)), None)
                
                if plantnet_chinese_name:
                    display_name = plantnet_chinese_name
                    source = "內建圖鑑"
                else:
                    # 第二層：如果沒有中文（或全都是英文），強制觸發維基百科搜尋
                    wiki_name = search_wikipedia_for_chinese(scientific_name)
                    if wiki_name:
                        display_name = wiki_name
                        source = "維基百科擴充"
                    else:
                        # 第三層：雙系統都找不到時的標準輸出
                        display_name = "【資料不足，無法確認】"
                        source = "無資料"
                
                # 輸出優化後的結果
                st.success(f"🎯 辨識結果：**{display_name}**")
                st.markdown(f"**學名：** *{scientific_name}*")
                st.info(f"準確率: {score:.2f}% (中文來源: {source})")
                
            else:
                st.error("辨識失敗，請確認網路連線或 API Key 是否正確。")
