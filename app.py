# aujourd'hui — 今日镜像
# 核心数据与叙事逻辑，供 FastAPI（backend_api.py）引用。Streamlit 前端已彻底移除。

import hashlib
import random
import re
from pathlib import Path

from draw_logic import match_artwork as match_artwork_for_card

# ============ 维特塔罗 1909 牌面图 · Wikipedia Commons ============
# 使用 upload.wikimedia.org 直链，避免 Special:FilePath 重定向在某些环境下导致图片不加载
UPLOAD_COMMONS_BASE = "https://upload.wikimedia.org/wikipedia/commons"


def _commons_direct_url(filename: str) -> str:
    """按 Commons 存储规则生成直链：/hash[0]/hash[0:2]/filename（MD5 对文件名计算）。"""
    fn = filename.replace(" ", "_")
    h = hashlib.md5(fn.encode("utf-8")).hexdigest()
    return f"{UPLOAD_COMMONS_BASE}/{h[0]}/{h[0:2]}/{filename}"

# 大阿卡纳（22张）-> Commons 文件名
MAJOR_ARCANA_IMAGES = {
    "0 愚人": "RWS_Tarot_00_Fool.jpg",
    "I 魔术师": "RWS_Tarot_01_Magician.jpg",
    "II 女祭司": "RWS_Tarot_02_High_Priestess.jpg",
    "III 皇后": "RWS_Tarot_03_Empress.jpg",
    "IV 皇帝": "RWS_Tarot_04_Emperor.jpg",
    "V 教皇": "RWS_Tarot_05_Hierophant.jpg",
    "VI 恋人": "RWS_Tarot_06_Lovers.jpg",
    "VII 战车": "RWS_Tarot_07_Chariot.jpg",
    "VIII 力量": "RWS_Tarot_08_Strength.jpg",
    "IX 隐士": "RWS_Tarot_09_Hermit.jpg",
    "X 命运之轮": "RWS_Tarot_10_Wheel_of_Fortune.jpg",
    "XI 正义": "RWS_Tarot_11_Justice.jpg",
    "XII 倒吊人": "RWS_Tarot_12_Hanged_Man.jpg",
    "XIII 死神": "RWS_Tarot_13_Death.jpg",
    "XIV 节制": "RWS_Tarot_14_Temperance.jpg",
    "XV 恶魔": "RWS_Tarot_15_Devil.jpg",
    "XVI 高塔": "RWS_Tarot_16_Tower.jpg",
    "XVII 星星": "RWS_Tarot_17_Star.jpg",
    "XVIII 月亮": "RWS_Tarot_18_Moon.jpg",
    "XIX 太阳": "RWS_Tarot_19_Sun.jpg",
    "XX 审判": "RWS_Tarot_20_Judgement.jpg",
    "XXI 世界": "RWS_Tarot_21_World.jpg",
}

# 小阿卡纳：权杖 Wands / 圣杯 Cups / 宝剑 Swords / 星币 Pents
_NUM_MAP = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
_SUIT_MAP = {"权杖": "Wands", "圣杯": "Cups", "宝剑": "Swords", "星币": "Pents"}
_COURT_MAP = {"侍从": 11, "骑士": 12, "皇后": 13, "国王": 14}


def _base_card_name(card_name: str) -> str:
    """返回牌面基础名（去除「· 逆位」），用于查图。"""
    if " · 逆位" in card_name:
        return card_name.replace(" · 逆位", "").strip()
    return card_name


