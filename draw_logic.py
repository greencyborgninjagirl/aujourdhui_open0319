# 《aujourd'hui》抽牌与艺术联觉逻辑
# 每张小阿卡纳牌有专属作品匹配；Met API 失败时花色池兜底

import random
from typing import Callable

try:
    import requests
except ImportError:
    requests = None

from artwork_minor import ARTWORK_BY_MINOR_CARD

# ---------------------------------------------------------------------------
# 1. 牌池与抽牌
# ---------------------------------------------------------------------------


def _base_card_name(card_name: str) -> str:
    """返回牌面基础名（去除「· 逆位」）。"""
    if " · 逆位" in card_name:
        return card_name.replace(" · 逆位", "").strip()
    return card_name


def build_card_pool(card_names: list[str]) -> list[str]:
    """
    从 78 张正位牌名构建 156 张牌池（每张正位 + 逆位）。
    用于随机抽取一张。
    """
    return [c for base in card_names for c in (base, base + " · 逆位")]


def draw_one_card(
    card_pool: list[str],
    get_meaning: Callable[[str, str], str],
) -> tuple[str, str]:
    """
    从 156 张牌池中随机抽一张，并解析其牌义。

    :param card_pool: 156 张牌名列表（正位 + 逆位）
    :param get_meaning: (card_name, base_card) -> base_meaning 的取值函数
    :return: (card_name, base_meaning)

    注意：若抽牌结果总是相同，请检查 1) 是否在某处调用了 random.seed；
    2) card_pool 长度是否为 156；3) 是否误用了 session_state 导致重复使用同一结果。
    """
    if not card_pool:
        return "", "照见当下的自己。"
    card_name = random.choice(card_pool)
    base_card = _base_card_name(card_name)
    base_meaning = get_meaning(card_name, base_card)
    return card_name, base_meaning


# ---------------------------------------------------------------------------
# 2. 艺术联觉（名画匹配）
# 优先 Met API 实时搜索，失败则回退到扩展静态池
# ---------------------------------------------------------------------------

# 中文关键词 → 英文 Met API 搜索词（逻辑映射中的关键词多为中文，需转译为英文）
KEYWORD_ZH_TO_EN = {
    "灵感": "inspiration", "行动": "action", "能量": "energy", "竞争": "competition", "冲突": "conflict",
    "情感": "emotion", "爱": "love", "直觉": "intuition", "联结": "connection", "和谐": "harmony",
    "思维": "thought", "真相": "truth", "清晰": "clarity", "理性": "reason",
    "物质": "material", "财富": "wealth", "稳固": "stability", "收获": "harvest",
    "探索": "exploration", "好奇": "curiosity", "创造": "creation", "滋养": "nurture",
    "平衡": "balance", "抉择": "choice", "转化": "transformation", "希望": "hope",
    "月亮": "moon", "太阳": "sun", "星星": "star", "花": "flower", "水": "water",
    "火": "fire", "风": "wind", "山": "mountain", "海": "sea", "夜": "night",
    "休息": "rest", "沉思": "contemplation", "孤独": "solitude", "欢庆": "celebration",
}

# 大阿卡纳主题 → 英文搜索词（补充 Met API 搜索）
THEME_SEARCH_TERMS = {
    "愚人": ["wanderer", "journey", "freedom"],
    "魔术师": ["creation", "magician", "skill"],
    "女祭司": ["wisdom", "moon", "intuition"],
    "皇后": ["nature", "abundance", "fertility"],
    "皇帝": ["mountain", "authority", "structure"],
    "教皇": ["tradition", "teaching"],
    "恋人": ["love", "choice"],
    "战车": ["chariot", "victory"],
    "力量": ["lion", "strength"],
    "隐士": ["solitude", "lantern"],
    "命运之轮": ["wheel", "fate"],
    "正义": ["balance", "scale"],
    "倒吊人": ["suspension", "reflection"],
    "死神": ["transformation"],
    "节制": ["temperance", "balance"],
    "恶魔": ["temptation"],
    "高塔": ["tower"],
    "星星": ["star", "hope"],
    "月亮": ["moon"],
    "太阳": ["sun", "light"],
    "审判": ["angel", "rebirth"],
    "世界": ["world", "completion"],
}

# 花色 → 英文搜索词
SUIT_SEARCH_TERMS = {
    "权杖": ["flame", "passion", "action", "creativity"],
    "圣杯": ["water", "emotion", "love", "heart"],
    "宝剑": ["thought", "truth", "blade", "clarity"],
    "星币": ["nature", "coin", "earth", "harvest"],
}

