import random
from datetime import datetime
import requests
from urllib.parse import quote
import time
import os
import json

# ==========================================
# 圖片快取目錄
# ==========================================
CACHE_DIR = os.path.join(os.path.dirname(__file__), '.image_cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_path(plant_name):
    """取得圖片快取檔案路徑"""
    safe_name = "".join(c for c in plant_name if c.isalnum() or c in (' ', '-', '_')).strip()
    return os.path.join(CACHE_DIR, f"{safe_name}.json")

def _load_image_cache(plant_name):
    """載入圖片快取"""
    cache_path = _get_cache_path(plant_name)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('image_url')
        except:
            return None
    return None

def _save_image_cache(plant_name, image_url):
    """儲存圖片快取"""
    cache_path = _get_cache_path(plant_name)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump({'image_url': image_url, 'cached_at': datetime.now().isoformat()}, f)
    except:
        pass

# ==========================================
# 從維基百科獲取圖片（改進版）
# ==========================================
def get_wikipedia_image(plant_name, scientific_name=None):
    """從維基百科獲取植物圖片 - 改進版"""
    try:
        base_url = "https://zh.wikipedia.org/w/api.php"
        
        # 嘗試順序：1.中文名 2.學名 3.中文名+植物
        search_terms = [plant_name]
        if scientific_name:
            search_terms.append(scientific_name)
        search_terms.append(f"{plant_name}植物")
        
        for search_term in search_terms:
            # 步驟1: 精確搜尋頁面標題
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": search_term,
                "srnamespace": "0",
                "srlimit": "3",
                "format": "json",
                "utf8": 1
            }
            
            response = requests.get(base_url, params=search_params, timeout=10)
            data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            
            for result in search_results:
                page_title = result.get("title", "")
                
                if not is_relevant_page(page_title, plant_name, scientific_name):
                    continue
                
                image_url = get_page_main_image(page_title)
                
                if image_url and is_valid_plant_image(image_url):
                    print(f"✓ 找到圖片: {page_title} -> {image_url[:80]}...")
                    return image_url
                
                infobox_image = get_infobox_image(page_title)
                if infobox_image and is_valid_plant_image(infobox_image):
                    print(f"✓ 找到 Infobox 圖片: {page_title} -> {infobox_image[:80]}...")
                    return infobox_image
            
            time.sleep(0.5)
        
        print(f"✗ 未找到合適圖片: {plant_name}")
        return None
        
    except Exception as e:
        print(f"✗ 獲取圖片時發生錯誤 ({plant_name}): {e}")
        return None

def is_relevant_page(page_title, plant_name, scientific_name):
    """判斷頁面是否與植物相關"""
    page_title_lower = page_title.lower()
    
    exclude_keywords = ['列表', '分類', '消歧義', 'disambig', 'list of', 'category']
    if any(keyword in page_title_lower for keyword in exclude_keywords):
        return False
    
    if plant_name in page_title:
        return True
    
    if scientific_name and scientific_name.lower() in page_title_lower:
        return True
    
    return False

