import streamlit as st
import requests
from PIL import Image

# 1. 設置你的 API Key，並在網址最後加上 &lang=zh 要求回傳中文
API_KEY = "2b1004UqTrbWJn4mj5hqcaZN"
API_ENDPOINT = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}&lang=zh"

st.title("🌿 生態探索：植物辨識系統")
st.write("請上傳植物照片（建議清晰拍攝葉片或花朵）")

# 2. 建立上傳介面
uploaded_file = st.file_uploader("選擇圖片", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 顯示上傳的照片
    image = Image.open(uploaded_file)
    st.image(image, caption='已上傳照片', use_container_width=True)
    
    if st.button("開始辨識"):
        with st.spinner("AI 辨識中..."):
            # 3. 將圖片轉換為 API 接受的格式並發送請求
            img_bytes = uploaded_file.getvalue()
            files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
            data = {'organs': ['auto']}
            
            response = requests.post(API_ENDPOINT, files=files, data=data)
            
            # 4. 處理回傳結果 (加入中文俗名判斷邏輯)
            if response.status_code == 200:
                result = response.json()
                best_match = result['results'][0]
                scientific_name = best_match['species']['scientificNameWithoutAuthor']
                
                # 取得俗名清單 (API 有時會回傳空集合，因此使用 .get 避免程式報錯)
                common_names = best_match['species'].get('commonNames', [])
                
                # 判斷：如果有中文俗名就優先顯示，否則退回顯示學名
                if common_names:
                    display_name = f"{common_names[0]} (學名: {scientific_name})"
                else:
                    display_name = f"無中文紀錄 (學名: {scientific_name})"
                    
                score = best_match['score'] * 100
                
                st.success(f"🎯 辨識結果：**{display_name}**")
                st.info(f"準確率: {score:.2f}%")
            else:
                st.error("辨識失敗，請確認網路連線或 API Key 是否正確。")
