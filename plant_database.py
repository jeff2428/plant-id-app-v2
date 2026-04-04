import random
from datetime import datetime
import requests
from urllib.parse import quote

# ==========================================
# 從維基百科獲取圖片
# ==========================================
def get_wikipedia_image(plant_name):
    """從維基百科獲取植物圖片"""
    try:
        # 1. 搜尋頁面
        search_url = "https://zh.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": plant_name,
            "format": "json",
            "utf8": 1
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=5)
        search_data = search_response.json()
        
        results = search_data.get("query", {}).get("search", [])
        if not results:
            return None
            
        page_title = results[0].get("title", "")
        
        # 2. 獲取頁面圖片
        image_url = "https://zh.wikipedia.org/w/api.php"
        image_params = {
            "action": "query",
            "titles": page_title,
            "prop": "pageimages",
            "piprop": "original",
            "format": "json",
            "utf8": 1
        }
        
        image_response = requests.get(image_url, params=image_params, timeout=5)
        image_data = image_response.json()
        
        pages = image_data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            original_image = page_info.get("original", {})
            if original_image:
                return original_image.get("source")
        
        # 3. 如果沒有主圖片，嘗試獲取第一張圖片
        images_params = {
            "action": "query",
            "titles": page_title,
            "prop": "images",
            "imlimit": 10,
            "format": "json",
            "utf8": 1
        }
        
        images_response = requests.get(image_url, params=images_params, timeout=5)
        images_data = images_response.json()
        
        pages = images_data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            images = page_info.get("images", [])
            for img in images:
                img_title = img.get("title", "")
                # 過濾掉圖標和 SVG
                if any(x in img_title.lower() for x in ['.jpg', '.jpeg', '.png']):
                    if not any(x in img_title.lower() for x in ['icon', 'logo', 'symbol']):
                        # 獲取圖片 URL
                        img_url_params = {
                            "action": "query",
                            "titles": img_title,
                            "prop": "imageinfo",
                            "iiprop": "url",
                            "format": "json",
                            "utf8": 1
                        }
                        img_url_response = requests.get(image_url, params=img_url_params, timeout=5)
                        img_url_data = img_url_response.json()
                        
                        img_pages = img_url_data.get("query", {}).get("pages", {})
                        for img_page_id, img_page_info in img_pages.items():
                            imageinfo = img_page_info.get("imageinfo", [])
                            if imageinfo:
                                return imageinfo[0].get("url")
        
        return None
        
    except Exception as e:
        print(f"獲取維基百科圖片失敗: {e}")
        return None