def get_page_main_image(page_title):
    """獲取頁面的主要圖片"""
    try:
        base_url = "https://zh.wikipedia.org/w/api.php"
        
        params = {
            "action": "query",
            "titles": page_title,
            "prop": "pageimages",
            "piprop": "original",
            "format": "json",
            "utf8": 1
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":
                original = page_data.get("original", {})
                if original:
                    return original.get("source")
        
        return None
        
    except Exception as e:
        print(f"獲取主圖失敗: {e}")
        return None

def get_infobox_image(page_title):
    """從頁面的 Infobox 獲取圖片"""
    try:
        base_url = "https://zh.wikipedia.org/w/api.php"
        
        params = {
            "action": "parse",
            "page": page_title,
            "prop": "images",
            "format": "json",
            "utf8": 1
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        images = data.get("parse", {}).get("images", [])
        
        for image_name in images[:5]:
            if is_likely_plant_photo(image_name):
                image_url = get_image_url(image_name)
                if image_url:
                    return image_url
        
        return None
        
    except Exception as e:
        print(f"獲取 Infobox 圖片失敗: {e}")
        return None

def is_likely_plant_photo(filename):
    """判斷檔案名是否像是植物照片"""
    filename_lower = filename.lower()
    
    if not any(ext in filename_lower for ext in ['.jpg', '.jpeg', '.png']):
        return False
    
    exclude = ['icon', 'logo', 'symbol', 'map', 'chart', 'diagram', 
               'graph', 'flag', 'coat', 'emblem', 'signature']
    if any(word in filename_lower for word in exclude):
        return False
    
    prefer = ['flower', 'plant', 'tree', 'leaf', 'blossom', 
              '花', '植物', '樹', '葉']
    if any(word in filename_lower for word in prefer):
        return True
    
    return True

def get_image_url(image_name):
    """根據圖片檔案名獲取完整 URL"""
    try:
        base_url = "https://zh.wikipedia.org/w/api.php"
        
        params = {
            "action": "query",
            "titles": f"File:{image_name}",
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
            "utf8": 1
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            imageinfo = page_data.get("imageinfo", [])
            if imageinfo:
                return imageinfo[0].get("url")
        
        return None
        
    except Exception as e:
        print(f"獲取圖片 URL 失敗: {e}")
        return None

def is_valid_plant_image(url):
    """驗證圖片 URL 是否有效"""
    if not url:
        return False
    
    url_lower = url.lower()
    
    if not any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png']):
        return False
    
    exclude = ['icon', 'logo', 'symbol', 'commons-logo', 'wiki']
    if any(word in url_lower for word in exclude):
        return False
    
    return True

def search_commons_image(plant_name, scientific_name=None):
    """從 Wikimedia Commons 搜尋植物圖片"""
    try:
        base_url = "https://commons.wikimedia.org/w/api.php"
        
        search_term = scientific_name if scientific_name else plant_name
        
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_term,
            "srnamespace": "6",
            "srlimit": "5",
            "format": "json",
            "utf8": 1
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        results = data.get("query", {}).get("search", [])
        
        for result in results:
            title = result.get("title", "")
            if is_likely_plant_photo(title):
                image_url = get_commons_image_url(title)
                if image_url:
                    print(f"✓ 從 Commons 找到圖片: {title[:50]}...")
                    return image_url
        
        return None
        
    except Exception as e:
        print(f"Commons 搜尋失敗: {e}")
        return None

def get_commons_image_url(title):
    """從 Commons 獲取圖片 URL"""
    try:
        base_url = "https://commons.wikimedia.org/w/api.php"
        
        params = {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
            "utf8": 1
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            imageinfo = page_data.get("imageinfo", [])
            if imageinfo:
                return imageinfo[0].get("url")
        
        return None
        
    except Exception as e:
        return None

# ==========================================
# 推薦原由系統
# ==========================================
def get_recommendation_reason(date, plant):
    """根據日期生成推薦原由"""
    month = date.month
    day = date.day
    weekday = date.weekday()  # 0=週一, 6=週日
    season = get_season(month)
    
    reasons = []
    
    # 1. 特殊節日推薦
    special_day = check_special_day(month, day)
    if special_day:
        reasons.append({
            "icon": "🎉",
            "title": "特殊節日",
            "content": special_day
        })
    
    # 2. 季節推薦
    if season in plant.get("seasons", []):
        season_reason = {
            "春季": f"現在是{season}，正是{plant['name']}的最佳觀賞期，花朵盛開，生機勃勃",
            "夏季": f"{season}時節，{plant['name']}在陽光下綻放，展現其最燦爛的姿態",
            "秋季": f"進入{season}，{plant['name']}依然美麗，為秋日增添一抹亮色",
            "冬季": f"{season}中的{plant['name']}別有韻味，在寒冷中展現堅韌之美"
        }
        reasons.append({
            "icon": "🌸",
            "title": "當季推薦",
            "content": season_reason.get(season, f"適合{season}種植觀賞")
        })
    
    # 3. 週間推薦
    weekday_reasons = get_weekday_reason(weekday, plant)
    if weekday_reasons:
        reasons.append(weekday_reasons)
    
    # 4. 數字吉祥寓意
    number_reason = get_number_meaning(day, plant)
    if number_reason:
        reasons.append(number_reason)
    
    # 5. 氣候適宜性
    climate_reason = get_climate_reason(month, plant)
    if climate_reason:
        reasons.append(climate_reason)
    
    # 如果沒有特別原由，添加通用推薦
    if not reasons:
        reasons.append({
            "icon": "✨",
            "title": "今日推薦",
            "content": f"{plant['name']}以其{plant['flower_language']}的花語，為您的一天帶來美好祝福"
        })
    
    return reasons

def get_season(month):
    """根據月份判斷季節（台灣氣象季節）"""
    if month in [3, 4, 5]:
        return "春季"
    elif month in [6, 7, 8]:
        return "夏季"
    elif month in [9, 10, 11]:
        return "秋季"
    else:  # 12, 1, 2
        return "冬季"

def check_special_day(month, day):
    """檢查特殊節日"""
    special_days = {
        (1, 1): "元旦新年，萬象更新，適合以花卉迎接新的開始",
        (2, 14): "情人節，用花朵傳遞愛意與浪漫",
        (3, 8): "婦女節，以花朵致敬每一位女性",
        (3, 12): "植樹節，一起關注綠色生態",
        (4, 5): "清明時節，春意盎然，正是賞花好時光",
        (5, 1): "勞動節，用美麗的植物犒賞辛勤的自己",
        (5, 14): "母親節，用花朵表達對母親的感恩",
        (6, 1): "兒童節，讓孩子認識大自然的美好",
        (7, 7): "七夕情人節，以花傳情，浪漫滿分",
        (8, 8): "父親節，用植物的堅韌象徵父愛",
        (9, 10): "教師節，以花朵感謝師恩",
        (10, 1): "國慶日，舉國同慶，花開盛世",
        (10, 31): "萬聖節，感受大自然的神秘魅力",
        (11, 1): "植物保護日，認識並珍惜每一種植物",
        (12, 25): "聖誕節，用綠色植物裝點節日氛圍"
    }
    return special_days.get((month, day))

def get_weekday_reason(weekday, plant):
    """根據星期幾生成推薦原由"""
    weekday_meanings = {
        0: {  # 週一
            "icon": "💪",
            "title": "週一能量",
            "content": f"週一需要正能量！{plant['name']}的{plant['flower_language']}，為新的一週注入活力"
        },
        1: {  # 週二
            "icon": "🌱",
            "title": "持續成長",
            "content": f"週二繼續努力，{plant['name']}的生長過程提醒我們堅持不懈"
        },
        2: {  # 週三
            "icon": "⚖️",
            "title": "週中平衡",
            "content": f"週三過半，用{plant['name']}的美麗平衡工作與生活"
        },
        3: {  # 週四
            "icon": "🎯",
            "title": "即將收穫",
            "content": f"週四將至週末，{plant['name']}象徵著即將到來的美好"
        },
        4: {  # 週五
            "icon": "🎊",
            "title": "週五驚喜",
            "content": f"週五到了！用{plant['name']}的芬芳迎接週末時光"
        },
        5: {  # 週六
            "icon": "🌈",
            "title": "週末悠閒",
            "content": f"週末好時光，適合欣賞{plant['name']}，享受愜意生活"
        },
        6: {  # 週日
            "icon": "☀️",
            "title": "週日陽光",
            "content": f"週日休息日，{plant['name']}陪伴您度過美好的一天"
        }
    }
    return weekday_meanings.get(weekday)

def get_number_meaning(day, plant):
    """根據日期數字生成寓意"""
    special_numbers = {
        1: "一心一意",
        2: "好事成雙",
        3: "三陽開泰",
        5: "五福臨門",
        6: "六六大順",
        8: "發發發，好運連連",
        9: "長長久久",
        10: "十全十美",
        13: "一生",
        14: "一世",
        20: "愛您",
        21: "愛您一生",
        25: "聖誕快樂",
        28: "發發發"
    }
    
    if day in special_numbers:
        return {
            "icon": "🎲",
            "title": f"吉祥數字 {day}",
            "content": f"今天是{day}號，{special_numbers[day]}，{plant['name']}為您帶來好運"
        }
    return None

def get_climate_reason(month, plant):
    """根據氣候給出推薦原由"""
    care = plant.get("care", {})
    
    climate_reasons = {
        1: "寒冬時節",
        2: "早春回暖",
        3: "春暖花開",
        4: "春末夏初",      # 修改這裡
        5: "初夏時光",
        6: "盛夏驕陽",
        7: "炎炎夏日",
        8: "酷暑時節",      # 修改這裡
        9: "夏末初秋",      # 修改這裡
        10: "秋高氣爽",
        11: "深秋時節",
        12: "寒冬臘月"
    }
    
    if month in climate_reasons:
        return {
            "icon": "🌡️",
            "title": "氣候適宜",
            "content": f"{climate_reasons[month]}，{plant['name']}在此氣候下{get_growth_status(month, plant)}"
        }
    return None

def get_growth_status(month, plant):
    """獲取植物在當前月份的生長狀態"""
    seasons = plant.get("seasons", [])
    season = get_season(month)
    
    if season in seasons:
        return "正值生長旺季，美不勝收"
    elif season == "春季":
        return "開始萌發新芽，充滿生機"
    elif season == "夏季":
        return "需要細心呵護，回報以繁茂"
    elif season == "秋季":
        return "展現成熟之美，韻味獨特"
    else:
        return "進入休眠期，靜待來年綻放"

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
        "image": None,
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

茉莉花在中國文化中地位崇高，常被用於花茶製作。茉莉花茶是中國十大名茶之一，以其獨特的香氣深受喜愛。此外，茉莉花也是菲律賓、印尼等國的國花。""",
        "flower_language": "純潔、忠貞、尊敬",
        "symbolism": "茉莉花象徵著純潔的愛情和忠貞不渝的感情。在東南亞文化中，茉莉花代表著母愛和尊敬。其潔白的花朵和清新的香氣也象徵著優雅與高貴。",
        "tags": ["芳香植物", "觀賞植物", "茶用植物", "精油原料"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照至半日照",
            "water": "保持土壤濕潤，避免過濕",
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
        "brief": "鬱金香是百合科鬱金香屬的多年生球根植物，以其優雅的杯狀花朵和豐富的色彩聞名，是荷蘭的國花。",
        "description": """鬱金香原產於中亞和土耳其地區，16世紀傳入歐洲後引發了著名的「鬱金香狂熱」。植株高度約20-50公分，由地下鱗莖生長而出。

葉片基生，呈帶狀或披針形，藍綠色且表面有蠟質。花莖直立，頂端著生單朵花，花朵呈杯狀或碗狀，花瓣6枚，顏色極為豐富，包括紅、黃、白、紫、粉等及其漸變色。

鬱金香品種超過8000個，按花期分為早花、中花、晚花品種。在荷蘭，每年春季都會舉辦盛大的鬱金香花展，吸引世界各地的遊客。""",
        "flower_language": "愛的表白、榮譽、祝福",
        "symbolism": "鬱金香象徵著高雅、富貴和永恆的愛。不同顏色代表不同含義：紅色象徵愛的宣言，黃色代表開朗，白色表示純潔，紫色象徵高貴。在土耳其文化中，鬱金香代表著天堂和神聖。",
        "tags": ["觀賞植物", "球根花卉", "春季花卉", "切花"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照至半日照",
            "water": "生長期保持濕潤，休眠期減少澆水",
            "temperature": "15-20°C（需低溫春化）",
            "humidity": "中等濕度",
            "soil": "排水良好的沙質壤土",
            "fertilizer": "種植時施基肥，生長期追肥",
            "pruning": "花後剪除花莖，保留葉片"
        }
    },
    
    7: {
        "name": "蓮花",
        "scientific_name": "Nelumbo nucifera",
        "family": "蓮科",
        "genus": "蓮屬",
        "origin": "亞洲、澳洲北部",
        "image": None,
        "brief": "蓮花是蓮科蓮屬的多年生水生植物，因其「出淤泥而不染」的特性，在東方文化中具有深刻的象徵意義。",
        "description": """蓮花是古老的水生植物，化石記錄可追溯到1億年前。植株由地下根莖（藕）生長，葉片圓形盾狀，直徑可達60公分，表面有蠟質，具疏水性。

花朵碩大美麗，直徑10-25公分，花瓣多層，顏色有白、粉、紅等。花朵在清晨開放，傍晚閉合，具有獨特的「恆溫」現象，能保持花溫在30-35°C。

蓮花全身是寶：蓮子可食用，蓮藕是常見蔬菜，蓮葉可入藥，花朵可觀賞。在佛教文化中，蓮花象徵著覺悟和清淨，是最神聖的植物之一。""",
        "flower_language": "清廉、純潔、堅貞",
        "symbolism": "蓮花象徵著清白、高潔，因其生長在污泥中卻保持潔淨而被視為君子的象徵。在佛教中代表覺悟和超脫，在中國文化中象徵品格高尚。蓮花「花果同時」的特性也代表因果相應。",
        "tags": ["水生植物", "觀賞植物", "食用植物", "藥用植物"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照（每天至少6小時）",
            "water": "需在水中栽培，水深10-20公分",
            "temperature": "20-30°C",
            "humidity": "高濕度（水生環境）",
            "soil": "富含有機質的塘泥",
            "fertilizer": "生長期定期施水生植物專用肥",
            "pruning": "及時清除枯葉殘花"
        }
    },

    # ===== 新增植物 (8-20) =====

    8: {
        "name": "蘭花",
        "scientific_name": "Phalaenopsis amabilis",
        "family": "蘭科",
        "genus": "蝴蝶蘭屬",
        "origin": "熱帶亞洲",
        "image": None,
        "brief": "蘭花是蘭科蝴蝶蘭屬的多年生草本，以其優雅的花姿和長花期聞名，被譽為「花中之后」。",
        "description": """蘭花原產於熱帶亞洲地區，是台灣重要的出口花卉。植株為附生蘭，根系粗壯發達，可攀附於樹幹或岩石上。

葉片呈肉質肥厚，橢圓形或披針形，翠綠色。花莖從葉腋抽出，著生數朵至數十朵花，花朵形似蝴蝶因而得名。

蘭花色彩豐富，有白、粉、紫、黃等顏色，花期可達2-3個月。其高雅脫俗的姿態，使其成為重要的高級盆花。""",
        "flower_language": "高雅、純潔、珍貴",
        "symbolism": "蘭花象徵著高貴、典雅和堅貞。在中國文化中，蘭花與梅、竹、菊並稱「四君子」，代表高尚的品格。蘭花也象徵著富貴和幸福。",
        "tags": ["觀賞植物", "高檔盆花", "切花", "蘭科花卉"],
        "seasons": ["春季", "冬季"],
        "care": {
            "difficulty": "困難",
            "sunlight": "散射光（避免直射）",
            "water": "每週澆水一次，保持根系濕潤",
            "temperature": "20-30°C",
            "humidity": "高濕度（60-80%）",
            "soil": "水苔或樹皮栽培介質",
            "fertilizer": "蘭花專用肥，每週一次稀釋",
            "pruning": "花後剪除花莖"
        }
    },

    9: {
        "name": "杜鵑花",
        "scientific_name": "Rhododendron simsii",
        "family": "杜鵑花科",
        "genus": "杜鵑花屬",
        "origin": "中國南部",
        "image": None,
        "brief": "杜鵑花是杜鵑花科杜鵑花屬的灌木，以其繁茂的花朵和豐富的色彩聞名，是世界著名的觀賞花卉。",
        "description": """杜鵑花原產於中國南部及雲貴高原地區，是落葉或常綠灌木。株高可達1-3公尺，分枝茂密。

葉片互生，橢圓形或卵形，質感粗糙。花2-6朵簇生於枝頂，花冠呈漏斗形，顏色有紅、粉、白、紫等，部分品种有斑点或条纹。

杜鵑花的花期在春季，滿山遍野的杜鵑花海景觀極為壯觀。其適應性強，耐寒耐熱，在園藝中應用廣泛。""",
        "flower_language": "愛的欣喜、節制",
        "symbolism": "杜鵑花象徵著節制和真誠的愛。在西方，它代表著衝動的情感。在中國，杜鵑花也叫映山紅，象徵著故鄉的思念。",
        "tags": ["觀賞植物", "庭園花卉", "行道樹", "春季花卉"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "半日照（避免強光直射）",
            "water": "保持土壤濕潤但勿積水",
            "temperature": "15-25°C",
            "humidity": "中等濕度",
            "soil": "排水良好的酸性土壤",
            "fertilizer": "春季每2週施肥",
            "pruning": "花後輕修剪"
        }
    },

    10: {
        "name": "茶花",
        "scientific_name": "Camellia japonica",
        "family": "山茶科",
        "genus": "山茶屬",
        "origin": "東亞",
        "image": None,
        "brief": "茶花是山茶科山茶屬的常綠灌木或小喬木，以其雍容華貴的花朵聞名，被譽為「花中嬌客」。",
        "description": """茶花原產於中國、日本、韓國等東亞地區，是常綠灌木或小喬木，高可達10公尺。樹皮灰褐色，葉片革質，橢圓形或卵形。

花單生或數朵簇生於枝頂，直徑5-12公分，花色豐富，有紅、粉、白、黃等，還有複色品種。花期從11月到翌年4月，跨越冬季。

茶花在中國文化中象徵高潔的品格，其花型碩大美麗，與牡丹、荷花並稱「三大名花」。""",
        "flower_language": "理想之愛、謙讓",
        "symbolism": "茶花象徵著理想中的愛和完美的魅力。在西方，茶花代表著仰慕和尊重。在中國文化中，茶花代表著高潔和堅貞。",
        "tags": ["觀賞植物", "庭園花卉", "高檔盆花", "冬季花卉"],
        "seasons": ["冬季", "春季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "半日照至全日照",
            "water": "保持土壤濕潤",
            "temperature": "15-25°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的微酸性土壤",
            "fertilizer": "春季施肥促進生長",
            "pruning": "花後輕修剪"
        }
    },

    11: {
        "name": "菊花",
        "scientific_name": "Chrysanthemum morifolium",
        "family": "菊科",
        "genus": "菊屬",
        "origin": "中國",
        "image": None,
        "brief": "菊花是菊科菊屬的多年生草本植物，是中國的傳統名花，被譽為「花中四君子」之一。",
        "description": """菊花原產於中國，是多年生草本植物，株高30-90公分。莖直立，分枝或不分枝，葉片互生，卵形或橢圓形，邊緣有鋸齒。

頭狀花序單生或數朵聚生於枝頂，直徑2-10公分。舌狀花和管狀花組成，花色有白、黃、粉、紅、紫等，品種超過數千個。

菊花在中國文化中象徵著高潔的品格，農曆九月九日重陽節有賞菊的傳統。其花可入藥、制茶。""",
        "flower_language": "高潔、長壽、堅貞",
        "symbolism": "菊花象徵著高潔的品格和長壽。在中國文化中，菊花代表著「採菊東籬下」的隱逸之美。菊花也象徵著對故人的思念。",
        "tags": ["觀賞植物", "藥用植物", "食用植物", "秋季花卉"],
        "seasons": ["秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤，避免過濕",
            "temperature": "15-28°C",
            "humidity": "中等濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "生長期每2週施肥",
            "prune": "定期摘心促進分枝"
        }
    },

    12: {
        "name": "蘭花",
        "scientific_name": "Dendrobium nobile",
        "family": "蘭科",
        "genus": "石斛蘭屬",
        "origin": "東南亞",
        "image": None,
        "brief": "石斛蘭是蘭科石斛蘭屬的多年生草本，以其優雅的花朵和芳香聞名，是常見的觀賞蘭花。",
        "description": """石斛蘭原產於東南亞地區，是附生性蘭花。莖直立或下垂，圓柱形，節間膨大，呈肉質。

葉片互生，披針形或橢圓形，革質。花序從莖節抽出，著生1-4朵花，花徑約3-5公分，花色有白、粉、紫等，部分有斑紋。

石斛蘭的花期在春季，花朵美麗且有芳香。其莖部可用於中藥，具滋陰清熱的功效。是重要的切花和盆花材料。""",
        "flower_language": "歡迎、祝福、堅強",
        "symbolism": "石斛蘭象徵著歡迎和祝福，代表著堅強的生命力。在泰國，石斛蘭是重要的敬佛花卉。",
        "tags": ["觀賞植物", "蘭科花卉", "切花", "藥用植物"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "散射光",
            "water": "保持濕潤但勿積水",
            "temperature": "18-28°C",
            "humidity": "高濕度（70-80%）",
            "soil": "樹皮、椰糠介質",
            "fertilizer": "生長期每週施肥",
            "pruning": "花後修剪"
        }
    },

    13: {
        "name": "紫藤",
        "scientific_name": "Wisteria sinensis",
        "family": "豆科",
        "genus": "紫藤屬",
        "origin": "中國",
        "image": None,
        "brief": "紫藤是豆科紫藤屬的落葉攀援灌木，以其長而下垂的紫色花序聞名，是著名的棚架花卉。",
        "description": """紫藤原產於中國，是落葉大型攀援灌木，藤蔓可長達20公尺。莖左旋纏繞，樹皮灰褐色。

奇數羽狀複葉，互生。總狀花序下垂，長可達30-50公分，著生數十至上百朵小花，花冠蝶形，紫色或淡紫色。

紫藤的花期在春季，滿藤紫花如瀑布般傾瀉，蔚為壯觀。其花可食用，製作紫藤花餅等特色食品。""",
        "flower_language": "沈醉、迷戀、優美",
        "symbolism": "紫藤象徵著沈醉的愛和優美的氣質。在日本，紫藤象徵著永恆的愛和深深的思念。紫藤花瀑是著名的春日景觀。",
        "tags": ["觀賞植物", "棚架植物", "攀援植物", "春季花卉"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照至半日照",
            "water": "保持土壤濕潤",
            "temperature": "15-25°C",
            "humidity": "中等濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "花後施肥促進生長",
            "pruning": "夏季修剪過長枝條"
        }
    },

    14: {
        "name": "梔子花",
        "scientific_name": "Gardenia jasminoides",
        "family": "茜草科",
        "genus": "梔子屬",
        "origin": "中國南部",
        "image": None,
        "brief": "梔子是茜草科梔子屬的常綠灌木，以其潔白的花朵和濃郁的香氣聞名，是重要的香花植物。",
        "description": """梔子花原產於中國南部，是常綠灌木，高可達2公尺。葉片對生，橢圓形或卵形，深綠色有光澤。

花單生於枝頂或葉腋，花冠高腳碟狀，直徑5-8公分，花瓣5-8枚，潔白如雪。花期在夏季，花香濃郁，可持續數天。

梔子花不僅觀賞價值高，其花可提取香料製作香水和化妝品。果實可作染料，也可入藥，具有清熱瀉火的功效。""",
        "flower_language": "純潔、永恆的愛、一生的守候",
        "symbolism": "梔子花象徵著純潔的愛和永恆的承諾。在中國文化中，梔子花代表著堅貞的愛情和一生的守候。",
        "tags": ["芳香植物", "觀賞植物", "藥用植物", "庭園花卉"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "半日照，避免強光直射",
            "water": "保持土壤濕潤",
            "temperature": "18-28°C",
            "humidity": "高濕度",
            "soil": "酸性土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "花後輕修剪"
        }
    },

    15: {
        "name": "繡球花",
        "scientific_name": "Hydrangea macrophylla",
        "family": "虎耳草科",
        "genus": "繡球屬",
        "origin": "日本、中國",
        "image": None,
        "brief": "繡球花是虎耳草科繡球屬的落葉灌木，以其碩大的球形花序聞名，是重要的庭園花卉。",
        "description": """繡球花原產於日本及中國，是落葉灌木，高1-2公尺。葉片對生，橢圓形或倒卵形，邊緣有粗鋸齒。

花序為聚傘花序，呈球形或半球形，直徑10-30公分。花色豐富，有藍、紫、粉、紅、白等，顏色會隨土壤酸鹼度變化。

繡球花的花期在夏季，一朵朵小花聚集如繡球般，因而得名。其花序大而美麗，是重要的切花和盆花材料。""",
        "flower_language": "希望、團聚、美滿",
        "symbolism": "繡球花象徵著希望、團聚和美滿的家庭。在西方，繡球花代表著感恩和謝意。",
        "tags": ["觀賞植物", "切花", "庭園花卉", "夏季花卉"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "半日照，避免直射",
            "water": "保持土壤濕潤",
            "temperature": "18-25°C",
            "humidity": "高濕度",
            "soil": "排水良好的微酸性土壤",
            "fertilizer": "春季每2週施肥",
            "pruning": "花後修剪"
        }
    },

    16: {
        "name": "九重葛",
        "scientific_name": "Bougainvillea spectabilis",
        "family": "紫茉莉科",
        "genus": "九重葛屬",
        "origin": "南美洲",
        "image": None,
        "brief": "九重葛是紫茉莉科九重葛屬的攀援灌木，以其豔麗的苞片聞名，是熱帶地區重要的觀賞植物。",
        "description": """九重葛原產於南美洲，是落葉或常綠攀援灌木，藤蔓可長達10公尺以上。莖上有刺，葉片互生，卵形。

花序由3朵小花組成，外圍有3枚色彩鮮豔的苞片，苞片有紅、紫、粉、橙、白等顏色，非常醒目。真正的花很小，呈管狀。

九重葛的花期長，在熱帶地區幾乎全年开花。其花量豐富，花色艷麗，是重要的棚架、圍牆美化植物。""",
        "flower_language": "熱情、活力、堅強",
        "symbolism": "九重葛象徵著熱情和活力，代表著堅強的生命力。在西方，九重葛代表著魅力和吸引力。",
        "tags": ["觀賞植物", "攀援植物", "棚架植物", "熱帶花卉"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "耐旱，澆水宜乾濕交替",
            "temperature": "20-35°C",
            "humidity": "中等濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "生長期每月施肥",
            "pruning": "定期修剪保持形態"
        }
    },

    17: {
        "name": "滿天星",
        "scientific_name": "Gypsophila paniculata",
        "family": "石竹科",
        "genus": "石頭花屬",
        "origin": "歐亞大陸",
        "image": None,
        "brief": "滿天星是石竹科石頭花屬的多年生草本，以其繁星般的小花聞名，是重要的配花材料。",
        "description": """滿天星原產於歐亞大陸，是多年生草本植物，高可達1公尺。莖直立，多分枝，葉片對生，披針形。

花序為圓錐狀聚傘花序，著生數百朵小白花，花徑僅約0.5公分，如滿天星斗，因而得名。

滿天星常作為配花使用，襯托主花使其更加美觀。其花乾燥後也可作為乾燥花使用。花期在夏季。""",
        "flower_language": "純潔、真心、思念",
        "symbolism": "滿天星象徵著純潔的心和真摯的思念。在花藝中，滿天星代表著配角的精神，甘居幕後襯托他人。",
        "tags": ["觀賞植物", "切花", "配花", "乾燥花"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤但勿積水",
            "temperature": "15-25°C",
            "humidity": "中等濕度",
            "soil": "排水良好的石灰質土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "定期摘心促進分枝"
        }
    },

    18: {
        "name": "聖誕紅",
        "scientific_name": "Euphorbia pulcherrima",
        "family": "大戟科",
        "genus": "大戟屬",
        "origin": "墨西哥",
        "image": None,
        "brief": "聖誕紅是大戟科大戟屬的落葉灌木，以其紅色的苞片聞名，是聖誕節重要的裝飾花卉。",
        "description": """聖誕紅原產於墨西哥，是落葉灌木，高可達3公尺。葉片互生，卵形或橢圓形，邊緣有鋸齒。

頂端的苞片呈鮮紅、粉紅、白等顏色，其中紅色最常見，常被誤認為花瓣。真正的花很小，黃綠色，著生於苞片基部。

聖誕紅因其聖誕節期間盛開的特性而成為節日象徵。其苞片色彩鮮豔，觀賞期長達數月。""",
        "flower_language": "熱情、祝福、聖誕歡樂",
        "symbolism": "聖誕紅象徵著聖誕節的歡樂和祝福。在西方，聖誕紅是聖誕節不可或缺的節日花卉。",
        "tags": ["觀賞植物", "節慶花卉", "冬季花卉", "盆栽"],
        "seasons": ["冬季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "半日照，避免強光直射",
            "water": "保持土壤微濕",
            "temperature": "15-25°C",
            "humidity": "中等濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "春季修剪"
        }
    },

    19: {
        "name": "海芋",
        "scientific_name": "Zantedeschia aethiopica",
        "family": "天南星科",
        "genus": "馬蹄蓮屬",
        "origin": "南非",
        "image": None,
        "brief": "海芋是天南星科馬蹄蓮屬的多年生草本，以其優雅的佛焰苞聞名，是重要的切花和盆花。",
        "description": """海芋原產於南非，是多年生草本植物，株高可達1公尺。葉片基生，箭形或心形，葉柄長達60公分。

花序為肉穗花序，外圍有一枚巨大的佛焰苞，形似馬蹄因而得名。佛焰苞白色或粉色，優雅高貴，真正的花很小，黃色，位於肉穗花序上。

海芋的花期在春季，是重要的切花材料，也適合作為盆花。其花姿優雅，被視為高貴的象徵。""",
        "flower_language": "純潔、優雅、高貴",
        "symbolism": "海芋象徵著純潔、優雅和高貴。在西方，海芋代表著美麗的容顏和崇高的精神。",
        "tags": ["觀賞植物", "切花", "高檔盆花", "春季花卉"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "半日照，避免直射",
            "water": "保持土壤濕潤",
            "temperature": "15-25°C",
            "humidity": "高濕度",
            "soil": "富含有機質的肥沃土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "花後剪除花莖"
        }
    },

    20: {
        "name": "鳶尾花",
        "scientific_name": "Iris tectorum",
        "family": "鱗茎科",
        "genus": "鳶尾屬",
        "origin": "中國、日本",
        "image": None,
        "brief": "鳶尾花是鱗茎科鳶尾屬的多年生草本，以其優雅的花朵和藍紫色花瓣聞名，被譽為「藍色精靈」。",
        "description": """鳶尾花原產於中國及日本，是多年生草本植物，株高30-60公分。葉片基生，劍形或帶狀，質地堅韌。

花單生或數朵聚生於莖頂，花被片6枚，外3枚較大下垂，內3枚較小直立，花色以藍紫為主，也有白、黃、粉等色。

鳶尾花的花期在春季，花朵優雅飄逸，似蝴蝶展翅，因而有「蝴蝶花」之稱。其花可用於切花和園林美化。""",
        "flower_language": "優雅、使命、信念",
        "symbolism": "鳶尾花象徵著優雅、使命和信念。在法國，鳶尾花是國花，代表著自由和尊嚴。",
        "tags": ["觀賞植物", "庭園花卉", "切花", "春季花卉"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照至半日照",
            "water": "保持土壤濕潤",
            "temperature": "15-25°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "春季施肥",
            "pruning": "花後剪除花莖"
        }
    },

    # ===== 新增植物 (21-50) =====

    21: {
        "name": "薄荷",
        "scientific_name": "Mentha haplocalyx",
        "family": "唇形科",
        "genus": "薄荷屬",
        "origin": "地中海沿岸",
        "image": None,
        "brief": "薄荷是唇形科薄荷屬的多年生草本，以其清涼的香氣廣泛種植於廚房花園。",
        "description": """薄荷原產於地中海沿岸，是多年生草本植物，株高30-80公分。莖四稜形，直立或斜生，葉片對生，卵形或橢圓形，邊緣有鋸齒。

葉片含有豐富的薄荷醇，揉搓後散發清涼芳香。花朵細小，呈淡紫色或白色，簇生於葉腋或莖頂。

薄荷廣泛應用於食品、飲料、藥品和化妝品。其清涼的特性使其成為重要的香料植物。""",
        "flower_language": "純潔、善良、溫暖",
        "symbolism": "薄荷象徵著純潔的心靈和溫暖的友誼。在古希臘，薄荷象徵著熱情和活力。",
        "tags": ["芳香植物", "藥用植物", "食用植物", "廚房香草"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "半日照至全日照",
            "water": "保持土壤濕潤",
            "temperature": "15-25°C",
            "humidity": "中等至高濕度",
            "soil": "肥沃排水良好的土壤",
            "fertilizer": "生長期每月施肥",
            "pruning": "定期收割促進新葉生長"
        }
    },

    22: {
        "name": "迷迭香",
        "scientific_name": "Rosmarinus officinalis",
        "family": "唇形科",
        "genus": "迷迭香屬",
        "origin": "地中海沿岸",
        "image": None,
        "brief": "迷迭香是唇形科迷迭香屬的常綠灌木，以其芳香的針葉和藍色小花聞名。",
        "description": """迷迭香原產於地中海沿岸，是常綠直立或匍匐灌木，高可達2公尺。莖木質，葉片對生，線形或披針形，革質，深綠色。

花朵小，藍色或淡藍色，唇形，簇生於葉腋。花期在春季或秋季。迷迭香具有強烈的芳香，是重要的香料和藥用植物。

在烹飪中，迷迭香常用於調味肉類和義大利菜。在芳香療法中，迷迭香被認為能提升記憶力和專注力的功效。""",
        "flower_language": "回憶、忠誠、友誼",
        "symbolism": "迷迭香象徵著回憶和忠誠。在歐洲，迷迭香代表著永恆的記憶和愛情的忠貞。",
        "tags": ["芳香植物", "藥用植物", "食用植物", "香草植物"],
        "seasons": ["春季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "耐旱，澆水宜乾濕交替",
            "temperature": "15-25°C",
            "humidity": "低至中等濕度",
            "soil": "排水良好的砂質土壤",
            "fertilizer": "少量施肥，春秋季",
            "pruning": "花後輕修剪維持形態"
        }
    },

    23: {
        "name": "百里香",
        "scientific_name": "Thymus mongolicus",
        "family": "唇形科",
        "genus": "百里香屬",
        "origin": "地中海沿岸",
        "image": None,
        "brief": "百里香是唇形科百里香屬的小型常綠灌木，以其濃郁的芳香聞名於烹飪界。",
        "description": """百里香原產於地中海沿岸，是多年生常綠小灌木，高20-40公分。莖木質，匍匐或直立，葉片細小，卵形或橢圓形。

花朵小，淡紫色或粉紅色，簇生於枝頂，花期在夏季。百里香具有強烈的芳香，是歐洲烹飪中重要的香草。

百里香可用於調味肉類、湯品和醬汁。其精油在香水和藥品中也有廣泛應用。""",
        "flower_language": "勇氣、活力、堅強",
        "symbolism": "百里香象徵著勇氣和活力。在古羅馬，百里香象徵著勇敢和戰鬥精神。",
        "tags": ["芳香植物", "藥用植物", "食用植物", "香草植物"],
        "seasons": ["春季", "夏季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "耐旱，保持土壤微濕",
            "temperature": "15-25°C",
            "humidity": "低濕度",
            "soil": "排水良好的石灰質土壤",
            "fertilizer": "少量施肥",
            "pruning": "定期修剪促進分枝"
        }
    },

    24: {
        "name": "羅勒",
        "scientific_name": "Ocimum basilicum",
        "family": "唇形科",
        "genus": "羅勒屬",
        "origin": "印度、東南亞",
        "image": None,
        "brief": "羅勒是唇形科羅勒屬的芳香草本，是義大利和泰國料理的重要香料。",
        "description": """羅勒原產於印度和東南亞，是一年生草本植物，株高30-90公分。莖直立，多分枝，葉片對生，卵形或橢圓形，綠色或紫色。

花朵小，白色或淡紫色，總狀花序著生於莖頂。羅勒有多個品種，包括甜羅勒、泰国羅勒和紫羅勒等。

羅勒是義大利青醬（pesto）和泰國料理的靈魂調料。其葉片可用於新鮮或乾燥後調味。""",
        "flower_language": "神聖、祝福、美好",
        "symbolism": "羅勒在印度文化中象徵著神聖和祝福。在西方，羅勒代表著激情和好客。",
        "tags": ["芳香植物", "食用植物", "香草植物", "料理香料"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤",
            "temperature": "20-30°C",
            "humidity": "中等濕度",
            "soil": "肥沃排水良好的土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "定期摘心促進分枝"
        }
    },

    25: {
        "name": "檸檬香茅",
        "scientific_name": "Cymbopogon citratus",
        "family": "禾本科",
        "genus": "香茅屬",
        "origin": "南亞、東南亞",
        "image": None,
        "brief": "檸檬香茅是禾本科香茅屬的多年生草本，以其檸檬清香聞名，是亞洲料理常用香料。",
        "description": """檸檬香茅原產於南亞和東南亞，是多年生草本植物，株高可達1.5公尺。莖粗壯，叢生，葉片狹長，線形，灰綠色。

葉片含有檸檬醛，散發濃郁的檸檬香氣。花序為總狀花序，著生於莖頂。

檸檬香茅廣泛用於泰國、越南等東南亞料理，也可用於製作茶飲和精油。其芳香有驅蟲效果。""",
        "flower_language": "清新、活力、純淨",
        "symbolism": "檸檬香茅象徵著清新和活力，代表著純淨的心靈。其芳香能帶來正面的能量。",
        "tags": ["芳香植物", "食用植物", "藥用植物", "香草植物"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤",
            "temperature": "20-30°C",
            "humidity": "中等至高濕度",
            "soil": "肥沃排水良好的土壤",
            "fertilizer": "生長期每月施肥",
            "pruning": "收割葉片即可"
        }
    },

    26: {
        "name": "金盞花",
        "scientific_name": "Calendula officinalis",
        "family": "菊科",
        "genus": "金盞花屬",
        "origin": "地中海沿岸",
        "image": None,
        "brief": "金盞花是菊科金盞花屬的一年生草本，以其明亮的橙黃色花朵聞名。",
        "description": """金盞花原產於地中海沿岸，是一年生草本植物，株高30-50公分。莖直立，分枝多，葉片互生，披針形或長橢圓形。

頭狀花序單生於枝頂，直徑4-7公分，花色為鮮亮的橙黃色或金黃色。花期從春季到秋季。

金盞花在園藝中常見於花壇和邊緣植物。其花瓣可入藥和製作染料，也可用於沙拉装飾。""",
        "flower_language": "光明、溫暖、希望",
        "symbolism": "金盞花象徵著光明和希望，代表著太陽的力量和溫暖。其明亮的色彩能帶來愉快的心情。",
        "tags": ["觀賞植物", "藥用植物", "食用植物", "染料植物"],
        "seasons": ["春季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤但勿過濕",
            "temperature": "15-25°C",
            "humidity": "中等濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "生長期每月施肥",
            "pruning": "摘除凋謝花朵延長花期"
        }
    },

    27: {
        "name": "金蓮花",
        "scientific_name": "Tropaeolum majus",
        "family": "金蓮花科",
        "genus": "金蓮花屬",
        "origin": "南美洲",
        "image": None,
        "brief": "金蓮花是金蓮花科金蓮花屬的一年或多年生草本，以其絢麗的花朵和可食用的特性聞名。",
        "description": """金蓮花原產於南美洲，是一年或多年生草本，株高20-40公分。莖肉質，多汁，蔓生或直立，葉片互生，圓形或盾形。

花大，單生於葉腋，花色有橙、黃、紅等，花期在夏季至秋季。其葉片和花朵都可食用，味道略帶辛辣。

金蓮花在園藝中適合吊籃或地被種植。其辛辣味道類似水芹，常用於沙拉和料理装飾。""",
        "flower_language": "戰鬥、激情、創造力",
        "symbolism": "金蓮花象徵著戰鬥精神和激情。其明亮的花朵代表著創造力和積極的人生態度。",
        "tags": ["觀賞植物", "可食用", "吊籃植物", "地被植物"],
        "seasons": ["夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照至半日照",
            "water": "保持土壤適度濕潤",
            "temperature": "15-25°C",
            "humidity": "中等濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "少量施肥",
            "pruning": "定期摘心促進分枝"
        }
    },

    28: {
        "name": "山蘇花",
        "scientific_name": "Asplenium nidus",
        "family": "鐵角蕨科",
        "genus": "鐵角蕨屬",
        "origin": "熱帶亞洲",
        "image": None,
        "brief": "山蘇花是鐵角蕨科鐵角蕨屬的觀葉植物，以其放射狀的鳥巢狀葉片聞名。",
        "description": """山蘇花原產於熱帶亞洲，是多年生觀葉植物。葉片叢生，呈放射狀展開，中心形成「鳥巢」狀。

葉片大型，長披針形，亮綠色，葉脈平行。新葉會從中心抽出，成熟後向外展開。

山蘇花是極受歡迎的室內觀葉植物，能適應低光環境。其獨特的葉片造型使其成為優雅的裝飾植物。""",
        "flower_language": "自然、生機、生命力",
        "symbolism": "山蘇花象徵著自然的生機和旺盛的生命力。其「鳥巢」象徵著家和歸屬感。",
        "tags": ["觀葉植物", "室內植物", "陰生植物", "熱帶植物"],
        "seasons": ["四季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "散射光，避免直射",
            "water": "保持土壤濕潤",
            "temperature": "18-28°C",
            "humidity": "高濕度",
            "soil": "富含有機質的土壤",
            "fertilizer": "生長期每2個月施肥",
            "pruning": "去除枯葉即可"
        }
    },

    29: {
        "name": "腎蕨",
        "scientific_name": "Nephrolepis exaltata",
        "family": "腎蕨科",
        "genus": "腎蕨屬",
        "origin": "熱帶地區",
        "image": None,
        "brief": "腎蕨是腎蕨科腎蕨屬的觀葉植物，以其優雅的羽狀葉片廣泛用於園藝。",
        "description": """腎蕨原產於熱帶地區，是多年生觀葉植物。葉片大型，羽狀複葉，長可達1公尺，叢生。

羽片對生或互生，翠綠色，形似腎臟因而得名。葉片下垂，姿態優雅。

腎蕨是重要的觀葉植物，適合吊籃種植或作為組合盆栽。其適應性強，容易栽培。""",
        "flower_language": "神秘、含蓄、優雅",
        "symbolism": "腎蕨象徵著神秘和含蓄的美。其優雅的姿態代表著溫柔和細膩的情感。",
        "tags": ["觀葉植物", "室內植物", "吊籃植物", "陰生植物"],
        "seasons": ["四季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "散射光或半陰",
            "water": "保持土壤濕潤",
            "temperature": "18-28°C",
            "humidity": "高濕度",
            "soil": "排水良好的腐殖質土壤",
            "fertilizer": "生長期每個月施肥",
            "pruning": "剪除枯黃葉片"
        }
    },

    30: {
        "name": "變葉木",
        "scientific_name": "Codiaeum variegatum",
        "family": "大戟科",
        "genus": "變葉木屬",
        "origin": "馬來西亞、西印度群島",
        "image": None,
        "brief": "變葉木是大戟科變葉木屬的常綠灌木，以其色彩繽紛的葉片聞名。",
        "description": """變葉木原產於馬來西亞和西印度群島，是常綠灌木，高可達2公尺。葉片互生，形狀多樣，有橢圓形、披針形、3裂等。

葉片色彩極為豐富，有綠、黃、橙、紅、紫等多種顏色和斑紋，是觀葉植物中的明星。

變葉木適合庭園種植或大型盆栽，其鮮豔的葉片可為環境增添熱帶風情。""",
        "flower_language": "變化、驚喜、多彩",
        "symbolism": "變葉木象徵著生活的變化和多彩。其繽紛的葉片代表著生命的豐富和驚喜。",
        "tags": ["觀葉植物", "庭園植物", "熱帶植物", "灌木"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照至半日照",
            "water": "保持土壤濕潤",
            "temperature": "20-30°C",
            "humidity": "高濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "春季修剪整形"
        }
    },

    31: {
        "name": "合歡",
        "scientific_name": "Albizia julibrissin",
        "family": "豆科",
        "genus": "合歡屬",
        "origin": "亞洲",
        "image": None,
        "brief": "合歡是豆科合歡屬的落葉喬木，以其扇形的粉紅色花絲聞名。",
        "description": """合歡原產於亞洲，是落葉小喬木，高可達10公尺。樹冠開展，樹皮灰褐色，葉片為二回羽狀複葉。

花序為頭狀花序，數十朵小花聚集，花絲細長呈扇形，粉紅色或淡紫色，非常美觀。花期在夏季。

合歡因其優美的花形和芳香而被種植於庭園和行道樹。其樹皮可入藥，有安神功效。""",
        "flower_language": "團結、和睦、幸福",
        "symbolism": "合歡象徵著團結和睦，其葉片夜間會闭合，代表著夫妻恩愛和家庭的和諧。",
        "tags": ["觀賞植物", "行道樹", "庭園樹", "藥用植物"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤",
            "temperature": "15-25°C",
            "humidity": "中等濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "春季施肥",
            "pruning": "冬季落葉後修剪"
        }
    },

    32: {
        "name": "紫薇",
        "scientific_name": "Lagerstroemia indica",
        "family": "千屈菜科",
        "genus": "紫薇屬",
        "origin": "中國、印度",
        "image": None,
        "brief": "紫薇是千屈菜科紫薇屬的落葉灌木或小喬木，以其夏季盛開的紫紅色花朵聞名。",
        "description": """紫薇原產於中國和印度，是落葉灌木或小喬木，高可達5公尺。樹皮光滑，灰白色，枝條扭曲。

葉片對生或互生，橢圓形或卵形。圓錐花序頂生，花色有紫紅、粉紅、白色等，花期在夏季。

紫薇因其夏季盛開的花朵而被種植於庭園。其樹姿優美，花色艷麗，是重要的觀賞樹種。""",
        "flower_language": "好運、沉迷、堅強",
        "symbolism": "紫薇象徵著好運和堅強的生命力。其花期長，代表著持久的熱情和美麗。",
        "tags": ["觀賞植物", "庭園樹", "夏季花卉", "落葉樹"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤",
            "temperature": "15-28°C",
            "humidity": "中等濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "春季施肥",
            "pruning": "冬季修剪"
        }
    },

    33: {
        "name": "扶桑",
        "scientific_name": "Hibiscus rosa-sinensis",
        "family": "錦葵科",
        "genus": "木槿屬",
        "origin": "中國",
        "image": None,
        "brief": "扶桑是錦葵科木槿屬的常綠灌木，以其碩大鮮豔的花朵聞名，是熱帶常見花卉。",
        "description": """扶桑原產於中國，是常綠灌木，高可達3公尺。葉片互生，卵形或橢圓形，邊緣有鋸齒。

花大，單生於葉腋，直徑10-15公分，花色有紅、橙、粉、黃、白等，還有複色品種。花期幾乎全年。

扶桑是熱帶和亞熱帶地區重要的觀賞植物，其花朵大而美麗，常用於庭園布置和綠籬。""",
        "flower_language": "熱情、魅力、青春",
        "symbolism": "扶桑象徵著熱情和魅力。在夏威夷，扶桑花代表著女性的美麗和青春。",
        "tags": ["觀賞植物", "庭園植物", "綠籬植物", "熱帶花卉"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤",
            "temperature": "18-30°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "花後修剪"
        }
    },

    34: {
        "name": "木棉",
        "scientific_name": "Bombax ceiba",
        "family": "木棉科",
        "genus": "木棉屬",
        "origin": "熱帶亞洲",
        "image": None,
        "brief": "木棉是木棉科木棉屬的落葉大喬木，以其春季先花後葉的壯觀景象聞名。",
        "description": """木棉原產於熱帶亞洲，是落葉大喬木，高可達25公尺。樹幹粗壯通直，樹皮灰褐色，幼樹有刺。

花朵大，橙紅色或紅色，直徑10-15公分，先於葉片開放，滿樹火紅，非常壯觀。花期在春季。

木棉因其先花後葉的獨特特性被稱為「英雄樹」。其棉絮可用於枕頭和填充材料。""",
        "flower_language": "英雄、熱情、珍惜",
        "symbolism": "木棉象徵著英雄精神和熱情的生命態度。其花語是「珍惜眼前的幸福」。",
        "tags": ["觀賞植物", "行道樹", "庭園樹", "落葉樹"],
        "seasons": ["春季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "耐旱，澆水適度",
            "temperature": "20-30°C",
            "humidity": "中等濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "春季施肥",
            "pruning": "不需要"
        }
    },

    35: {
        "name": "芒果",
        "scientific_name": "Mangifera indica",
        "family": "漆樹科",
        "genus": "芒果屬",
        "origin": "南亞",
        "image": None,
        "brief": "芒果是漆樹科芒果屬的熱帶常綠大喬木，以其美味的果實聞名世界。",
        "description": """芒果原產於南亞，是熱帶常綠大喬木，高可達30公尺。樹冠開展，葉片互生，披針形或橢圓形，革質。

花小，淡黃綠色，圓錐花序。果實為核果，橢圓形或腎形，果肉黃色或橙色，甜美多汁。

芒果是世界上最受欢迎的热带水果之一，有数百个品种。果实可鲜食或加工成果汁、罐头等。""",
        "flower_language": "豐收、甜蜜、願望",
        "symbolism": "芒果象徵著豐收和甜蜜的生活。在印度文化中，芒果葉用於婚禮裝飾。",
        "tags": ["果樹", "熱帶植物", "觀賞樹", "經濟作物"],
        "seasons": ["春季", "夏季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照",
            "water": "保持土壤濕潤，果期減少",
            "temperature": "20-35°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "果後和花前施肥",
            "pruning": "採果後修剪"
        }
    },

    36: {
        "name": "荔枝",
        "scientific_name": "Litchi chinensis",
        "family": "無患子科",
        "genus": "荔枝屬",
        "origin": "中國南方",
        "image": None,
        "brief": "荔枝是無患子科荔枝屬的常綠喬木，以其晶瑩剔透的果肉和獨特風味聞名。",
        "description": """荔枝原產於中國南方，是常綠喬木，高可達15公尺。樹冠圓形，葉片為偶數羽狀複葉，小葉橢圓形。

花小，綠白色，圓錐花序。果實為漿果，卵圓形，外殼粗糙呈紅色或暗紅色，果肉白色半透明，多汁甜美。

荔枝是中國特產的水果，被譽為「水果之王」。其果肉玲瓏剔透，味道甜美芳香。""",
        "flower_language": "珍貴、相思、團圓",
        "symbolism": "荔枝諧音「離枝」，象徵著珍惜和相守。其圓滿的果實代表著團圓和美滿。",
        "tags": ["果樹", "觀賞樹", "庭園樹", "經濟作物"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照",
            "water": "保持土壤濕潤",
            "temperature": "20-30°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的酸性土壤",
            "fertilizer": "果後和花前施肥",
            "pruning": "採果後修剪"
        }
    },

    37: {
        "name": "龍眼",
        "scientific_name": "Dimocarpus longan",
        "family": "無患子科",
        "genus": "龍眼屬",
        "origin": "中國南方",
        "image": None,
        "brief": "龍眼是無患子科龍眼屬的常綠喬木，以其甜美可口的果實聞名。",
        "description": """龍眼原產於中國南方，是常綠喬木，高可達20公尺。樹冠開展，葉片為偶數羽狀複葉，小葉橢圓形。

花小，白色，圓錐花序。果實為漿果，球形，外殼黃褐色或灰褐色，果肉白色透明，甜美多汁。

龍眼與荔枝並稱為華南三大名果。其果肉可鮮食或製成龍眼乾、罐頭等。""",
        "flower_language": "珍貴、圓滿、祝福",
        "symbolism": "龍眼諧音「龍眼」，象徵著珍貴和圓滿。其果實象徵著祝福和好運。",
        "tags": ["果樹", "觀賞樹", "庭園樹", "經濟作物"],
        "seasons": ["夏季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照",
            "water": "保持土壤濕潤",
            "temperature": "20-30°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "果後和花前施肥",
            "pruning": "採果後修剪"
        }
    },

    38: {
        "name": "芭樂",
        "scientific_name": "Psidium guajava",
        "family": "桃金孃科",
        "genus": "番石榴屬",
        "origin": "熱帶美洲",
        "image": None,
        "brief": "芭樂是桃金孃科番石榴屬的常綠灌木或小喬木，以其營養豐富的果實聞名。",
        "description": """芭樂原產於熱帶美洲，是常綠灌木或小喬木，高可達10公尺。樹皮灰褐色，葉片對生，橢圓形或卵形。

花白色，單生或數朵簇生於葉腋。果實為漿果，球形或卵形，果肉白色或紅色，脆甜多汁。

芭樂營養價值高，富含維生素C和膳食纖維。果實可鮮食或加工成果汁、果醬等。""",
        "flower_language": "豐收、健康、樸實",
        "symbolism": "芭樂象徵著豐收和健康的 生活。其樸實的果實代表著踏實和實在。",
        "tags": ["果樹", "觀賞樹", "經濟作物", "熱帶植物"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "保持土壤濕潤",
            "temperature": "20-30°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "生長期每2個月施肥",
            "pruning": "定期修剪整形"
        }
    },

    39: {
        "name": "楊桃",
        "scientific_name": "Averrhoa carambola",
        "family": "酢漿草科",
        "genus": "楊桃屬",
        "origin": "熱帶亞洲",
        "image": None,
        "brief": "楊桃是酢漿草科楊桃屬的常綠小喬木，以其星形的橫切面聞名。",
        "description": """楊桃原產於熱帶亞洲，是常綠小喬木，高可達8公尺。樹皮灰褐色，葉片為奇數羽狀複葉，互生。

花小，淡紫色或白色，腋生。果實為漿果，橢圓形，有5條纵向棱，切開呈星形，非常特別。

楊桃果實可鮮食或製作果汁、果醬。其獨特的星形切面使其成為受歡迎的水果。""",
        "flower_language": "純真、思念、期待",
        "symbolism": "楊桃的星形象徵著閃亮的希望和夢想。其甜美的果實代表著對美好事物的期待。",
        "tags": ["果樹", "觀賞樹", "熱帶植物", "經濟作物"],
        "seasons": ["春季", "秋季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照至半日照",
            "water": "保持土壤濕潤",
            "temperature": "20-30°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "生長期每2個月施肥",
            "pruning": "定期修剪"
        }
    },

    40: {
        "name": "火鶴花",
        "scientific_name": "Anthurium andraeanum",
        "family": "天南星科",
        "genus": "花燭屬",
        "origin": "哥倫比亞、厄瓜多爾",
        "image": None,
        "brief": "火鶴花是天南星科花燭屬的多年生草本，以其鮮紅的佛焰苞聞名。",
        "description": """火鶴花原產於哥倫比亞和厄瓜多爾，是多年生草本。葉片基生，心形或卵形，革質，深綠色。

佛焰苞心形，鮮紅色或粉紅色，非常醒目，是主要的觀賞部位。肉穗花序黃色，著於佛焰苞基部。

火鶴花是重要的切花和盆花材料。其佛焰苞色彩鮮豔，花期長達數月。""",
        "flower_language": "熱情、祝福、吉祥",
        "symbolism": "火鶴花象徵著熱情的祝福和吉祥。其鮮紅的佛焰苞代表著濃烈的愛和熱情。",
        "tags": ["觀賞植物", "切花", "高檔盆花", "室內植物"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "散射光，避免直射",
            "water": "保持土壤濕潤",
            "temperature": "20-28°C",
            "humidity": "高濕度",
            "soil": "排水良好的腐殖質土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "去除枯葉"
        }
    },

    41: {
        "name": "長春花",
        "scientific_name": "Catharanthus roseus",
        "family": "夾竹桃科",
        "genus": "長春花屬",
        "origin": "馬達加斯加",
        "image": None,
        "brief": "長春花是夾竹桃科長春花屬的多年生草本，以其全年不斷的開花生態聞名。",
        "description": """長春花原產於馬達加斯加，是多年生草本或亞灌木，高30-60公分。葉片對生，橢圓形或卵形。

花單生於葉腋或頂生，直徑2-4公分，花色有白、粉、紅、紫等，還有複色品種。花期幾乎全年不斷。

長春花適合花壇、吊籃和邊緣種植。其低維護和長花期的特性使其成為受歡迎的園藝植物。""",
        "flower_language": "青春、快樂、堅強",
        "symbolism": "長春花象徵著青春永駐和快樂的心情。其全年開花的特性代表著堅強和持續的生命力。",
        "tags": ["觀賞植物", "花壇植物", "吊籃植物", "地被植物"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照至半日照",
            "water": "保持土壤適度濕潤",
            "temperature": "15-28°C",
            "humidity": "中等濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "定期摘心促進分枝"
        }
    },

    42: {
        "name": "非洲堇",
        "scientific_name": "Saintpaulia ionantha",
        "family": "苦苣苔科",
        "genus": "非洲堇屬",
        "origin": "東非",
        "image": None,
        "brief": "非洲堇是苦苣苔科非洲堇屬的多年生草本，以其四季不斷的小巧花朵聞名。",
        "description": """非洲堇原產於東非，是多年生草本植物。葉片基生，蓮座狀，卵圓形，葉面有細毛，質地柔軟。

花莖從葉腋抽出，著生數朵小花，花色有紫、藍、粉、白等，還有重瓣品種。花期幾乎全年。

非洲堇是重要的室內觀花植物，其小巧玲瓏的植株和豐富的花色使其成為窗台和案頭的常見擺設。""",
        "flower_language": "永恆的愛、忠誠、溫暖",
        "symbolism": "非洲堇象徵著永恆的愛和忠誠。其小巧的花朵代表著細膩而溫暖的情感。",
        "tags": ["觀花植物", "室內植物", "小型盆栽", "陰生植物"],
        "seasons": ["四季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "散射光，避免直射",
            "water": "保持土壤微濕，避免澆到葉片",
            "temperature": "18-24°C",
            "humidity": "中等濕度",
            "soil": "排水良好的輕質土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "去除凋謝花朵"
        }
    },

    43: {
        "name": "沙漠玫瑰",
        "scientific_name": "Adenium obesum",
        "family": "夾竹桃科",
        "genus": "沙漠玫瑰屬",
        "origin": "非洲東部、阿拉伯半島",
        "image": None,
        "brief": "沙漠玫瑰是夾竹桃科沙漠玫瑰屬的多肉植物，以其膨大的莖部和美麗的花朵聞名。",
        "description": """沙漠玫瑰原產於非洲東部和阿拉伯半島，是落葉或常綠多肉灌木。莖部膨大，呈酒瓶狀，高可達2公尺。

葉片倒卵形或線形，叢生於枝頂。花大，漏斗形，花色有紅、粉、白等，花期在春季至秋季。

沙漠玫瑰是受歡迎的多肉觀賞植物，其獨特的莖部造型和美麗的花朵使其成為多肉玩家的最愛。""",
        "flower_language": "堅強、热情、等待",
        "symbolism": "沙漠玫瑰象徵著堅強的生命力，在艱困環境中依然能綻放美麗。其花語是等待和希望。",
        "tags": ["多肉植物", "觀賞植物", "盆景植物", "熱帶植物"],
        "seasons": ["春季", "夏季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "耐旱，澆水宜乾透澆透",
            "temperature": "20-35°C",
            "humidity": "低濕度",
            "soil": "排水良好的砂質土壤",
            "fertilizer": "生長期每月施肥",
            "pruning": "春季修剪"
        }
    },

    44: {
        "name": "玉樹",
        "scientific_name": "Crassula arborescens",
        "family": "景天科",
        "genus": "青鎖龍屬",
        "origin": "南非",
        "image": None,
        "brief": "玉樹是景天科青鎖龍屬的多肉植物，以其肥厚的葉片和粗壯的莖部聞名。",
        "description": """玉樹原產於南非，是多年生多肉灌木或小喬木。莖部粗壯，多分枝，木質化。葉片對生，肥厚，橢圓形或倒卵形，灰綠色。

花小，白色或淡粉色，簇生於枝頂，花期在冬季或早春。玉樹的葉片在充足光照下會呈現紅邊。

玉樹是常見的多肉植物，因其容易栽培和寓意「玉樹臨風」而被廣泛種植。""",
        "flower_language": "富貴、吉祥、堅強",
        "symbolism": "玉樹象徵著富貴和吉祥。其肥厚的葉片代表著堅強的生命力和儲存能量的智慧。",
        "tags": ["多肉植物", "觀賞植物", "室內植物", "盆景植物"],
        "seasons": ["春季", "秋季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "耐旱，澆水宜乾透澆透",
            "temperature": "15-25°C",
            "humidity": "低濕度",
            "soil": "排水良好的砂質土壤",
            "fertilizer": "生長期每月施肥",
            "pruning": "定期修剪維持形態"
        }
    },

    45: {
        "name": "蘆薈",
        "scientific_name": "Aloe vera",
        "family": "百合科",
        "genus": "蘆薈屬",
        "origin": "阿拉伯半島",
        "image": None,
        "brief": "蘆薈是百合科蘆薈屬的多肉植物，以其醫療和美容功效聞名於世。",
        "description": """蘆薈原產於阿拉伯半島，是多年生多肉草本。葉片大型，披針形，基部寬厚，葉緣有鋸齒，葉肉透明多汁。

花莖從葉腋抽出，總狀花序，小花黃色或橙紅色。蘆薈的葉肉含有豐富的凝膠，可用於護膚和醫療。

蘆薈是重要的藥用和美容植物。其凝膠可用於治療燒傷、曬傷和皮膚問題。""",
        "flower_language": "純潔、健康、治癒",
        "symbolism": "蘆薈象徵著純潔和健康的 生活。其治癒的特性代表著恢復和更新的力量。",
        "tags": ["多肉植物", "藥用植物", "美容植物", "室內植物"],
        "seasons": ["春季", "夏季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照至半日照",
            "water": "耐旱，澆水宜乾透澆透",
            "temperature": "15-30°C",
            "humidity": "低濕度",
            "soil": "排水良好的砂質土壤",
            "fertilizer": "生長期每月施肥",
            "pruning": "去除枯葉"
        }
    },

    46: {
        "name": "虎尾蘭",
        "scientific_name": "Sansevieria trifasciata",
        "family": "天門冬科",
        "genus": "虎尾蘭屬",
        "origin": "西非",
        "image": None,
        "brief": "虎尾蘭是天門冬科虎尾蘭屬的觀葉植物，以其堅挺的劍形葉片聞名。",
        "description": """虎尾蘭原產於西非，是多年生常綠草本。葉片大型，劍形，直立，基部抱合，葉面有深綠色的斑紋。

花莖短，總狀花序，小花白綠色或淡黃色，有芳香。虎尾蘭的葉片堅挺，造型簡潔現代。

虎尾蘭是重要的室內觀葉植物，其堅強的特性和淨化空氣的能力使其成為辦公室和家居的常見選擇。""",
        "flower_language": "堅強、剛毅、健康",
        "symbolism": "虎尾蘭象徵著堅強和剛毅的生命力。其筆直的葉片代表著正直和不屈的精神。",
        "tags": ["觀葉植物", "室內植物", "空氣淨化", "陰生植物"],
        "seasons": ["四季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照至散射光",
            "water": "耐旱，澆水宜乾透澆透",
            "temperature": "15-30°C",
            "humidity": "低至中等濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "生長期每2個月施肥",
            "pruning": "去除枯葉"
        }
    },

    47: {
        "name": "黃金葛",
        "scientific_name": "Epipremnum aureum",
        "family": "天南星科",
        "genus": "麒麟葉屬",
        "origin": "所羅門群島",
        "image": None,
        "brief": "黃金葛是天南星科麒麟葉屬的攀援植物，以其金黃色的斑紋葉片聞名。",
        "description": """黃金葛原產於所羅門群島，是多年生攀援草本。莖節具氣根，可攀附或垂吊。葉片心形，綠色帶黃色斑紋或全黃色。

黃金葛有多个品种，包括綠葉、金葉和斑葉等。其生長快速，適應性強。

黃金葛是極受歡迎的室內觀葉植物，其攀援或垂吊的姿態可美化空間。其淨化空氣的能力也獲得NASA認證。""",
        "flower_language": "堅強、活力、希望",
        "symbolism": "黃金葛象徵著堅強的生命力和對光的追求。其金黃的葉色代表著活力和希望。",
        "tags": ["觀葉植物", "室內植物", "攀援植物", "空氣淨化"],
        "seasons": ["四季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "散射光，避免直射",
            "water": "保持土壤濕潤",
            "temperature": "18-28°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "定期修剪控制生長"
        }
    },

    48: {
        "name": "蔓綠絨",
        "scientific_name": "Monstera deliciosa",
        "family": "天南星科",
        "genus": "龜背竹屬",
        "origin": "熱帶美洲",
        "image": None,
        "brief": "蔓綠絨是天南星科龜背竹屬的觀葉植物，以其大型裂葉聞名。",
        "description": """蔓綠絨原產於熱帶美洲，是多年生常綠攀援植物。莖粗壯，具氣根。葉片大型，幼時心形，成葉羽狀裂開。

葉片裂開是成熟的標誌，裂葉越多表示植株越成熟。其花為佛焰苞，但室內較少开花。

蔓綠絨是熱帶風格室內布置的首選植物。其大氣的葉片能立即提升空間的檔次。""",
        "flower_language": "熱帶風情、活力、獨特",
        "symbolism": "蔓綠絨象徵著熱帶風情和獨特的審美。其裂葉代表著成長和成熟的過程。",
        "tags": ["觀葉植物", "室內植物", "熱帶植物", "攀援植物"],
        "seasons": ["四季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "散射光或半日照",
            "water": "保持土壤濕潤",
            "temperature": "18-28°C",
            "humidity": "高濕度",
            "soil": "排水良好的腐殖質土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "去除枯葉"
        }
    },

    49: {
        "name": "龜背竹",
        "scientific_name": "Philodendron bipinnatifidum",
        "family": "天南星科",
        "genus": "喜林芋屬",
        "origin": "南美洲",
        "image": None,
        "brief": "龜背竹是天南星科喜林芋屬的觀葉植物，以其深裂的葉片和優雅的姿態聞名。",
        "description": """龜背竹原產於南美洲，是多年生常綠灌木或小喬木。莖粗壯直立，葉片大型，基生，深裂，葉柄長。

龜背竹的葉片會隨年齡增長而分裂加深，形成獨特的龜背狀圖案。其株型大氣，非常適合大型空間。

龜背竹是重要的室內觀葉植物，常用於客廳、辦公室等大空間的布置。""",
        "flower_language": "長壽、吉祥、健康",
        "symbolism": "龜背竹象徵著長壽和吉祥。其「龜」的形象在中國文化中代表著長壽和穩健。",
        "tags": ["觀葉植物", "室內植物", "熱帶植物", "大型盆栽"],
        "seasons": ["四季"],
        "care": {
            "difficulty": "中等",
            "sunlight": "散射光或半日照",
            "water": "保持土壤濕潤",
            "temperature": "18-28°C",
            "humidity": "高濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "去除枯葉"
        }
    },

    50: {
        "name": "福祿桐",
        "scientific_name": "Polyscias scutellaria",
        "family": "五加科",
        "genus": "南洋參屬",
        "origin": "太平洋群島",
        "image": None,
        "brief": "福祿桐是五加科南洋參屬的觀葉植物，以其圓潤的葉片和吉祥的名字聞名。",
        "description": """福祿桐原產於太平洋群島，是常綠灌木或小喬木。莖直立，分枝多，葉片互生，圓形或卵形，邊緣有鋸齒。

葉色有綠色、斑葉和金邊等品種。福祿桐的葉片圓潤可愛，造型整齊。

福祿桐因其吉祥的名字和優美的姿態成為受歡迎的室內觀葉植物。其寓意「福祿」深受華人喜愛。""",
        "flower_language": "福氣、吉祥、富貴",
        "symbolism": "福祿桐直接象徵著福氣和富貴。其名字中的「福祿」代表著幸福和俸祿。",
        "tags": ["觀葉植物", "室內植物", "吉利植物", "小型盆栽"],
        "seasons": ["四季"],
        "care": {
            "difficulty": "容易",
            "sunlight": "半日照至散射光",
            "water": "保持土壤濕潤",
            "temperature": "18-28°C",
            "humidity": "中等至高濕度",
            "soil": "排水良好的肥沃土壤",
            "fertilizer": "生長期每2週施肥",
            "pruning": "定期修剪維持形態"
        }
    },
}

# ==========================================
# 圖片快取
# ==========================================
IMAGE_CACHE = {}

# ==========================================
# 獲取植物資料（自動獲取維基圖片）
# ==========================================
def get_plant_data(plant_id):
    """獲取植物資料，並從維基百科獲取圖片"""
    if plant_id not in PLANT_DATABASE:
        return None
    
    plant = PLANT_DATABASE[plant_id].copy()
    
    if not plant.get("image"):
        cache_key = f"{plant['name']}_{plant['scientific_name']}"
        
        # 優先使用記憶體快取
        if cache_key in IMAGE_CACHE:
            plant["image"] = IMAGE_CACHE[cache_key]
            print(f"✓ 使用記憶體快取: {plant['name']}")
        else:
            # 其次使用檔案快取
            cached_url = _load_image_cache(plant['name'])
            if cached_url:
                plant["image"] = cached_url
                IMAGE_CACHE[cache_key] = cached_url
                print(f"✓ 使用檔案快取: {plant['name']}")
            else:
                # 都沒有才抓新圖片
                wiki_image = get_wikipedia_image(plant["name"], plant["scientific_name"])
                
                if not wiki_image:
                    print(f"→ 嘗試從 Commons 搜尋: {plant['name']}")
                    wiki_image = search_commons_image(plant["name"], plant["scientific_name"])
                
                if wiki_image:
                    plant["image"] = wiki_image
                    IMAGE_CACHE[cache_key] = wiki_image
                    _save_image_cache(plant['name'], wiki_image)
                    print(f"✓ 新圖片已儲存: {plant['name']}")
                else:
                    plant["image"] = f"https://via.placeholder.com/400x300/2d5c3a/ffffff?text={quote(plant['name'])}"
                    print(f"✗ 使用備用圖片: {plant['name']}")
    
    return plant

# ==========================================
# 今日推薦植物（含推薦原由）
# ==========================================
def get_daily_plant():
    """根據日期返回每日推薦植物，並生成推薦原由"""
    today = datetime.now()
    plant_id = (today.timetuple().tm_yday % len(PLANT_DATABASE)) + 1
    plant = get_plant_data(plant_id)
    
    if plant:
        # 添加推薦原由
        plant["recommendation_reasons"] = get_recommendation_reason(today, plant)
        plant["recommendation_date"] = today.strftime("%Y年%m月%d日")
        plant["weekday"] = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"][today.weekday()]
    
    return plant

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