# 大阿卡纳主题 -> 扩展静态池（每主题 2–3 张，随机选）
ARTWORK_BY_MAJOR_THEME = {
    "愚人": [
        {"artist": "Claude Monet", "title": "Wheatstacks, Snow Effect, Morning", "year": 1891, "url": "https://www.artic.edu/artworks/64818", "reason": "雪后麦垛的留白与朦胧，呼应愚人牌中未被命名的可能性与信任过程的轻盈感。"},
        {"artist": "Vincent van Gogh", "title": "Wheat Field with Cypresses", "year": 1889, "url": "https://www.metmuseum.org/art/collection/search/436535", "reason": "麦田与天空的广阔，呼应愚人牌迈向未知的起点。"},
    ],
    "魔术师": [
        {"artist": "Pierre-Auguste Renoir", "title": "Two Sisters (On the Terrace)", "year": 1881, "url": "https://www.artic.edu/artworks/14655", "reason": "姐妹俩坐在露台的静谧瞬间，呼应魔术师牌中资源齐备、从容开启的表达姿态。"},
        {"artist": "Rembrandt", "title": "The Philosopher in Meditation", "year": 1632, "url": "https://commons.wikimedia.org/wiki/File:Rembrandt_-_The_Philosopher_in_Meditation.jpg", "reason": "内省与创造的前奏，呼应魔术师整合四元素的意象。"},
    ],
    "女祭司": [
        {"artist": "Johannes Vermeer", "title": "Girl with a Pearl Earring", "year": 1665, "url": "https://commons.wikimedia.org/wiki/File:Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_1665.jpg", "reason": "少女的静默与内省，呼应女祭司牌中直觉觉察与智慧沉淀的意象。"},
        {"artist": "Claude Monet", "title": "Impression, Sunrise", "year": 1872, "url": "https://commons.wikimedia.org/wiki/File:Claude_Monet,_Impression,_soleil_levant.jpg", "reason": "朦胧的光影与未名的直觉，呼应女祭司的静默智慧。"},
    ],
    "皇后": [
        {"artist": "Pierre-Auguste Renoir", "title": "Luncheon of the Boating Party", "year": 1881, "url": "https://www.phillipscollection.org/collection/luncheon-boating-party", "reason": "丰盛与欢愉的瞬间，呼应皇后牌中滋养与创造的丰盛感。"},
        {"artist": "Gustav Klimt", "title": "The Tree of Life", "year": 1909, "url": "https://commons.wikimedia.org/wiki/File:Gustav_Klimt_019.jpg", "reason": "生命的丰饶与创造，呼应皇后牌滋养万物的意象。"},
    ],
    "皇帝": [
        {"artist": "Caspar David Friedrich", "title": "Wanderer above the Sea of Fog", "year": 1818, "url": "https://commons.wikimedia.org/wiki/File:Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg", "reason": "立于山巅的凝视，呼应皇帝牌中结构与边界的稳定感。"},
        {"artist": "Thomas Cole", "title": "The Oxbow", "year": 1836, "url": "https://www.metmuseum.org/art/collection/search/10497", "reason": "秩序与疆域的视野，呼应皇帝牌的统御感。"},
    ],
    "教皇": [
        {"artist": "Rembrandt", "title": "The Night Watch", "year": 1642, "url": "https://commons.wikimedia.org/wiki/File:The_Night_Watch,_by_Rembrandt_van_Rijn_(SM).jpg", "reason": "秩序与指引的意象，呼应教皇牌中价值体系与知识传承的主题。"},
        {"artist": "Raphael", "title": "The School of Athens", "year": 1511, "url": "https://commons.wikimedia.org/wiki/File:Sanzio_01.jpg", "reason": "传统与知识的传承，呼应教皇牌的教导意象。"},
    ],
    "恋人": [
        {"artist": "Gustav Klimt", "title": "The Kiss", "year": 1908, "url": "https://commons.wikimedia.org/wiki/File:The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg", "reason": "亲密与选择的瞬间，呼应恋人牌中关系动态与价值协调的意象。"},
        {"artist": "Gustav Klimt", "title": "The Embrace", "year": 1905, "url": "https://commons.wikimedia.org/wiki/File:Gustav_Klimt_014.jpg", "reason": "联结与选择的张力，呼应恋人牌的价值抉择。"},
    ],
    "战车": [
        {"artist": "Eugène Delacroix", "title": "Liberty Leading the People", "year": 1830, "url": "https://commons.wikimedia.org/wiki/File:Eug%C3%A8ne_Delacroix_-_La_libert%C3%A9_guidant_le_peuple.jpg", "reason": "意志与方向的统一，呼应战车牌中内在统一性决定前进的主题。"},
    ],
    "力量": [
        {"artist": "Édouard Manet", "title": "The Rest", "year": 1870, "url": "https://www.artic.edu/artworks/20684", "reason": "温和的休憩姿态，呼应力量牌中共情理解化解紧张的意象。"},
    ],
    "隐士": [
        {"artist": "Caspar David Friedrich", "title": "Moonrise over the Sea", "year": 1822, "url": "https://commons.wikimedia.org/wiki/File:Caspar_David_Friedrich_-_Moonrise_over_the_Sea_-_Google_Art_Project.jpg", "reason": "独处与内省的氛围，呼应隐士牌中向内探寻、智慧追寻的意象。"},
    ],
    "命运之轮": [
        {"artist": "Vincent van Gogh", "title": "The Starry Night", "year": 1889, "url": "https://commons.wikimedia.org/wiki/File:Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg", "reason": "流转与变化的星空，呼应命运之轮中周期接纳与动态过程的意象。"},
    ],
    "正义": [
        {"artist": "Raphael", "title": "The School of Athens", "year": 1511, "url": "https://commons.wikimedia.org/wiki/File:Sanzio_01.jpg", "reason": "权衡与理性的秩序，呼应正义牌中多重因素平衡的主题。"},
    ],
    "倒吊人": [
        {"artist": "Édouard Manet", "title": "The Rest", "year": 1870, "url": "https://www.artic.edu/artworks/20684", "reason": "休憩与视角转换的姿态，呼应倒吊人牌中主动暂停、意义重构的意象。"},
    ],
    "死神": [
        {"artist": "Winslow Homer", "title": "The Gulf Stream", "year": 1899, "url": "https://www.metmuseum.org/art/collection/search/11122", "reason": "人与海浪的张力与转化感，呼应死神牌中释放旧模式、迎接自然转化的主题。"},
    ],
    "节制": [
        {"artist": "Claude Monet", "title": "Water Lilies", "year": 1906, "url": "https://www.artic.edu/artworks/16568", "reason": "对立元素的调和与流动，呼应节制牌中情绪调节、对立融合的意象。"},
    ],
    "恶魔": [
        {"artist": "Hieronymus Bosch", "title": "The Garden of Earthly Delights", "year": 1510, "url": "https://commons.wikimedia.org/wiki/File:The_Garden_of_Earthly_Delights_by_Bosch_High_Resolution.jpg", "reason": "欲望与束缚的隐喻，呼应恶魔牌中审视束缚感、认知局限的主题。"},
    ],
    "高塔": [
        {"artist": "J.M.W. Turner", "title": "The Burning of the Houses of Lords and Commons", "year": 1834, "url": "https://www.artic.edu/artworks/61925", "reason": "认知重构与虚假安全感瓦解的意象，呼应高塔牌的主题。"},
    ],
    "星星": [
        {"artist": "Vincent van Gogh", "title": "Starry Night Over the Rhône", "year": 1888, "url": "https://commons.wikimedia.org/wiki/File:Van_Gogh_-_Starry_Night_Over_the_Rhone.jpg", "reason": "希望与内在指引的星光，呼应星星牌中灵感连接、内在指引的意象。"},
    ],
    "月亮": [
        {"artist": "Claude Monet", "title": "Impression, Sunrise", "year": 1872, "url": "https://commons.wikimedia.org/wiki/File:Claude_Monet,_Impression,_soleil_levant.jpg", "reason": "模糊与不确定的光影，呼应月亮牌中潜意识材料浮现、不确定性接纳的主题。"},
    ],
    "太阳": [
        {"artist": "Claude Monet", "title": "Water Lilies", "year": 1906, "url": "https://www.artic.edu/artworks/16568", "reason": "清晰与愉悦的光影，呼应太阳牌中自我肯定、真实愉悦的意象。"},
    ],
    "审判": [
        {"artist": "Michelangelo", "title": "The Creation of Adam", "year": 1512, "url": "https://commons.wikimedia.org/wiki/File:Michelangelo_-_Creation_of_Adam_(cropped).jpg", "reason": "内在召唤与自我澄清的意象，呼应审判牌的主题。"},
    ],
    "世界": [
        {"artist": "Claude Monet", "title": "Water Lilies", "year": 1906, "url": "https://www.artic.edu/artworks/16568", "reason": "圆满与整合的流动感，呼应世界牌中周期完成、整体感的意象。"},
    ],
}

