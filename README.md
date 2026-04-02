# 🌿 植物辨識系統

基於 AI 深度學習的植物辨識應用，支援 45,000+ 物種辨識。

## 🚀 功能特色

- 📸 支援照片上傳與即時拍照
- 🤖 AI 智慧辨識植物種類
- 📚 自動查詢中文名稱（PlantNet + 維基百科）
- 📊 辨識信心指數顯示
- 🕐 歷史紀錄追蹤
- 📱 響應式設計（手機/平板/電腦）

## 🛠️ 技術堆疊

- **前端框架：** Streamlit
- **AI 引擎：** Pl@ntNet API
- **資料來源：** 維基百科 API
- **影像處理：** Pillow

## 📦 本地執行

```bash
# 1. 克隆專案
git clone https://github.com/你的使用者名稱/plant-identifier.git

# 2. 安裝套件
pip install -r requirements.txt

# 3. 執行應用
streamlit run app.py