def get_tarot_image_url(card_name: str) -> str | None:
    """
    通过 Wikipedia Commons 直链获取 1909 版维特塔罗牌面图 URL。
    逆位牌使用同一张图（由 render 层做上下翻转）。
    大阿卡纳支持带罗马数字的键（如 X 命运之轮）或纯中文名（命运之轮）查找。
    """
    base = _base_card_name(card_name)
    filename: str | None = None
    # 大阿卡纳：先精确匹配，再按「以 base 结尾」匹配
    if base in MAJOR_ARCANA_IMAGES:
        filename = MAJOR_ARCANA_IMAGES[base]
    if not filename:
        for key, fn in MAJOR_ARCANA_IMAGES.items():
            if key.endswith(base) or key == base.strip():
                filename = fn
                break
    if filename:
        return _commons_direct_url(filename)

    # 小阿卡纳：权杖五、圣杯三、宝剑十、星币四 等（Commons 小牌文件名如 Wands05.jpg）
    for suit_cn, suit_en in _SUIT_MAP.items():
        if not base.startswith(suit_cn):
            continue
        rest = base[len(suit_cn):].strip()
        if rest == "Ace":
            filename = f"{suit_en}01.jpg"
        else:
            for num_cn, num in _NUM_MAP.items():
                if rest == num_cn:
                    filename = f"{suit_en}{num:02d}.jpg"
                    break
            else:
                for court_cn, idx in _COURT_MAP.items():
                    if rest == court_cn:
                        filename = f"{suit_en}{idx:02d}.jpg"
                        break
                else:
                    continue
        if filename:
            return _commons_direct_url(filename)

    return None


# ============ 产品宪章常量 ============
DISCLAIMER = "本服务仅供美学启发与心理平衡，不具临床诊断价值。你对自己的生活拥有最终决定权。"

# 附录 1：厌女词汇（生成前自检，发现则重新生成）
MISOGYNY_BLOCKLIST = [
    "荡妇", "荡妇羞辱", "鸡", "妓女", "婊子", "破鞋", "不干不净", "公交车",
    "胸大无脑", "花瓶", "花瓶女", "妇人之仁", "头发长", "见识短",
    "黄脸婆", "生殖机器", "家庭主妇", "扶弟魔", "吸血", "女强人",
    "歇斯底里", "撒泼", "疯女人", "作女", "矫情", "戏精",
    "剩女", "老女人", "豆腐渣", "恐龙", "丑女",
    "女拳", "拳师", "你一个女人", "要不是为了你",
]