# 小阿卡纳/宫廷牌：按花色分配扩展池（每花色 4–5 张，随机选）
ARTWORK_BY_SUIT = (
    [  # 权杖
        {"artist": "Claude Monet", "title": "Water Lilies", "year": 1906, "url": "https://www.artic.edu/artworks/16568", "reason": "莫奈睡莲的静谧与流动，呼应照见当下的主题。"},
        {"artist": "Vincent van Gogh", "title": "Sunflowers", "year": 1888, "url": "https://www.metmuseum.org/art/collection/search/436524", "reason": "向日葵的活力与热情，呼应权杖组的行动能量。"},
        {"artist": "J.M.W. Turner", "title": "The Burning of the Houses of Lords and Commons", "year": 1834, "url": "https://www.artic.edu/artworks/61925", "reason": "火焰与动势，呼应权杖的火元素意象。"},
        {"artist": "Eugène Delacroix", "title": "Tiger Hunt", "year": 1854, "url": "https://commons.wikimedia.org/wiki/File:Eug%C3%A8ne_Delacroix_-_Tiger_Hunt_-_WGA6171.jpg", "reason": "活力与创造冲动，呼应权杖的动能。"},
    ],
    [  # 圣杯
        {"artist": "Vincent van Gogh", "title": "Starry Night Over the Rhône", "year": 1888, "url": "https://commons.wikimedia.org/wiki/File:Van_Gogh_-_Starry_Night_Over_the_Rhone.jpg", "reason": "星光与水面，呼应内在情感的流动与映照。"},
        {"artist": "Claude Monet", "title": "Water Lilies", "year": 1906, "url": "https://www.artic.edu/artworks/16568", "reason": "水面的静谧与情感深度，呼应圣杯组的水元素意象。"},
        {"artist": "Johannes Vermeer", "title": "Girl with a Pearl Earring", "year": 1665, "url": "https://commons.wikimedia.org/wiki/File:Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_1665.jpg", "reason": "内敛的情感与联结，呼应圣杯的滋养感。"},
        {"artist": "Pierre-Auguste Renoir", "title": "Luncheon of the Boating Party", "year": 1881, "url": "https://www.phillipscollection.org/collection/luncheon-boating-party", "reason": "欢聚与情感的共享，呼应圣杯的联结意象。"},
    ],
    [  # 宝剑
        {"artist": "Johannes Vermeer", "title": "Girl with a Pearl Earring", "year": 1665, "url": "https://commons.wikimedia.org/wiki/File:Johannes_Vermeer_-_Girl_with_a_Pearl_Earring_-_1665.jpg", "reason": "静默与内省，呼应思维与真相的沉淀。"},
        {"artist": "Caspar David Friedrich", "title": "Wanderer above the Sea of Fog", "year": 1818, "url": "https://commons.wikimedia.org/wiki/File:Caspar_David_Friedrich_-_Wanderer_above_the_sea_of_fog.jpg", "reason": "清晰的目光与理性的俯瞰，呼应宝剑的思维穿透力。"},
        {"artist": "Rembrandt", "title": "The Philosopher in Meditation", "year": 1632, "url": "https://commons.wikimedia.org/wiki/File:Rembrandt_-_The_Philosopher_in_Meditation.jpg", "reason": "沉思与智慧的寻求，呼应宝剑的心智意象。"},
        {"artist": "Raphael", "title": "The School of Athens", "year": 1511, "url": "https://commons.wikimedia.org/wiki/File:Sanzio_01.jpg", "reason": "理性与知识的秩序，呼应宝剑的真相辨识。"},
    ],
    [  # 星币
        {"artist": "Winslow Homer", "title": "The Gulf Stream", "year": 1899, "url": "https://www.metmuseum.org/art/collection/search/11122", "reason": "现实与身体的张力，呼应物质与根基的意象。"},
        {"artist": "Jean-François Millet", "title": "The Gleaners", "year": 1857, "url": "https://commons.wikimedia.org/wiki/File:Jean-Fran%C3%A7ois_Millet_-_Gleaners_-_Google_Art_Project.jpg", "reason": "劳作与收获，呼应星币组的物质与根基。"},
        {"artist": "Vincent van Gogh", "title": "The Potato Eaters", "year": 1885, "url": "https://commons.wikimedia.org/wiki/File:Van_Gogh_-_Die_Kartoffelesser_04240.jpg", "reason": "朴实与现实，呼应星币的稳固与踏实。"},
        {"artist": "Claude Monet", "title": "Poppy Field", "year": 1873, "url": "https://commons.wikimedia.org/wiki/File:Claude_Monet_-_Poppy_Field_-_Google_Art_Project.jpg", "reason": "自然与丰饶，呼应星币的收获意象。"},
    ],
)
SUIT_ORDER = ("权杖", "圣杯", "宝剑", "星币")