# ==========================================
# 植物資料庫
# ==========================================
PLANT_DATABASE = {
    1: {
        "name": "玫瑰",
        "scientific_name": "Rosa rugosa",
        "family": "薔薇科",
        "genus": "薔薇屬",
        "origin": "中國、日本、朝鮮半島",
        "image": None,  # 將從維基百科獲取
        "brief": "玫瑰是薔薇科薔薇屬植物，被譽為「花中皇后」，以其芳香和美麗的花朵聞名於世。",
        "description": """玫瑰原產於亞洲東部地區，現已遍布世界各地。植株為落葉灌木，莖直立，多刺，葉片為奇數羽狀複葉。

花朵通常為重瓣，顏色豐富多樣，包括紅色、粉色、白色、黃色等。花期主要在春季至秋季，具有濃郁的香氣。

玫瑰不僅具有觀賞價值，其花瓣還可用於提取精油、製作花茶和食品。在園藝栽培中，玫瑰有數千個品種，是世界上最受歡迎的觀賞植物之一。""",
        "flower_language": "愛情、美麗、熱情",
        "symbolism": "玫瑰象徵著愛情與浪漫，不同顏色代表不同的情感：紅玫瑰代表熱烈的愛，粉玫瑰象徵感激與欣賞，白玫瑰代表純潔與尊敬，黃玫瑰則表示友誼與關懷。",
        "tags": ["觀賞植物", "芳香植物", "藥用植物", "庭園花卉"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照（每天6-8小時）",
            "water": "保持土壤濕潤，避免積水",
            "temperature": "15-25°C",
            "humidity": "中等濕度（50-70%）",
            "soil": "排水良好的微酸性土壤",
            "fertilizer": "生長期每2-3週施肥一次",
            "pruning": "早春修剪枯枝和弱枝"
        }
    },
    
    2: {
        "name": "薰衣草",
        "scientific_name": "Lavandula angustifolia",
        "family": "唇形科",
        "genus": "薰衣草屬",
        "origin": "地中海沿岸",
        "image": None,
        "brief": "薰衣草是唇形科薰衣草屬的常綠小灌木，以其優雅的紫色花穗和獨特的芳香而聞名。",
        "description": """薰衣草原產於地中海沿岸，是一種多年生常綠小灌木。植株高度約30-60公分，莖直立，呈方形，全株覆蓋細小絨毛。

葉片狹長呈線形或披針形，對生排列，呈灰綠色。花序為穗狀，著生於枝條頂端，花朵小巧呈管狀，顏色以淡紫色、深紫色最常見，也有白色和粉色品種。

薰衣草具有強烈的芳香，富含揮發油，廣泛應用於香水、精油、藥用和觀賞。其精油具有鎮靜、舒緩、殺菌等功效，是芳香療法的重要原料。""",
        "flower_language": "等待愛情、寧靜、優雅",
        "symbolism": "薰衣草象徵純潔、清新和寧靜。在法國普羅旺斯，薰衣草田是浪漫的代名詞。它也代表著等待和期盼，傳說中聞到薰衣草香氣就會遇到真愛。",
        "tags": ["芳香植物", "觀賞植物", "藥用植物", "精油原料"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照（每天至少6小時）",
            "water": "耐旱，土壤乾燥後再澆水",
            "temperature": "15-30°C",
            "humidity": "低濕度環境",
            "soil": "排水良好的鹼性或中性土壤",
            "fertilizer": "少量施肥，生長期每月一次",
            "pruning": "花後修剪促進分枝"
        }
    },
    
    3: {
        "name": "向日葵",
        "scientific_name": "Helianthus annuus",
        "family": "菊科",
        "genus": "向日葵屬",
        "origin": "北美洲",
        "image": None,
        "brief": "向日葵是菊科向日葵屬的一年生草本植物，以其碩大的花盤和向陽性而聞名，象徵著光明與希望。",
        "description": """向日葵原產於北美洲，是一種高大的一年生草本植物，莖可高達1-3公尺。莖直立粗壯，表面有剛毛，單一不分枝或少分枝。

葉片互生，呈心形或卵形，邊緣有鋸齒，表面粗糙。最顯著的特徵是其碩大的頭狀花序，直徑可達10-40公分，由周圍的舌狀花（通常為黃色）和中央的管狀花（褐色或紫色）組成。

向日葵具有明顯的向光性，花盤會隨太陽移動，這種現象稱為「向日性」。其種子富含油脂，是重要的油料作物，也可作為休閒食品。""",
        "flower_language": "忠誠、愛慕、光輝",
        "symbolism": "向日葵象徵著忠誠和堅定的信念，因其始終追隨太陽而得名。它代表著光明、希望和正能量，是積極向上精神的象徵。在藝術作品中，向日葵常被用來表達對生命的熱愛。",
        "tags": ["觀賞植物", "油料作物", "食用植物", "庭園花卉"],
        "seasons": ["夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照（每天至少8小時）",
            "water": "保持土壤濕潤，生長期需水量大",
            "temperature": "20-30°C",
            "humidity": "中等濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "生長期每2週施肥一次",
            "pruning": "不需要特別修剪"
        }
    },
    
    4: {
        "name": "櫻花",
        "scientific_name": "Prunus serrulata",
        "family": "薔薇科",
        "genus": "櫻屬",
        "origin": "東亞（中國、日本、韓國）",
        "image": None,
        "brief": "櫻花是薔薇科櫻屬植物的統稱，以其短暫而絢爛的花期和優雅的姿態，成為東亞文化的重要象徵。",
        "description": """櫻花原產於東亞地區，是溫帶地區重要的觀賞花木。樹高可達4-16公尺，樹皮平滑，呈紫褐色或灰褐色，具有明顯的橫紋。

葉片互生，呈橢圓形或倒卵形，邊緣有細鋸齒，秋季葉色轉為橙紅色。花朵通常在早春綻放，花色有白色、粉紅色或淡紅色，花瓣5枚，部分品種為重瓣。

櫻花的花期短暫，通常只有7-10天，這種「物哀之美」在日本文化中具有特殊意義。全世界有200多個櫻花品種，其中日本培育的品種最為著名。""",
        "flower_language": "生命、幸福、純潔",
        "symbolism": "櫻花象徵著生命的短暫與美好，代表著把握當下和珍惜時光的精神。在日本文化中，櫻花象徵著武士道精神中的「生如夏花之絢爛」。櫻花季也代表著新的開始和希望。",
        "tags": ["觀賞植物", "文化植物", "行道樹", "春季花卉"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照至半日照",
            "water": "保持土壤適度濕潤",
            "temperature": "0-25°C（需要冷涼期）",
            "humidity": "中等濕度",
            "soil": "排水良好的微酸性土壤",
            "fertilizer": "春秋兩季施肥",
            "pruning": "花後適度修剪整形"
        }
    },
    
    5: {
        "name": "茉莉花",
        "scientific_name": "Jasminum sambac",
        "family": "木犀科",
        "genus": "素馨屬",
        "origin": "印度、東南亞",
        "image": None,
        "brief": "茉莉花是木犀科素馨屬的常綠灌木，以其潔白的花朵和濃郁的香氣而聞名，是重要的香料植物。",
        "description": """茉莉花原產於印度和東南亞地區，是一種攀援性常綠灌木，莖細長柔軟，可長達2-3公尺。葉片對生，呈卵形或橢圓形，深綠色且有光澤。

花朵通常在夏季盛開，花色純白，花瓣通常為5-9枚，部分品種為重瓣。花朵在傍晚和夜間香氣最為濃郁，這種特性使其成為提取精油和製作香水的重要原料。

茉莉花在中國文化中地位崇高,常被用於花茶製作。茉莉花茶是中國十大名茶之一,以其獨特的香氣深受喜愛。此外,茉莉花也是菲律賓、印尼等國的國花。""",
        "flower_language": "純潔、忠貞、尊敬",
        "symbolism": "茉莉花象徵著純潔的愛情和忠貞不渝的感情。在東南亞文化中,茉莉花代表著母愛和尊敬。其潔白的花朵和清新的香氣也象徵著優雅與高貴。",
        "tags": ["芳香植物", "觀賞植物", "茶用植物", "精油原料"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照至半日照",
            "water": "保持土壤濕潤,避免過濕",
            "temperature": "20-35°C",
            "humidity": "高濕度環境",
            "soil": "排水良好的微酸性土壤",
            "fertilizer": "生長期每2週施肥一次",
            "pruning": "花後修剪促進新枝生長"
        }
    },
    
    6: {
        "name": "鬱金香",
        "scientific_name": "Tulipa gesneriana",
        "family": "百合科",
        "genus": "鬱金香屬",
        "origin": "中亞、土耳其",
        "image": None,
        "brief": "鬱金香是百合科鬱金香屬的多年生球根植物,以其優雅的杯狀花朵和豐富的色彩聞名,是荷蘭的國花。",
        "description": """鬱金香原產於中亞和土耳其地區,16世紀傳入歐洲後引發了著名的「鬱金香狂熱」。植株高度約20-50公分,由地下鱗莖生長而出。

葉片基生,呈帶狀或披針形,藍綠色且表面有蠟質。花莖直立,頂端著生單朵花,花朵呈杯狀或碗狀,花瓣6枚,顏色極為豐富,包括紅、黃、白、紫、粉等及其漸變色。

鬱金香品種超過8000個,按花期分為早花、中花、晚花品種。在荷蘭,每年春季都會舉辦盛大的鬱金香花展,吸引世界各地的遊客。""",
        "flower_language": "愛的表白、榮譽、祝福",
        "symbolism": "鬱金香象徵著高雅、富貴和永恆的愛。不同顏色代表不同含義:紅色象徵愛的宣言,黃色代表開朗,白色表示純潔,紫色象徵高貴。在土耳其文化中,鬱金香代表著天堂和神聖。",
        "tags": ["觀賞植物", "球根花卉", "春季花卉", "切花"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照至半日照",
            "water": "生長期保持濕潤,休眠期減少澆水",
            "temperature": "15-20°C(需低溫春化)",
            "humidity": "中等濕度",
            "soil": "排水良好的沙質壤土",
            "fertilizer": "種植時施基肥,生長期追肥",
            "pruning": "花後剪除花莖,保留葉片"
        }
    },
    
    7: {
        "name": "蓮花",
        "scientific_name": "Nelumbo nucifera",
        "family": "蓮科",
        "genus": "蓮屬",
        "origin": "亞洲、澳洲北部",
        "image": None,
        "brief": "蓮花是蓮科蓮屬的多年生水生植物,因其「出淤泥而不染」的特性,在東方文化中具有深刻的象徵意義。",
        "description": """蓮花是古老的水生植物,化石記錄可追溯到1億年前。植株由地下根莖(藕)生長,葉片圓形盾狀,直徑可達60公分,表面有蠟質,具疏水性。

花朵碩大美麗,直徑10-25公分,花瓣多層,顏色有白、粉、紅等。花朵在清晨開放,傍晚閉合,具有獨特的「恆溫」現象,能保持花溫在30-35°C。

蓮花全身是寶:蓮子可食用,蓮藕是常見蔬菜,蓮葉可入藥,花朵可觀賞。在佛教文化中,蓮花象徵著覺悟和清淨,是最神聖的植物之一。""",
        "flower_language": "清廉、純潔、堅貞",
        "symbolism": "蓮花象徵著清白、高潔,因其生長在污泥中卻保持潔淨而被視為君子的象徵。在佛教中代表覺悟和超脫,在中國文化中象徵品格高尚。蓮花「花果同時」的特性也代表因果相應。",
        "tags": ["水生植物", "觀賞植物", "食用植物", "藥用植物"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照(每天至少6小時)",
            "water": "需在水中栽培,水深10-20公分",
            "temperature": "20-30°C",
            "humidity": "高濕度(水生環境)",
            "soil": "富含有機質的塘泥",
            "fertilizer": "生長期定期施水生植物專用肥",
            "pruning": "及時清除枯葉殘花"
        }
    }
}

