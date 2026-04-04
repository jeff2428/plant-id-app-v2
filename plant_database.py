"""
🌿 植物資料庫模組
包含植物詳細資料、今日推薦功能
"""

from datetime import datetime
import hashlib

# ==========================================
# 植物資料庫
# ==========================================
PLANT_DATABASE = {
    "rose": {
        "name": "玫瑰",
        "scientific_name": "Rosa",
        "family": "薔薇科",
        "genus": "薔薇屬",
        "image": "https://images.unsplash.com/photo-1455659817273-f96807779a8a?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1455659817273-f96807779a8a?w=400",
        "origin": "亞洲、歐洲、北美洲",
        "brief": "玫瑰是世界上最受歡迎的觀賞花卉之一，以其優雅的花形和迷人的香氣聞名於世。",
        "flower_language": "愛情、美麗、熱情",
        "symbolism": "玫瑰自古以來就是愛情的象徵，紅玫瑰代表熱烈的愛，白玫瑰象徵純潔，粉玫瑰表達溫柔的愛意。",
        "description": """
玫瑰（Rosa）是薔薇科薔薇屬植物的通稱，原產於亞洲，現已廣泛種植於世界各地。玫瑰花朵大而美麗，色彩豐富，從純白到深紅，甚至有藍色和彩虹色的品種。

**形態特徵**
- 灌木或攀緣植物
- 莖上有刺
- 花瓣5枚或重瓣
- 花色多樣：紅、粉、白、黃、橙等

**生長習性**
玫瑰喜歡陽光充足、通風良好的環境，適合在排水良好的土壤中生長。春季是玫瑰開花的主要季節，部分品種可四季開花。

**栽培要點**
- 日照：全日照（每天6小時以上）
- 澆水：保持土壤濕潤，避免積水
- 施肥：生長期每月施肥一次
- 修剪：冬季休眠期進行重剪

**藥用價值**
玫瑰花瓣可用於製作玫瑰茶、玫瑰精油，具有美容養顏、舒緩情緒的功效。
        """,
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照",
            "water": "中等，保持濕潤",
            "temperature": "15-28°C",
            "humidity": "50-70%",
            "soil": "排水良好的肥沃���壤",
            "fertilizer": "生長期每月施肥",
            "pruning": "冬季重剪，花後輕剪"
        },
        "seasons": ["春", "夏", "秋"],
        "tags": ["觀花", "香氣", "愛情", "園藝"]
    },
    
    "sunflower": {
        "name": "向日葵",
        "scientific_name": "Helianthus annuus",
        "family": "菊科",
        "genus": "向日葵屬",
        "image": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?w=400",
        "origin": "北美洲",
        "brief": "向日葵因其花朵���隨著太陽轉動而得名，是陽光和希望的象徵。",
        "flower_language": "崇拜、忠誠、陽光、希望",
        "symbolism": "向日葵象徵著對陽光的追求，代表積極向上、充滿希望的人生態度，也寓意忠誠和堅定的愛。",
        "description": """
向日葵（Helianthus annuus）是菊科向日葵屬的一年生草本植物，原產於北美洲，現已成為世界重要的油料作物和觀賞植物。

**形態特徵**
- 株高可達1-3米
- 花盤直徑可達30厘米以上
- 舌狀花黃色，管狀花褐色或紫色
- 種子（葵花籽）可食用

**生長習性**
向日葵是典型的向光性植物，幼嫩的花盤會隨太陽轉動（向日性），成熟後固定朝東。喜溫暖、耐旱，生長迅速。

**栽培要點**
- 日照：全日照，越多越好
- 澆水：耐旱，但開花期需充足水分
- 施肥：基肥為主，追肥為輔
- 土壤：適應性強，但喜肥沃土壤

**經濟價值**
- 葵花籽油：優質食用油
- 葵花籽：營養豐富的零食
- 觀賞價值：切花、園藝景觀
        """,
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "中等，耐旱",
            "temperature": "20-30°C",
            "humidity": "40-60%",
            "soil": "肥沃排水良好",
            "fertilizer": "播種前施基肥",
            "pruning": "一般不需修剪"
        },
        "seasons": ["夏", "秋"],
        "tags": ["觀花", "食用", "油料", "陽光"]
    },
    
    "orchid": {
        "name": "蝴蝶蘭",
        "scientific_name": "Phalaenopsis",
        "family": "蘭科",
        "genus": "蝴蝶蘭屬",
        "image": "https://images.unsplash.com/photo-1566836610593-62a64888c216?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1566836610593-62a64888c216?w=400",
        "origin": "東南亞熱帶地區",
        "brief": "蝴蝶蘭因花形似蝴蝶而得名，是最受歡迎的室內觀賞蘭花之一。",
        "flower_language": "幸福來臨、純潔、優雅",
        "symbolism": "蝴蝶蘭象徵著幸福和高雅，在華人文化中寓意「蝴蝶飛來，幸福到來」，是送禮和節慶的首選花卉。",
        "description": """
蝴蝶蘭（Phalaenopsis）是蘭科蝴蝶蘭屬植物的總稱，原產於東南亞熱帶雨林，現已成為全球最暢銷的盆栽蘭花。

**形態特徵**
- 附生蘭，無假球莖
- 葉片肥厚，深綠色
- 花莖長，可著生多朵花
- 花色豐富：白、粉、紫、黃、斑紋等

**生長習性**
蝴蝶蘭在自然環境中附生於樹幹上，喜歡溫暖、濕潤、通風的環境，不耐寒，忌強光直射。

**栽培要點**
- 日照：散射光，避免強光
- 澆水：根部乾燥後再澆，不可積水
- 施肥：生長期薄肥勤施
- 溫度：15-30°C，晝夜溫差有助開花

**花期管理**
蝴蝶蘭花期可長達2-3個月，花謝後剪除花梗，適當降溫可促進再次開花。
        """,
        "care": {
            "difficulty": "中等",
            "sunlight": "散射光",
            "water": "少量，根乾再澆",
            "temperature": "18-28°C",
            "humidity": "60-80%",
            "soil": "水苔或蘭花專用介質",
            "fertilizer": "生長期每2週一次",
            "pruning": "花後剪除花梗"
        },
        "seasons": ["春", "冬"],
        "tags": ["觀花", "室內", "高雅", "送禮"]
    },
    
    "lavender": {
        "name": "薰衣草",
        "scientific_name": "Lavandula",
        "family": "唇形科",
        "genus": "薰衣草屬",
        "image": "https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1499002238440-d264edd596ec?w=400",
        "origin": "地中海沿岸",
        "brief": "薰衣草以其迷人的紫色花穗和舒緩的香氣聞名，是芳香療法的代表植物。",
        "flower_language": "等待愛情、浪漫、寧靜",
        "symbolism": "薰衣草象徵著浪漫和等待，紫色的花海代表著夢幻與純淨的愛情，也寓意安寧與療癒。",
        "description": """
薰衣草（Lavandula）是唇形科薰衣草屬的多年生芳香植物，原產於地中海沿岸，以其優美的紫色花穗和獨特的香氣而聞名於世。

**形態特徵**
- 常綠小灌木
- 株高30-100厘米
- 葉片銀灰色，線形
- 花穗紫色或藍紫色

**生長習性**
薰衣草喜歡陽光充足、乾燥涼爽的環境，耐旱、耐寒，不耐高溫高濕。原產地中海型氣候最適合其生長。

**栽培要點**
- 日照：全日照
- 澆水：少量，寧乾勿濕
- 施肥：少肥，避免氮肥過多
- 修剪：花後修剪促進分枝

**應用價值**
- 精油提取：芳香療法
- 乾燥花：香包、裝飾
- 茶飲：舒緩助眠
- 護膚品：抗菌、修復
        """,
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照",
            "water": "少量，耐旱",
            "temperature": "15-25°C",
            "humidity": "40-50%",
            "soil": "鹼性排水良好",
            "fertilizer": "少肥",
            "pruning": "花後輕剪"
        },
        "seasons": ["夏"],
        "tags": ["香草", "芳療", "浪漫", "紫色"]
    },
    
    "monstera": {
        "name": "龜背芋",
        "scientific_name": "Monstera deliciosa",
        "family": "天南星科",
        "genus": "龜背芋屬",
        "image": "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1614594975525-e45190c55d0b?w=400",
        "origin": "中美洲熱帶雨林",
        "brief": "龜背芋以其獨特的裂葉造型聞名，是近年最流行的室內觀葉植物之一。",
        "flower_language": "健康長壽、堅韌不拔",
        "symbolism": "龜背芋的葉片紋路如龜甲，象徵長壽健康；其堅韌的生命力也代表著不屈不撓的精神。",
        "description": """
龜背芋（Monstera deliciosa）是天南星科龜背芋屬的常綠藤本植物，原產於中美洲熱帶雨林，因其葉片的獨特裂孔造型而廣受喜愛。

**形態特徵**
- 攀緣藤本植物
- 葉片大型，心形，具深裂和孔洞
- 氣生根發達
- 成熟葉可達60-90厘米

**生長習性**
龜背芋在原生環境中攀附在大樹上生長，喜歡溫暖濕潤、散射光充足的環境，是極佳的室內綠植。

**栽培要點**
- 日照：明亮散射光
- 澆水：土壤略乾即澆
- 施肥：生長期每月一次
- 支撐：提供攀爬支柱

**特殊說明**
- 幼葉完整，成熟後才出現裂孔
- 果實成熟可食用（需完全成熟）
- 汁液有微毒，避免誤食
        """,
        "care": {
            "difficulty": "容易",
            "sunlight": "明亮散射光",
            "water": "中等，土乾再澆",
            "temperature": "18-30°C",
            "humidity": "60-80%",
            "soil": "疏鬆排水良好",
            "fertilizer": "生長期每月一次",
            "pruning": "修剪老葉黃葉"
        },
        "seasons": ["四季常綠"],
        "tags": ["觀葉", "室內", "網紅植物", "熱帶"]
    },
    
    "sakura": {
        "name": "櫻花",
        "scientific_name": "Prunus serrulata",
        "family": "薔薇科",
        "genus": "李屬",
        "image": "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=400",
        "origin": "東亞（日本、中國、韓國）",
        "brief": "櫻花是日本的國花，以其短暫而絢爛的花期象徵著生命之美。",
        "flower_language": "生命之美、純潔、高尚",
        "symbolism": "櫻花象徵著生命的短暫與美麗，提醒人們珍惜當下。在日本文化中，櫻花代表著武士道精神——燦爛綻放，毅然凋落。",
        "description": """
櫻花（Prunus serrulata）是薔薇科李屬的落葉喬木，原產於東亞地區，是日本的國花，也是東亞文化中重要的象徵植物。

**形態特徵**
- 落葉喬木，株高5-25米
- 花瓣5枚或重瓣
- 花色：白、淡粉、粉紅
- 花期短暫，約7-14天

**生長習性**
櫻花喜歡溫涼氣候，需要冬季低溫休眠，春季氣溫回升時開花。不耐酷暑和嚴寒。

**著名品種**
- 染井吉野：最常見的觀賞品種
- 河津櫻：早開品種，粉紅色
- 八重櫻：重瓣品種，花期較長
- 枝垂櫻：枝條下垂，姿態優美

**文化意義**
櫻花在東亞文化中具有深遠意義，日本每年的「花見」（賞櫻）活動吸引無數遊客。櫻花的短暫綻放也成為許多文學、藝術作品的靈感來源。
        """,
        "care": {
            "difficulty": "中等偏難",
            "sunlight": "全日照",
            "water": "中等",
            "temperature": "10-25°C",
            "humidity": "50-70%",
            "soil": "肥沃排水良好",
            "fertilizer": "花後施肥",
            "pruning": "花後修剪"
        },
        "seasons": ["春"],
        "tags": ["觀花", "日本", "春天", "短暫之美"]
    },
    
    "lotus": {
        "name": "荷花",
        "scientific_name": "Nelumbo nucifera",
        "family": "蓮科",
        "genus": "蓮屬",
        "image": "https://images.unsplash.com/photo-1474557157379-8aa74a6ef541?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1474557157379-8aa74a6ef541?w=400",
        "origin": "亞洲、澳洲",
        "brief": "荷花出淤泥而不染，是東方文化中高潔品格的象徵。",
        "flower_language": "純潔、高雅、清廉、圓滿",
        "symbolism": "荷花在佛教中象徵純淨與覺悟，在中國文化中代表君子之德——出淤泥而不染，濯清漣而不妖。",
        "description": """
荷花（Nelumbo nucifera）是蓮科蓮���的多年生水生植物，原產於亞洲熱帶和溫帶地區，是中國的十大名花之一。

**形態特徵**
- 水生草本植物
- 葉片大型圓形，具蠟質
- 花大而美麗，直徑可達20厘米
- 花色：白、粉、紅

**生長習性**
荷花生長於池塘、湖泊等靜水環境，喜歡溫暖陽光充足的環境，地下莖（藕）在泥中越冬。

**全株可用**
- 荷花：觀賞、茶飲
- 蓮子：食用、中藥
- 藕：蔬菜
- 荷葉：包裹食物、茶飲
- 蓮藕節：中藥材

**文化意義**
荷花在東方文化中地位崇高，佛教以蓮花為聖物，中國古典文學中更是君子品格的象徵。周敦頤的《愛蓮說》千古傳頌。
        """,
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照",
            "water": "水生植物",
            "temperature": "20-30°C",
            "humidity": "高",
            "soil": "池塘泥土",
            "fertilizer": "生長期施用水生肥",
            "pruning": "清除枯葉"
        },
        "seasons": ["夏"],
        "tags": ["水生", "觀花", "佛教", "君子"]
    },
    
    "succulent": {
        "name": "多肉植物",
        "scientific_name": "Succulents",
        "family": "多科",
        "genus": "多屬",
        "image": "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1509423350716-97f9360b4e09?w=400",
        "origin": "世界各地乾旱地區",
        "brief": "多肉植物以其肥厚多汁的外形和易養護的特性，成為現代都市人的療癒夥伴。",
        "flower_language": "堅韌、療癒、簡約之美",
        "symbolism": "多肉植物象徵著頑強的生命力和適應環境的能力，也代表著現代生活中的簡約美學和治癒力量。",
        "description": """
多肉植物（Succulents）是指莖、葉或根特別肥厚多汁的植物總稱，包含多個科屬，分布於世界各地的乾旱地區。

**形態特徵**
- 莖葉肥厚，儲存水分
- 形態多樣：蓮座型、柱狀、匍匐等
- 顏色豐富：綠、紅、紫、藍等
- 體型從微型到大型

**主要類群**
- 景天科：石蓮花、玉露、熊童子
- 番杏科：生石花、玉扇
- 百合科：蘆薈、十二卷
- 仙人掌科：仙人球、仙人柱

**栽培要點**
- 日照：充足陽光（部分需遮陰）
- 澆水：寧乾勿濕，不耐積水
- 配土：顆粒土為主，排水良好
- 通風：良好通風防止病害

**新手推薦**
姬朧月、玉露、黃麗、虹之玉、熊童子等品種適合新手入門。
        """,
        "care": {
            "difficulty": "容易",
            "sunlight": "充足陽光",
            "water": "少量，乾透再澆",
            "temperature": "10-30°C",
            "humidity": "30-50%",
            "soil": "顆粒土為主",
            "fertilizer": "生長期薄肥",
            "pruning": "摘除枯葉"
        },
        "seasons": ["四季"],
        "tags": ["多肉", "療癒", "易養", "桌面植物"]
    },
    
    "bamboo": {
        "name": "竹子",
        "scientific_name": "Bambusoideae",
        "family": "禾本科",
        "genus": "竹亞科",
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
        "origin": "亞洲熱帶與亞熱帶",
        "brief": "竹子是生長最快的植物之一，以其挺拔的姿態象徵著氣節與堅韌。",
        "flower_language": "氣節、堅韌、謙虛、長壽",
        "symbolism": "竹子在東亞文化中象徵君子之德，與梅、蘭、菊並稱「四君子」，與松、梅合稱「歲寒三友」，代表堅韌不屈的品格。",
        "description": """
竹子是禾本科竹亞科植物的統稱，主要分布於亞洲熱帶和亞熱帶地區，是世界上生長速度最快的植物之一。

**形態特徵**
- 木質化的禾本科植物
- 莖（竹竿）中空有節
- 常綠或落葉
- 地下莖發達

**生長特性**
竹子可以在一天之內生長近1米，是地球上生長最快的植物。竹子一生只開一次花，開花後往往會死亡。

**主要品種**
- 毛竹：最常見的大型竹
- 桂竹：優質食用筍
- 孟宗竹：冬筍來源
- 觀音竹：室內觀賞
- 富貴竹：水培觀賞

**應用價值**
- 建築材料：竹屋、竹橋
- 生活用品：竹筷、竹籃
- 食用：竹筍
- 造紙原料
- 觀賞園藝
        """,
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照或半遮陰",
            "water": "中等偏多",
            "temperature": "15-30°C",
            "humidity": "60-80%",
            "soil": "肥沃濕潤",
            "fertilizer": "春季施肥",
            "pruning": "疏除老竿"
        },
        "seasons": ["四季常綠"],
        "tags": ["觀葉", "君子", "東方", "快速生長"]
    },
    
    "jasmine": {
        "name": "茉莉花",
        "scientific_name": "Jasminum sambac",
        "family": "木犀科",
        "genus": "茉莉屬",
        "image": "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?w=400",
        "origin": "印度、阿拉伯",
        "brief": "茉莉花以其潔白的花朵和馥郁的香氣聞名，是製作花茶的重要原料。",
        "flower_language": "純潔、親切、優雅",
        "symbolism": "茉莉花象徵純潔和友誼，在許多國家被視為神聖的花朵。在菲律賓和印尼，茉莉花是國花。",
        "description": """
茉莉花（Jasminum sambac）是木犀科茉莉屬的常綠灌木，原產於印度，現廣泛種植於熱帶和亞熱帶地區。

**形態特徵**
- 常綠灌木或藤本
- 葉片對生，卵形
- 花白色，重瓣或單瓣
- 花香濃郁持久

**生長習性**
茉莉花喜歡溫暖濕潤的環境，怕冷，在中國南方生長良好。夏季是主要花期，香氣在夜間更加濃郁。

**栽培要點**
- 日照：全日照或半日照
- 澆水：喜濕潤，怕積水
- 施肥：花期前後施肥
- 修剪：花後修剪促進分枝

**應用價值**
- 茉莉花茶：中國傳統名茶
- 精油提取：高級香水原料
- 觀賞：盆栽、花架
- 佛教供花
        """,
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照",
            "water": "保持濕潤",
            "temperature": "20-35°C",
            "humidity": "60-80%",
            "soil": "酸性排水良好",
            "fertilizer": "花期前後施肥",
            "pruning": "花後修剪"
        },
        "seasons": ["夏", "秋"],
        "tags": ["香花", "茶飲", "白色", "夜香"]
    },
    
    "ginkgo": {
        "name": "銀杏",
        "scientific_name": "Ginkgo biloba",
        "family": "銀杏科",
        "genus": "銀杏屬",
        "image": "https://images.unsplash.com/photo-1509335919466-c196457ea95a?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1509335919466-c196457ea95a?w=400",
        "origin": "中國",
        "brief": "銀杏是地球上最古老的樹種之一，被稱為「活化石」，金黃色的秋葉美不勝收。",
        "flower_language": "堅韌、長壽、永恆的愛",
        "symbolism": "銀杏象徵著長壽���堅韌，因其能存活千年而被視為永恆的象徵。金黃的銀杏葉也代表著成熟和收穫。",
        "description": """
銀杏（Ginkgo biloba）是銀杏科銀杏屬的落葉喬木，是現存最古老的樹種之一，被譽為「活化石」，原產於中國。

**形態特徵**
- 落葉大喬木，可高達40米
- 葉片扇形，秋季金黃
- 雌雄異株
- 種子（白果）可食用

**生長特性**
銀杏生長緩慢但壽命極長，可存活數千年。「公孫樹」之名源於「公種而孫得食」，說明其生長緩慢的特性。

**栽培要點**
- 日照：全日照
- 澆水：中等，耐旱
- 土壤：適應性強
- 特點：極少病蟲害

**應用價值**
- 觀賞：行道樹、園景樹
- 藥用：銀杏葉提取物
- 食用：白果（需處理後食用）
- 木材：珍貴木材

**文化意義**
銀杏在中國文化中具有特殊地位，許多古剎寺廟都種有千年銀杏，是吉祥長壽的象徵。
        """,
        "care": {
            "difficulty": "容易",
            "sunlight": "全日照",
            "water": "中等",
            "temperature": "-20~35°C",
            "humidity": "適應性強",
            "soil": "排水良好",
            "fertilizer": "春季施肥",
            "pruning": "冬季修剪"
        },
        "seasons": ["秋（觀葉）"],
        "tags": ["觀葉", "行道樹", "活化石", "長壽"]
    },
    
    "plum_blossom": {
        "name": "梅花",
        "scientific_name": "Prunus mume",
        "family": "薔薇科",
        "genus": "李屬",
        "image": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=800",
        "thumbnail": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=400",
        "origin": "中國",
        "brief": "梅花凌寒獨放，是中國十大名花之首，象徵著堅韌不拔的民族精神。",
        "flower_language": "堅強、高雅、忠貞",
        "symbolism": "梅花象徵著不畏嚴寒、堅韌不拔的精神，是中國的國花候選之一。與蘭、竹、菊並稱「四君子」，與松、竹並稱「歲寒三友」。",
        "description": """
梅花（Prunus mume）是薔薇科李屬的落葉小喬木，原產於中國，是中國傳統名花，位列十大名花之首。

**形態特徵**
- 落葉小喬木，株高4-10米
- 花先葉開放
- 花色：白、粉、紅
- 花香清雅

**生長習性**
梅花耐寒性強，在寒冷的冬末春初開花，「凌寒獨自開」正是其獨特魅力所在。

**著名品種**
- 宮粉梅：粉紅色，最常見
- 綠萼梅：萼片綠色
- 朱砂梅：花色深紅
- 玉蝶梅：白色重瓣

**文化意義**
梅花在中國文化中具有崇高地位，歷代文人墨客留下無數詠梅詩篇。王安石的「牆角數枝梅，凌寒獨自開」膾炙人口。

**應用價值**
- 觀賞：園林、盆景
- 食用：梅子（青梅、烏梅）
- 藥用：烏梅入藥
        """,
        "care": {
            "difficulty": "中等",
            "sunlight": "全日照",
            "water": "中等",
            "temperature": "-10~30°C",
            "humidity": "50-70%",
            "soil": "排水良好",
            "fertilizer": "花後施肥",
            "pruning": "花後修剪整形"
        },
        "seasons": ["冬", "早春"],
        "tags": ["觀花", "國花", "四君子", "傲骨"]
    }
}