def _keywords_to_search_terms(card_keywords: str, base: str) -> list[str]:
    """从逻辑映射关键词 + 牌面基础名生成 Met API 可用的英文搜索词。"""
    terms: list[str] = []
    kw_parts = [p.strip() for p in (card_keywords or "").replace("、", ",").split(",") if p.strip()]
    for kw in kw_parts[:4]:  # 取前 4 个关键词
        if kw in KEYWORD_ZH_TO_EN:
            terms.append(KEYWORD_ZH_TO_EN[kw])
    for theme, en_terms in THEME_SEARCH_TERMS.items():
        if theme in base:
            terms.extend(en_terms[:2])
            break
    for suit, en_terms in SUIT_SEARCH_TERMS.items():
        if base.startswith(suit):
            terms.extend(en_terms[:2])
            break
    return list(dict.fromkeys(terms))[:3]  # 去重，最多 3 个


def _fetch_artwork_from_met(search_term: str, timeout: int = 8) -> dict | None:
    """从 Met Museum API 按关键词搜索，返回随机一件公有领域作品。"""
    if not requests or not search_term:
        return None
    try:
        r = requests.get(
            "https://collectionapi.metmuseum.org/public/collection/v1/search",
            params={"q": search_term, "hasImages": "true"},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        ids = data.get("objectIDs") or []
        if not ids:
            return None
        # 随机选一件，最多尝试 5 次以找到有图且公有的
        random.shuffle(ids)
        for oid in ids[:10]:
            obj_r = requests.get(
                f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}",
                timeout=timeout,
            )
            if not obj_r.ok:
                continue
            obj = obj_r.json()
            if not obj.get("isPublicDomain") or not obj.get("primaryImage"):
                continue
            title = obj.get("title") or "Untitled"
            artist = obj.get("artistDisplayName") or "Unknown"
            year = obj.get("objectDate") or obj.get("objectEndDate") or ""
            url = obj.get("objectURL") or f"https://www.metmuseum.org/art/collection/search/{oid}"
            return {
                "artist": artist,
                "title": title,
                "year": str(year)[:4] if year else "",
                "url": url,
                "reason": f"大都会博物馆藏品，与「{search_term}」相关。",
            }
        return None
    except Exception:
        return None