# ============ 牌义与叙事库 ============
CARD_DATA = {
    "0 愚人": {
        "raw": "拥抱未知，信任过程。",
        "narratives": [
            "此刻，一种视角——你或许正站在边缘。未知不是威胁，而是未被命名的可能性。信任这一步，比急着看清终点更重要。牌面提醒你：愚人之所以敢迈出悬崖，是因为他相信脚下的风。正如拉康所说，主体通过镜像获得统一感；此刻的你不必等待一个完整的答案，迈出这一步本身，就是在与未命名的可能性对话。这是一种可能性视角，你对自己的生活拥有最终决定权。",
            "此刻你或许感到不确定。牌面在说：未知里藏着另一种秩序。不必用过去的经验丈量未来的路，信任此刻的直觉，比任何规划都更贴近你自己。愚人牌的轻盈来自于对「过程」的信任——他手中的包袱很轻，因为他知道真正重要的不是背负多少，而是是否愿意踏出那一步。今日的镜像邀请你照见这份不确定中的可能性，而非焦虑。",
        ],
        "serene": "身体有它自己的节律。此刻不必追赶效率，不必证明什么。牌面在说：愚人的轻盈，来自于允许自己暂停。接纳这份不确定，它正在为新的可能性腾出空间。当外界催促你「应该怎样」时，愚人提醒你：有些答案只有在停顿中才会浮现。尊重身体的节奏，停顿与等待，都是对自我的一种照护。今日镜像仅作为美学启发，你对自己的生活拥有最终决定权。",
        "artwork": {"artist": "Claude Monet", "title": "Wheatstacks, Snow Effect, Morning", "year": 1891, "url": "https://www.artic.edu/artworks/64818", "reason": "雪后麦垛的留白与朦胧，呼应愚人牌中未被命名的可能性与信任过程的轻盈感。"},
    },
    "I 魔术师": {
        "raw": "资源整合，开启表达。",
        "narratives": [
            "你手中已有足够。此刻的停滞，可能只是在等待一个开启的姿势。牌面提醒你：魔术师桌上的四元素早已齐备，缺的只是你愿意伸出手的那一瞬间。荣格将塔罗视为集体潜意识的投射——魔术师牌象征的是「整合」的原型：内在的资源、外在的机会，都在等待一个连接的姿态。不必追求完美，表达不需要等到一切就绪；此刻的你，比你以为的更有力量去连接内在与外在。这是一种可能性视角，你对自己的生活拥有最终决定权。",
            "资源一直都在，只是尚未被整合。牌面在说：表达不需要完美，只需要开始。魔术师的从容来自于他相信「桌上已有足够」——四元素的齐备，不是偶然，而是提醒你：开启与整合，往往只差一个决定。今日的镜像邀请你照见这种「已有足够」的丰盛感，而非匮乏。温柔地对待自己，你对自己的生活拥有最终决定权。",
        ],
        "serene": "身体有它自己的节律。不必急于展现，不必证明价值。牌面在说：魔术师的从容，来自于接纳当下的不完美。停顿不是软弱，而是为下一次开启积蓄能量。当外界期待你「有所作为」时，魔术师提醒你：整合需要时间，开启需要节奏。尊重身体的节律，不必追赶效率。今日镜像仅作为美学启发，你对自己的生活拥有最终决定权。",
        "artwork": {"artist": "Pierre-Auguste Renoir", "title": "Two Sisters (On the Terrace)", "year": 1881, "url": "https://www.artic.edu/artworks/14655", "reason": "姐妹俩坐在露台的静谧瞬间，呼应魔术师牌中资源齐备、从容开启的表达姿态。"},
    },
    "XII 倒吊人": {
        "raw": "主动暂停，视角转换。",
        "narratives": [
            "暂停不是失败。换一个角度，看见的会是另一种风景。牌面提醒你：倒吊人主动选择了悬挂，因为他知道，有些答案只有在颠倒的视角里才会显现。正如荣格所言，阴影与光明的整合需要视角的转换——倒吊人的智慧，恰恰在于他愿意「停下来」、愿意「颠倒」。当你暂时放下「应该怎样」，新的可能性才会浮出水面。接纳这份暂停，它正在为你铺路。这是一种可能性视角，你对自己的生活拥有最终决定权。",
            "此刻或许感到卡住。牌面在说：停滞有时是礼物。倒吊人牌象征的是主动的暂停——不是被动等待，而是有意选择另一种观看方式。当外界催促你「快点行动」时，牌面邀请你照见：有些问题，恰恰需要在静止中才能看清。温柔地接纳这份卡住，它可能是转化前的沉淀。你对自己的生活拥有最终决定权。",
        ],
        "serene": "身体有它自己的节律。牌面在说：倒吊人的智慧，来自于允许自己停顿。不必与外界节奏同步，此刻的休息，正是为了更清晰地看见自己。当身体发出「需要暂停」的信号时，倒吊人提醒你：这不是软弱，而是一种更深的智慧。尊重节律，接纳停顿。今日镜像仅作为美学启发，你对自己的生活拥有最终决定权。",
        "artwork": {"artist": "Édouard Manet", "title": "The Rest", "year": 1870, "url": "https://www.artic.edu/artworks/20684", "reason": "画中人物的休憩姿态，与倒吊人牌主动暂停、视角转换的意象形成呼应。"},
    },
    "XIII 死神": {
        "raw": "释放旧模式，自然转化。",
        "narratives": [
            "某些东西正在离开。这不是终结，而是为新的形态腾出空间。牌面提醒你：死神牌无关灾祸，它说的是告别与转化。旧的自我、旧的关系模式，正在以一种你或许尚未命名的方式松动。荣格将转化视为心理发展的必然阶段——死神牌象征的是「释放」的原型，而非生命的终结。转化往往以「失去」的面貌出现，但空间本身，就是一种新的可能性。接纳这种松动，不必急着填补空白。这是一种可能性视角，你对自己的生活拥有最终决定权。",
            "此刻或许感到某种结束。牌面在说：转化往往以「失去」的面貌出现。死神牌聚焦的是心理转变——释放旧模式、为新阶段腾出空间。当某些东西正在离开时，牌面邀请你照见：这不是失败，而是周期的一部分。温柔地接纳这种松动，空间本身，就是一种新的可能性。你对自己的生活拥有最终决定权。",
        ],
        "serene": "身体有它自己的节律。牌面在说：转化不需要用力推动。接纳离开的，接纳空出来的部分。停顿与放手，都是对身体节律的尊重。当身体经历周期性的变化时，死神牌提醒你：转化是自然的，不必急于「重建」。尊重节律，接纳空白。今日镜像仅作为美学启发，你对自己的生活拥有最终决定权。",
        "artwork": {"artist": "Winslow Homer", "title": "The Gulf Stream", "year": 1899, "url": "https://www.metmuseum.org/art/collection/search/11122", "reason": "人与海浪之间的张力与转化感，呼应死神牌中释放旧模式、迎接自然转化的主题。"},
    },
    "XVI 高塔": {
        "raw": "认知重构，打破虚假安全感。",
        "narratives": [
            "坚固有时是假象。坍塌之后，视线反而清晰。牌面提醒你：高塔牌说的不是灾难，而是那些你以为「必须如此」的认知正在松动。崩塌之后，才能看见更真实的地基。荣格将高塔视为「虚假安全感」的瓦解——当某些坚固的信念被撼动时，不适是正常的，但也是转化的前奏。虚假的安全感比真实的不确定更消耗人；允许某些结构倒塌，是为了让更贴近自己的东西生长出来。这是一种可能性视角，你对自己的生活拥有最终决定权。",
            "此刻或许感到震动。牌面在说：虚假的安全感比真实的不确定更消耗人。高塔牌聚焦的是认知重构——打破那些「必须如此」的假象。当某些结构正在松动时，牌面邀请你照见：这不是灾难，而是为更真实的东西腾出空间。温柔地接纳这份震动，重构不需要在一天内完成。你对自己的生活拥有最终决定权。",
        ],
        "serene": "身体有它自己的节律。牌面在说：重构不需要在一天内完成。接纳此刻的震荡，不必急于重建。停顿与等待，都是对自我的一种照护。当外界期待你「立刻振作」时，高塔牌提醒你：尊重节律，允许自己有时间整合。今日镜像仅作为美学启发，你对自己的生活拥有最终决定权。",
        "artwork": {"artist": "J.M.W. Turner", "title": "The Burning of the Houses of Lords and Commons", "year": 1834, "url": "https://www.artic.edu/artworks/61925", "reason": "火焰与建筑崩塌中的光与烟，呼应高塔牌认知重构、打破虚假安全感的意象。"},
    },
}