# ==========================================
# 工具函數
# ==========================================

def get_all_plants():
    """取得所有植物資料"""
    return PLANT_DATABASE

def get_plant_by_id(plant_id: str) -> dict:
    """根據 ID 取得植物資料"""
    return PLANT_DATABASE.get(plant_id, None)

def get_plant_list():
    """取得植物列表（簡化資訊）"""
    return [
        {
            "id": pid,
            "name": data["name"],
            "scientific_name": data["scientific_name"],
            "thumbnail": data["thumbnail"],
            "brief": data["brief"],
            "flower_language": data["flower_language"]
        }
        for pid, data in PLANT_DATABASE.items()
    ]

def get_daily_plant(date: datetime = None) -> dict:
    """
    取得今日推薦植物
    根據日期產生固定的推薦（同一天看到同一種植物）
    """
    if date is None:
        date = datetime.now()
    
    # 使用日期字串產生 hash，確保同一天推薦同一種植物
    date_str = date.strftime("%Y-%m-%d")
    hash_value = int(hashlib.md5(date_str.encode()).hexdigest(), 16)
    
    plant_ids = list(PLANT_DATABASE.keys())
    index = hash_value % len(plant_ids)
    
    plant_id = plant_ids[index]
    plant_data = PLANT_DATABASE[plant_id].copy()
    plant_data["id"] = plant_id
    
    return plant_data