def _pick_from_static_pool(theme: str | None, suit: str | None) -> dict:
    """从扩展静态池中随机选取一件作品。"""
    if theme and theme in ARTWORK_BY_MAJOR_THEME:
        pool = ARTWORK_BY_MAJOR_THEME[theme]
        return random.choice(pool)
    if suit:
        for i, s in enumerate(SUIT_ORDER):
            if suit.startswith(s):
                return random.choice(ARTWORK_BY_SUIT[i])
    return random.choice(ARTWORK_BY_SUIT[0])


def match_artwork(
    card_name: str,
    base_meaning: str,
    card_data: dict,
    card_keywords: dict[str, str] | None = None,
) -> dict:
    """
    板块 B：匹配意境契合的艺术作品。
    1. 若牌在 card_data 中且含 artwork，直接返回。
    2. 小阿卡纳：优先使用 ARTWORK_BY_MINOR_CARD 中该牌专属作品（正位/逆位分别匹配）。
    3. 否则尝试 Met Museum API 实时搜索（用牌意关键词转译的英文词）。
    4. 失败则从花色兜底池（每花色 4 张）随机选取。
    """
    base = _base_card_name(card_name)
    data = card_data.get(card_name) or card_data.get(base)
    if data and data.get("artwork"):
        aw = data["artwork"]
        if isinstance(aw, list):
            return random.choice(aw)
        return aw

    # 小阿卡纳：每张牌（含逆位）有专属作品
    if card_name in ARTWORK_BY_MINOR_CARD:
        return ARTWORK_BY_MINOR_CARD[card_name]

    # Met API 实时搜索（仅当无专属作品时尝试，如大阿卡纳）
    kw_str = (card_keywords or {}).get(card_name) or (card_keywords or {}).get(base)
    terms = _keywords_to_search_terms(kw_str or "", base)
    if terms and requests:
        chosen = random.choice(terms)
        met_aw = _fetch_artwork_from_met(chosen)
        if met_aw:
            return met_aw

    # 花色兜底池：仅 Met 失败时使用
    theme = None
    for t in THEME_SEARCH_TERMS:
        if t in card_name or t in base_meaning:
            theme = t
            break
    suit = None
    for s in SUIT_ORDER:
        if base.startswith(s):
            suit = s
            break
    return _pick_from_static_pool(theme, suit or base)