def load_cards_from_logic_mapping() -> tuple[list[str], dict, dict]:
    """
    从 docs/content/logic_mapping_2.md 解析牌库、基础牌义与关键词。
    返回 (card_names, card_meanings, card_keywords)。
    """
    mapping_path = Path(__file__).parent / "docs" / "content" / "logic_mapping_2.md"
    card_names: list[str] = []
    card_meanings: dict[str, str] = {}
    card_keywords: dict[str, str] = {}

    if not mapping_path.exists():
        card_names = list(MAJOR_ARCANA_IMAGES.keys())
        return card_names, {k: CARD_DATA.get(k, {}).get("raw", "") for k in card_names}, {}

    text = mapping_path.read_text(encoding="utf-8")

    # 解析 ### I 魔术师 等标题，下一行 - **今日镜像**：xxx、**关键词**：xxx
    header_pattern = re.compile(r"^### (.+)$", re.MULTILINE)
    mirror_pattern = re.compile(r"\*\*今日镜像\*\*[：:]\s*([^\n]+)")
    keyword_pattern = re.compile(r"\*\*关键词\*\*[：:]\s*([^\n]+)")

    for match in header_pattern.finditer(text):
        raw_name = match.group(1).strip()
        # 跳过非牌名行
        if any(kw in raw_name for kw in ["设计", "原则", "大阿卡纳", "小阿卡纳", "数字", "权杖组", "圣杯组", "宝剑组", "星币组", "宫廷", "示例", "统一"]):
            continue
        if any(kw in raw_name for kw in ["核心", "隐喻", "今日视角", "特殊", "危机", "免责", "量子", "系统"]):
            continue
        if len(raw_name) > 30:
            continue

        # 逆位补丁：### 0. 愚人（逆位）、### I. 魔术师（逆位）-> 存为 "0 愚人 · 逆位"
        is_reversed = "（逆位）" in raw_name
        if is_reversed:
            base = raw_name.replace("（逆位）", "").strip().replace(". ", " ")
            name = base + " · 逆位"
        else:
            # 正位：### I 魔术师、### 0 愚人 -> 保持；### 0. 愚人 -> 转为 0 愚人
            name = raw_name.replace(". ", " ").strip()

        # 查找该牌下的今日镜像与关键词
        start = match.end()
        segment = text[start : start + 800]
        mirror_match = mirror_pattern.search(segment)
        meaning = mirror_match.group(1).strip() if mirror_match else ""
        kw_match = keyword_pattern.search(segment)
        keywords = kw_match.group(1).strip() if kw_match else ""

        # 逆位只存牌义，不加入 card_names（抽牌从正位牌池抽，50% 概率标记为逆位）
        if is_reversed:
            if meaning and base:
                card_meanings[name] = meaning
            if keywords and base:
                card_keywords[name] = keywords
            continue

        if name and (get_tarot_image_url(name) or name in CARD_DATA):
            if name not in card_names:
                card_names.append(name)
            if meaning:
                card_meanings[name] = meaning
            if keywords:
                card_keywords[name] = keywords

    # 解析小阿卡纳示例：- **权杖五**：xxx（仅权杖/圣杯/宝剑/星币）
    bullet_pattern = re.compile(r"-\s*\*\*([^*]+)\*\*[：:]\s*([^\n]+)")
    for match in bullet_pattern.finditer(text):
        name = match.group(1).strip()
        meaning = match.group(2).strip()
        if any(name.startswith(s) for s in ["权杖", "圣杯", "宝剑", "星币"]) and get_tarot_image_url(name) and name not in card_names:
            card_names.append(name)
            card_meanings[name] = meaning

    # 解析表格行：| **权杖Ace** | 今日镜像... | 关键词 |（小阿卡纳与宫廷牌正/逆位）
    table_row_pattern = re.compile(r"\|\s*\*\*([^*|]+)\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|")
    for match in table_row_pattern.finditer(text):
        raw_name = match.group(1).strip()
        meaning = match.group(2).strip()
        keywords = match.group(3).strip() if match.lastindex >= 3 else ""
        if not meaning or len(meaning) < 5:
            continue
        is_reversed_row = "逆位" in raw_name
        if is_reversed_row:
            base_name = raw_name.replace("逆位", "").strip()
            name = base_name + " · 逆位"
            if get_tarot_image_url(base_name):
                card_meanings[name] = meaning
                if keywords:
                    card_keywords[name] = keywords
            continue
        name = raw_name
        if any(name.startswith(s) for s in ["权杖", "圣杯", "宝剑", "星币"]) and get_tarot_image_url(name):
            if name not in card_names:
                card_names.append(name)
            card_meanings[name] = meaning
            if keywords:
                card_keywords[name] = keywords

    # 解析宫廷牌逆位网格表：| 牌组 | 侍从 逆位 | 骑士 逆位 | 皇后 逆位 | 国王 逆位 | 下接 | **权杖** | cell | cell | cell | cell |
    court_roles = ["侍从", "骑士", "皇后", "国王"]
    court_reversed_marker = "### 👑 宫廷牌逆位"
    if court_reversed_marker in text:
        block = text.split(court_reversed_marker)[1].split("## ")[0]
        for line in block.splitlines():
            line = line.strip()
            if not line.startswith("| **") or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 6:
                continue
            suit_raw = parts[1].strip().strip("*").strip()
            if suit_raw in ("权杖", "圣杯", "宝剑", "星币") and not suit_raw.startswith(":"):
                for i, role in enumerate(court_roles):
                    cell_idx = i + 2
                    if cell_idx < len(parts):
                        meaning = parts[cell_idx].strip()
                        if meaning and len(meaning) > 3:
                            card_key = f"{suit_raw}{role} · 逆位"
                            card_meanings[card_key] = meaning

    # 确保 16 张宫廷牌在牌池中（表格为网格格式，可能未解析到）
    court_cards = [
        "权杖侍从", "权杖骑士", "权杖皇后", "权杖国王",
        "圣杯侍从", "圣杯骑士", "圣杯皇后", "圣杯国王",
        "宝剑侍从", "宝剑骑士", "宝剑皇后", "宝剑国王",
        "星币侍从", "星币骑士", "星币皇后", "星币国王",
    ]
    for name in court_cards:
        if name not in card_names and get_tarot_image_url(name):
            card_names.append(name)
            if name not in card_meanings:
                card_meanings[name] = "此刻，牌面邀请你照见当下的自己。一种可能性视角，你对自己的生活拥有最终决定权。"

    # 若解析结果为空，使用大阿卡纳 + 小阿卡纳示例
    if not card_names:
        card_names = list(MAJOR_ARCANA_IMAGES.keys()) + [
            "权杖五", "权杖十", "圣杯三", "圣杯九", "宝剑三", "宝剑十", "星币四", "星币九",
        ] + court_cards
        for k in card_names:
            if k not in card_meanings:
                card_meanings[k] = CARD_DATA.get(k, {}).get("raw", "此刻，牌面邀请你照见当下的自己。")

    return card_names, card_meanings, card_keywords