def get_random_plants(count: int = 3, exclude: list = None) -> list:
    """
    取得隨機植物推薦
    """
    import random
    
    if exclude is None:
        exclude = []
    
    available = [pid for pid in PLANT_DATABASE.keys() if pid not in exclude]
    
    if len(available) <= count:
        selected = available
    else:
        selected = random.sample(available, count)
    
    return [
        {**PLANT_DATABASE[pid], "id": pid}
        for pid in selected
    ]

def search_plants(keyword: str) -> list:
    """
    搜尋植物
    """
    keyword = keyword.lower()
    results = []
    
    for pid, data in PLANT_DATABASE.items():
        # 搜尋名稱、學名、標籤
        searchable = f"{data['name']} {data['scientific_name']} {' '.join(data.get('tags', []))}".lower()
        if keyword in searchable:
            results.append({**data, "id": pid})
    
    return results

def get_plants_by_tag(tag: str) -> list:
    """
    根據標籤取得植物
    """
    results = []
    
    for pid, data in PLANT_DATABASE.items():
        if tag in data.get("tags", []):
            results.append({**data, "id": pid})
    
    return results

def get_all_tags() -> list:
    """
    取得所有標籤
    """
    tags = set()
    for data in PLANT_DATABASE.values():
        tags.update(data.get("tags", []))
    return sorted(list(tags))