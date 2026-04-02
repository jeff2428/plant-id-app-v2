import streamlit as st
import requests
from PIL import Image

# 1. 設置你的 API Key
API_KEY = "2b1004UqTrbWJn4mj5hqcaZN"
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

# 建立一個維基百科搜尋函數
def search_wikipedia_for_chinese(scientific_name):
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": scientific_name,
        "redirects": 1, # 開啟重新導向，學名通常會導向中文俗名頁面
        "format": "json",
        "uselang": "zh-tw"
    }
    try:
        res = requests.get(wiki_url, params=params).json()
        pages = res.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if int(page_id) > 0: # 如果 page_id 大於 0 代表有找到頁面
                title = page_data.get("title", "")
                # 如果回傳的標題跟原本的學名不同，通常代表成功轉成了中文俗名
                if title.lower() != scientific_name.lower():
                    return title
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
            
            # 4. 雙層驗證資料處理邏輯
            if response.status_code == 200:
                result = response.json()
                best_match = result['results'][0]
                scientific_name = best_match['species']['scientificNameWithoutAuthor']
                common_names = best_match['species'].get('commonNames', [])
                score = best_match['score'] * 100
                
                # 第一層：檢查 PlantNet API 是否有自帶中文
                if common_names:
                    display_name = f"{common_names[0]}"
                    source = "內建圖鑑"
                else:
                    # 第二層：觸發維基百科爬蟲救援
                    wiki_name = search_wikipedia_for_chinese(scientific_name)
                    if wiki_name:
                        display_name = f"{wiki_name}"
                        source = "維基百科擴充"
                    else:
                        display_name = "無中文紀錄"
                        source = "無資料"
                
                # 輸出優化後的結果
                st.success(f"🎯 辨識結果：**{display_name}**")
                st.markdown(f"**學名：** *{scientific_name}*")
                st.info(f"準確率: {score:.2f}% (中文來源: {source})")
                
            else:
                st.error("辨識失敗，請確認網路連線或 API Key 是否正確。")