# ==========================================
# 獲取植物資料（自動獲取維基圖片）
# ==========================================
def get_plant_data(plant_id):
    """獲取植物資料,並從維基百科獲取圖片"""
    if plant_id not in PLANT_DATABASE:
        return None
    
    plant = PLANT_DATABASE[plant_id].copy()
    
    # 如果沒有圖片,從維基百科獲取
    if not plant.get("image"):
        wiki_image = get_wikipedia_image(plant["name"])
        if wiki_image:
            plant["image"] = wiki_image
        else:
            # 備用圖片
            plant["image"] = f"https://via.placeholder.com/400x300/2d5c3a/ffffff?text={quote(plant['name'])}"
    
    return plant

# ==========================================
# 今日推薦植物
# ==========================================
def get_daily_plant():
    """根據日期返回每日推薦植物"""
    today = datetime.now()
    plant_id = (today.timetuple().tm_yday % len(PLANT_DATABASE)) + 1
    return get_plant_data(plant_id)

# ==========================================
# 根據 ID 獲取植物
# ==========================================
def get_plant_by_id(plant_id):
    """根據 ID 獲取特定植物"""
    return get_plant_data(plant_id)

# ==========================================
# 隨機獲取植物
# ==========================================
def get_random_plants(count=3):
    """隨機獲取指定數量的植物"""
    plant_ids = random.sample(list(PLANT_DATABASE.keys()), min(count, len(PLANT_DATABASE)))
    return [get_plant_data(pid) for pid in plant_ids if get_plant_data(pid)]

# ==========================================
# 搜尋植物
# ==========================================
def search_plants(keyword):
    """根據關鍵字搜尋植物"""
    results = []
    keyword = keyword.lower()
    
    for plant_id, plant_data in PLANT_DATABASE.items():
        if (keyword in plant_data["name"].lower() or 
            keyword in plant_data["scientific_name"].lower() or
            keyword in plant_data["family"].lower()):
            results.append(get_plant_data(plant_id))
    
    return results

# ==========================================
# 獲取所有植物
# ==========================================
def get_all_plants():
    """獲取所有植物資料"""
    return [get_plant_data(pid) for pid in PLANT_DATABASE.keys()]

# ==========================================
# 獲取植物總數
# ==========================================
def get_plant_count():
    """獲取植物資料庫中的植物總數"""
    return len(PLANT_DATABASE)
