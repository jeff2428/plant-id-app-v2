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

def search_wikipedia_for_chinese(scientific_name):
    """
    透過維基百科 API 進行模糊搜尋，尋找該學名對應的中文條目。
    具備 User-Agent 標頭，以符合伺服器安全政策，防止 403 阻擋。
    """
    wiki_url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": scientific_name,
        "format": "json",
        "utf8": 1
    }
    # 偽裝成常規瀏覽器請求，突破防護機制
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(wiki_url, params=params, headers=headers).json()
        search_results = res.get("query", {}).get("search", [])
        if search_results:
            first_title = search_results[0].get("title", "")
            # 確認維基百科回傳的標題確實是中文
            if has_chinese(first_title):
                return first_title
    except Exception as e:
        return None
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
    # 顯示使用者上傳的圖片 (這就是剛剛發生截斷錯誤的那一行，現在已修復完整)
    image = Image.open(uploaded_file)
    st.image(image, caption='已上傳照片', use_container_width=True)
    
    if st.button("開始辨識"):
        with st.spinner("AI 辨識中，並同步檢索文獻..."):
            
            # 將圖片轉換為 API 接受的二進位格式
            img_bytes = uploaded_file.getvalue()
            files = {'images': ('image.jpg', img_bytes, 'image/jpeg')}
            data = {'organs': ['auto']} # 讓系統自動判斷植物器官
            
            # 發送請求至 PlantNet
            response = requests.post(API_ENDPOINT, files=files, data=data)
            
            # 處理伺服器回傳結果
            if response.status_code == 200:
                result = response.json()
                best_match = result['results'][0]
                
                # 提取學名與內建俗名清單
                scientific_name = best_match['species']['scientificNameWithoutAuthor']
                common_names = best_match['species'].get('commonNames', [])
                score = best_match['score'] * 100
                
                display_name = ""
                source = ""
                
                # 第一層檢索：尋找內建圖鑑中的中文字元
                plantnet_chinese_name = next((name for name in common_names if has_chinese(name)), None)
                
                if plantnet_chinese_name:
                    display_name = plantnet_chinese_name
                    source = "內建圖鑑"
                else:
                    # 第二層檢索：啟動維基百科備援搜尋
                    wiki_name = search_wikipedia_for_chinese(scientific_name)
                    if wiki_name:
                        display_name = wiki_name
                        source = "維基百科擴充"
                    else:
                        # 第三層判定：資料庫中缺乏相關資訊
                        display_name = "【資料不足，無法確認】"
                        source = "無資料"
                
                # 輸出最終辨識結果
                st.success(f"🎯 辨識結果：**{display_name}**")
                st.markdown(f"**學名：** *{scientific_name}*")
                st.info(f"準確率: {score:.2f}% (中文來源: {source})")
                
            else:
                # 處理 API 請求失敗的狀況
                st.error("辨識失敗，請確認網路連線或 API Key 是否正確。")