def contains_misogyny(text: str) -> bool:
    """检测文案是否包含附录 1 厌女词汇。"""
    t = text.lower()
    for w in MISOGYNY_BLOCKLIST:
        if w in t:
            return True
    return False


def _golden_opening() -> str:
    """板块 A · 极简锚定（迁移后仅保留 main body，无用户变量）。"""
    return "此刻，"


def _psychology_body(card_name: str, base_meaning: str) -> str:
    """
    板块 A · 正文（产品宪章 §3）：基于塔罗牌意 + 拉康/荣格镜像解读。
    语感：温柔、克制、法式疏离美感；禁令：无迷信宿命论、无医疗/财务/法律建议。
    无字数限制；非 CARD_DATA 牌 = logic_mapping 完整牌义 + 镜像收束句。
    """
    base = _base_card_name(card_name)
    data = CARD_DATA.get(card_name) or CARD_DATA.get(base)
    if data:
        narratives = data.get("narratives", [base_meaning])
        return random.choice(narratives)

    # 非 CARD_DATA 牌（小阿卡纳）：以牌意为主体，短收束句收尾（产品宪章 §3 小阿卡纳扩写与滤镜）
    # 避免定型文过长，让 logic_mapping 的牌意真正触及用户
    meaning = (base_meaning or "").strip()
    close = "这是一种可能性视角，你对自己的生活拥有最终决定权。"
    return f"{meaning} {close}" if meaning else close


def generate_narrative(
    card_name: str,
    base_meaning: str,
    card_keywords: dict[str, str] | None = None,
) -> tuple[str, dict]:
    """
    《aujourd'hui》板块 A [当下叙事] + 板块 B [名画意境]（产品宪章 §3）
    迁移简化版：入参仅保留抽出的牌（牌名 + 牌义 + 关键词），无 period/weather/region/thought。
    """
    body = _psychology_body(card_name, base_meaning)
    opening = _golden_opening()
    narrative = opening + body

    # 产品宪章 §3 禁令 + 附录 1：厌女词汇严格禁止
    if contains_misogyny(narrative):
        narrative = "此刻，牌面邀请你照见当下的自己。这是一种可能性视角，温柔地接纳此刻的状态。你对自己的生活拥有最终决定权。"

    # 板块 B：名画意境匹配（见 draw_logic.match_artwork）
    artwork = match_artwork_for_card(card_name, base_meaning, CARD_DATA, card_keywords or {})

    return narrative, artwork

