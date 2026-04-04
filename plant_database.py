import random
from datetime import datetime
import requests
from urllib.parse import quote
import time

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
    """根據月份判斷季節"""
    if month in [3, 4, 5]:
        return "春季"
    elif month in [6, 7, 8]:
        return "夏季"
    elif month in [9, 10, 11]:
        return "秋季"
    else:
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
    temp_range = care.get("temperature", "")
    
    climate_reasons = {
        1: "寒冬時節",
        2: "春寒料峭",
        3: "春暖花開",
        4: "春意盎然",
        5: "初夏時光",
        6: "盛夏驕陽",
        7: "炎炎夏日",
        8: "夏末秋初",
        9: "秋高氣爽",
        10: "金秋十月",
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
    }
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
        
        if cache_key in IMAGE_CACHE:
            plant["image"] = IMAGE_CACHE[cache_key]
            print(f"✓ 使用快取圖片: {plant['name']}")
        else:
            wiki_image = get_wikipedia_image(plant["name"], plant["scientific_name"])
            
            if not wiki_image:
                print(f"→ 嘗試從 Commons 搜尋: {plant['name']}")
                wiki_image = search_commons_image(plant["name"], plant["scientific_name"])
            
            if wiki_image:
                plant["image"] = wiki_image
                IMAGE_CACHE[cache_key] = wiki_image
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
