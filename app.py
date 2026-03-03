# aujourd'hui — 今日镜像
# 基于《aujourd'hui》产品宪章 v1.1 · Streamlit

import base64
import hashlib
import streamlit as st
import random
import re
import time
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

from draw_logic import build_card_pool, draw_one_card, match_artwork as match_artwork_for_card

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


def _fetch_image_as_data_url(url: str, timeout: int = 10) -> str | None:
    """服务端拉取图片并转为 data URL，避免浏览器直连外部图床被拦截。"""
    if not url or not requests:
        return None
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        raw = r.content
        ct = r.headers.get("Content-Type", "").split(";")[0].strip() or "image/jpeg"
        b64 = base64.b64encode(raw).decode("ascii")
        return f"data:{ct};base64,{b64}"
    except Exception:
        return None


def _local_image_as_data_url(path: Path) -> str | None:
    """本地图片转为 data URL，用于内联样式或点击区域。"""
    if not path.exists():
        return None
    try:
        raw = path.read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    except Exception:
        return None


def render_tarot_image(card_name: str, alt: str = "塔罗牌面", reversed: bool = False):
    """
    渲染塔罗牌图片。优先用服务端拉取后以 data URL 内联展示，避免直连 Commons 不加载。
    逆位牌上下翻转（scaleY(-1)），符合维特塔罗逆位视觉惯例。
    """
    url = get_tarot_image_url(card_name)
    flip = "transform: scaleY(-1);" if reversed else ""
    if not url:
        st.markdown(
            f'<div class="tarot-card-wrapper" style="min-height:180px;display:flex;align-items:center;justify-content:center;background:#f0eeeb;border-radius:12px;color:#6A6A7A;">{alt}</div>',
            unsafe_allow_html=True,
        )
        return
    # 服务端拉取后内联，避免浏览器直连外部图床失败
    data_url = _fetch_image_as_data_url(url)
    src = data_url if data_url else url
    st.markdown(
        f"""
        <div class="tarot-card-wrapper">
            <img src="{src}" alt="{alt}" class="tarot-card-image" style="{flip}" />
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    从 logic_mapping_2.md 解析牌库、基础牌义与关键词。
    返回 (card_names, card_meanings, card_keywords)。
    """
    mapping_path = Path(__file__).parent / "logic_mapping_2.md"
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


# 危机干预：检测严重负面心理倾向时触发的安全提示
CRISIS_TRIGGERS = ["自杀", "自伤", "重度抑郁", "创伤重现", "不想活了", "活着没意思"]

# 各地区心理援助热线（按国家/地区代码）
HELPLINE_BY_REGION = {
    "CN": {"name": "全国心理援助热线", "number": "400-161-9995", "hours": "24小时", "lang": "zh"},
    "HK": {"name": "香港撒玛利亚防止自杀会", "number": "+852 2389 2222", "hours": "24小时", "lang": "zh"},
    "TW": {"name": "台湾自杀防治协会", "number": "1925", "hours": "24小时", "lang": "zh"},
    "US": {"name": "National Suicide Prevention Lifeline", "number": "988", "hours": "24/7", "lang": "en"},
    "GB": {"name": "Samaritans", "number": "116 123", "hours": "24/7", "lang": "en"},
    "JP": {"name": "こころの健康相談統一ダイヤル", "number": "0570-064-556", "hours": "24时间", "lang": "ja"},
    "KR": {"name": "生命电话", "number": "1393", "hours": "24시간", "lang": "ko"},
    "AU": {"name": "Lifeline Australia", "number": "13 11 14", "hours": "24/7", "lang": "en"},
    "CA": {"name": "Canada Crisis Services", "number": "1-833-456-4566", "hours": "24/7", "lang": "en"},
    "SG": {"name": "Singapore Samaritans", "number": "1-767", "hours": "24小时", "lang": "zh"},
    "DEFAULT": {"name": "International Association for Suicide Prevention", "number": "https://www.iasp.info/resources/Crisis_Centres/", "hours": "", "lang": "en"},
}


def _get_user_region_for_helpline() -> str:
    """
    获取用户地区用于展示当地心理援助热线。
    优先尝试 IP 地理定位（需部署环境支持），否则使用侧边栏选择。
    """
    # 1. 尝试从 session_state 获取（由侧边栏选择或之前检测结果）
    region = st.session_state.get("helpline_region")
    if region and region != "auto":
        return region

    # 2. 尝试 IP 地理定位
    if "user_region_detected" not in st.session_state:
        client_ip = None
        if hasattr(st, "request") and st.request:
            headers = getattr(st.request, "headers", None) or {}
            forwarded = headers.get("X-Forwarded-For") or headers.get("X-Real-IP")
            if forwarded:
                client_ip = forwarded.split(",")[0].strip()
            elif hasattr(st.request, "remote_ip"):
                client_ip = st.request.remote_ip

        if client_ip and client_ip not in ("127.0.0.1", "::1") and requests:
            try:
                r = requests.get(
                    f"http://ip-api.com/json/{client_ip}?fields=countryCode",
                    timeout=2,
                )
                if r.ok:
                    data = r.json()
                    cc = data.get("countryCode", "")
                    if cc in HELPLINE_BY_REGION:
                        st.session_state["user_region_detected"] = cc
            except Exception:
                pass
        st.session_state.setdefault("user_region_detected", None)

    detected = st.session_state.get("user_region_detected")
    if detected:
        return detected

    return "CN"  # 默认中国大陆


def _get_crisis_response(region: str) -> str:
    """根据地区返回危机干预响应文案，含当地心理援助热线。"""
    info = HELPLINE_BY_REGION.get(region, HELPLINE_BY_REGION["DEFAULT"])
    if info.get("number", "").startswith("http"):
        return f"此刻你可能需要更专业的支持。可访问 {info['number']} 查找您所在地区的心理援助热线。你的感受值得被认真对待。"
    return f"此刻你可能需要更专业的支持。{info['name']}：{info['number']}（{info.get('hours','')}）。你的感受值得被认真对待。"


def _needs_crisis_intervention(thought: str) -> bool:
    """危机干预协议：检测输入中的危机关键词。"""
    t = thought.strip()
    if not t:
        return False
    return any(kw in t for kw in CRISIS_TRIGGERS)


def _golden_opening(mood: int, period_mode: bool, mbti: str | None = None, weather: str | None = None) -> str:
    """
    板块 A · 前 50 字（产品宪章 §3 关键细节）：通感锚定（光影、气味、身体感觉），
    呼应用户变量（天气/生理期），体现此时此刻唯一性。无字数上限。
    """
    if period_mode:
        return "身体有它自己的节律。此刻的光影、呼吸的深浅，都在邀请你放慢——"
    if mood <= -2:
        # 阴雨天 / 沉郁：光影暗淡、身体沉重感
        if weather and ("雨" in weather or "阴" in weather):
            return "此刻的光线有些沉，空气里带着湿意。你或许感到身体比往常更愿意停顿——"
        return "此刻的光影有些淡，身体或许比往常更愿意停顿。这种沉，不是失败——"
    if mood >= 2:
        # 晴朗 / 轻快：光影流动、身体轻盈
        if weather and ("晴" in weather or "阳" in weather):
            return "此刻的光线流动着，空气里有一种轻盈。你或许感到身体比往常更愿意伸展——"
        return "此刻的能量在流动，身体或许比往常更愿意伸展。这种轻，值得被照见——"
    # 中性：极简锚定，避免定型文过长（产品宪章 §3 小阿卡纳扩写：牌意为主体）
    if mbti and ("F" in mbti.upper() or "N" in mbti.upper()):
        return "此刻的光影在变化，你或许能感受到某种未被命名的情绪在流动——"
    if weather and weather != "—":
        return f"此刻的{weather}里，"
    return "此刻，"


def _psychology_body(card_name: str, base_meaning: str, period_mode: bool) -> str:
    """
    板块 A · 正文（产品宪章 §3）：基于塔罗牌意 + 拉康/荣格镜像解读。
    语感：温柔、克制、法式疏离美感；禁令：无迷信宿命论、无医疗/财务/法律建议。
    无字数限制；非 CARD_DATA 牌 = logic_mapping 完整牌义 + 镜像收束句。
    """
    base = _base_card_name(card_name)
    data = CARD_DATA.get(card_name) or CARD_DATA.get(base)
    if data and period_mode:
        return data.get("serene", base_meaning)
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
    mood: int,
    period_mode: bool,
    base_meaning: str,
    thought: str = "",
    mbti: str | None = None,
    weather: str | None = None,
    card_keywords: dict[str, str] | None = None,
) -> tuple[str, dict]:
    """
    《aujourd'hui》板块 A [当下叙事] + 板块 B [名画意境]（产品宪章 §3）

    - 板块 A：前 50 字通感锚定（_golden_opening）+ 牌意正文（_psychology_body）；无字数上限
    - 语感：温柔、克制、法式疏离；禁令：迷信宿命论、医疗/财务/法律建议、厌女词（附录 1）
    - 危机倾向时自动转为安抚 + 心理援助引导（宪章 §3 禁令 3）
    - 板块 B：名画匹配见 draw_logic.match_artwork
    """
    # 产品宪章 §3 禁令 3：严重负面心理危机 → 极度克制安抚 + 专业帮助引导
    if _needs_crisis_intervention(thought):
        region = _get_user_region_for_helpline()
        safe_narrative = f"{_golden_opening(mood, period_mode, mbti, weather)}{_get_crisis_response(region)}"
        return safe_narrative, match_artwork_for_card(card_name, base_meaning, CARD_DATA, card_keywords or {})

    # 正文：心理学化解读（我与他者、欲望与存在）
    body = _psychology_body(card_name, base_meaning, period_mode)

    # 黄金前 50 字：通感锚定（光影 / 气味 / 身体感觉），呼应用户变量
    # 生理期模式下的 serene 已内含「身体节律」锚定，不再重复
    opening = _golden_opening(mood, period_mode, mbti, weather)
    if period_mode and ("身体有它自己的节律" in body[:60] or "身体" in body[:60]):
        narrative = body
    else:
        narrative = opening + body

    # 产品宪章 §3 禁令 + 附录 1：厌女词汇严格禁止
    if contains_misogyny(narrative):
        narrative = "此刻，牌面邀请你照见当下的自己。这是一种可能性视角，温柔地接纳此刻的状态。你对自己的生活拥有最终决定权。"

    # 板块 B：名画意境匹配（见 draw_logic.match_artwork）
    artwork = match_artwork_for_card(card_name, base_meaning, CARD_DATA, card_keywords or {})

    return narrative, artwork


# ============ 页面渲染 ============
def inject_morandi_css():
    """注入莫兰迪粉紫渐变与留白感 CSS（产品宪章 视觉定义）。"""
    st.markdown(
        """
        <style>
        /* 主背景：莫兰迪粉到淡紫渐变 */
        .stApp {
            background: linear-gradient(135deg, #FADADD 0%, #E6E6FA 100%);
        }
        /* 质感：半透明遮罩，模拟微光/闪粉静态呼吸感 */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(circle at 20% 30%, rgba(255,230,240,0.4) 0%, transparent 50%),
                        radial-gradient(circle at 80% 70%, rgba(230,230,255,0.3) 0%, transparent 50%);
            pointer-events: none;
        }
        /* 留白感：增大内边距，降低认知负荷 */
        .main .block-container {
            padding: 4rem 3rem;
            max-width: 560px;
        }
        /* 文字颜色：深灰，非纯黑 */
        .stMarkdown, .stMarkdown p, .mirror-text {
            color: #4A4A4A !important;
        }
        .mirror-output {
            margin-top: 2rem;
            padding: 2rem;
            background: rgba(255,255,255,0.6);
            border-radius: 12px;
            color: #4A4A4A;
            font-size: 0.95rem;
            line-height: 1.8;
        }
        .card-name {
            font-weight: 300;
            letter-spacing: 0.15em;
            margin-bottom: 1rem;
            color: #5A4A6A;
        }
        .subtitle {
            font-weight: 300;
            letter-spacing: 0.25em;
            color: #6A6A7A;
            font-size: 0.8rem;
        }
        .disclaimer {
            margin-top: 2rem;
            padding-top: 1.5rem;
            font-size: 0.75rem;
            color: #8A8A9A;
            border-top: 1px solid rgba(0,0,0,0.06);
        }
        /* 塔罗牌图片 · 莫兰迪风格 */
        .tarot-card-wrapper {
            margin: 1rem 0;
            text-align: center;
        }
        .tarot-card-image {
            max-width: 200px;
            border-radius: 8px;
            opacity: 0.8;
            filter: sepia(0.2);
        }
        /* 牌背 · 莫兰迪风格 */
        .tarot-card-back {
            width: 180px;
            height: 300px;
            margin: 1rem auto;
            background: linear-gradient(135deg, #D4C4D8 0%, #C8B8CC 50%, #DCD4E0 100%);
            border-radius: 12px;
            border: 1px solid rgba(139,119,139,0.3);
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.5s ease;
        }
        .tarot-card-back:hover { transform: scale(1.02); }
        .tarot-card-back::before {
            content: 'aujourd\'hui';
            font-size: 0.9rem;
            letter-spacing: 0.3em;
            color: rgba(90,74,106,0.6);
            font-weight: 300;
            writing-mode: vertical-rl;
            text-orientation: mixed;
        }
        /* 解读渐入 */
        .mirror-fade-in {
            animation: mirrorFadeIn 1.2s ease-out forwards;
        }
        @keyframes mirrorFadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        /* 第2页：主次分明 + 开启镜像按钮莫兰迪紫 */
        .intro-main { font-size: 0.9rem !important; line-height: 1.8 !important; color: #5A5A6A !important; margin: 1.5rem 0 !important; }
        .disclaimer-secondary { font-size: 0.7rem !important; color: #9A9AAA !important; font-style: italic !important; margin-top: 1.5rem !important; padding-top: 1rem !important; border-top: 1px solid rgba(0,0,0,0.06) !important; }
        .card-screen-wrap .stButton > button { background: #9B8B9E !important; border-color: #8A7B8E !important; color: #fff !important; }
        .card-screen-wrap .stButton > button:hover { background: #8A7B8E !important; border-color: #7A6B7E !important; color: #fff !important; }
        /* 手机端响应式 */
        @media (max-width: 768px) {
            .main .block-container { padding: 1.25rem 1rem !important; max-width: 100% !important; }
            .stMarkdown h2 { font-size: 1.35rem !important; }
            .subtitle { font-size: 0.75rem !important; letter-spacing: 0.15em !important; }
            .intro-main { font-size: 0.85rem !important; margin: 1rem 0 !important; }
            .disclaimer-secondary { font-size: 0.65rem !important; margin-top: 1rem !important; }
            .mirror-output { padding: 1.25rem !important; font-size: 0.88rem !important; }
            .tarot-card-image { max-width: 160px !important; }
            .tarot-card-back { width: 150px !important; height: 250px !important; margin: 0.75rem auto !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# 开屏画作：The Magic Circle, John William Waterhouse, 1886（公有领域）
OPENING_ARTWORK_URL = "https://upload.wikimedia.org/wikipedia/commons/3/33/The_Magic_Circle_-_John_William_Waterhouse.jpg"
# 宝剑箭头 PNG（塔罗宝剑意象）：优先指定文件，否则使用项目根目录下任意 .png
_ROOT = Path(__file__).parent
# 牌背图（第二页）：支持 back.jpeg / back.jpg 等
_back_candidates = [_ROOT / "back.jpeg", _ROOT / "back.jpg", _ROOT / "back.JPG", _ROOT / "back.JPEG"]
BACK_IMAGE_PATH = next((p for p in _back_candidates if p.exists()), _ROOT / "back.jpeg")
SWORD_ARROW_PATH = _ROOT / "Gemini_Generated_Image_vkq8avkq8avkq8av.png"
if not SWORD_ARROW_PATH.exists():
    _pngs = list(_ROOT.glob("*.png"))
    SWORD_ARROW_PATH = _pngs[0] if _pngs else Path(".")


def render_opening_screen():
    """开屏：左画作（左下角作品信息）+ 右侧 tell me about today + 宝剑按钮"""
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        #MainMenu, footer, header { visibility: hidden !important; }
        [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
        [data-testid="stAppViewContainer"], .stApp, section.main {
            background: linear-gradient(90deg,
                #8B5A4A 0%,
                #A67B5B 20%,
                #C9A88A 45%,
                #E8DCC8 65%,
                #F5F0E5 80%,
                #E8F0F5 100%) !important;
        }
        .block-container { background: transparent !important; }
        .opening-artwork-wrap { display: inline-block; }
        .opening-artwork { border-radius: 12px; max-width: 100%; height: auto; }
        .opening-caption-below { margin-top: 0.75rem; font-size: 0.9rem; font-weight: 400; letter-spacing: 0.06em; color: rgba(60,48,42,0.9); }
        .opening-caption-below .meta { font-size: 0.75rem; color: rgba(60,48,42,0.7); }
        [data-testid="stHorizontalBlock"] > div:last-child .stButton { width: auto !important; }
        [data-testid="stHorizontalBlock"] > div:last-child .stButton > button {
            border: none !important; background: transparent !important;
            box-shadow: none !important; padding: 0.25rem !important;
            color: rgba(100,85,75,0.85) !important; font-size: 1.4rem !important;
            outline: none !important;
        }
        [data-testid="stHorizontalBlock"] > div:last-child .stButton > button:hover,
        [data-testid="stHorizontalBlock"] > div:last-child .stButton > button:focus {
            color: rgba(80,68,58,0.95) !important; background: transparent !important;
            border: none !important; outline: none !important; box-shadow: none !important;
        }
        .opening-text-block { margin-top: 14rem; margin-left: 5rem; }
        @media (max-width: 768px) {
            .block-container { padding: 1rem 0.75rem !important; }
            .opening-artwork { max-width: 100%; }
            .opening-caption-below { font-size: 0.8rem; }
            .opening-text-block { margin-top: 2rem; margin-left: 1rem; }
            [data-testid="column"] { min-width: 100% !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_img, col_text = st.columns([1.1, 1], gap="large")
    with col_img:
        img_src = OPENING_ARTWORK_URL
        if requests:
            data_url = _fetch_image_as_data_url(OPENING_ARTWORK_URL)
            if data_url:
                img_src = data_url
        st.markdown(
            f'''
            <div class="opening-artwork-wrap">
                <img src="{img_src}" alt="The Magic Circle" class="opening-artwork" />
            </div>
            <div class="opening-caption-below">
                <div>The Magic Circle</div>
                <div class="meta">1886, John William Waterhouse</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    with col_text:
        st.markdown(
            '<div class="opening-text-block">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-size:0.95rem; font-weight:300; letter-spacing:0.2em; color:rgba(88,75,68,0.9); margin-bottom:1.2rem;">tell me about today</p>',
            unsafe_allow_html=True,
        )
        if st.button("👉", key="open_sword", help="进入"):
            st.session_state["step"] = 2
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_breathing_screen():
    """静心引导：三次深呼吸"""
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        .stApp {
            background: linear-gradient(135deg, #E6D5E8 0%, #D4C4E8 100%);
            background-size: 200% 200%;
            animation: breathe 10s ease-in-out infinite;
        }
        @keyframes breathe {
            0%, 100% { background-position: 0% 50%; background-size: 180% 180%; }
            40% { background-position: 100% 50%; background-size: 250% 250%; }
            50% { background-position: 100% 50%; background-size: 250% 250%; }
            90% { background-position: 0% 50%; background-size: 180% 180%; }
        }
        .breathe-container { display: flex; flex-direction: column; align-items: center; min-height: 70vh; color: #4A4A4A; }
        .breathe-phase { font-size: 1.2rem; letter-spacing: 0.2em; margin-bottom: 1rem; }
        .breathe-count { font-size: 2.5rem; font-weight: 300; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    placeholder = st.empty()
    for breath in range(1, 4):
        for phase, sec in [("吸气", 4), ("呼气", 6)]:
            for s in range(sec, 0, -1):
                with placeholder.container():
                    st.markdown(
                        f"<div class='breathe-container'><div class='breathe-phase'>第 {breath} 次 · {phase}</div><div class='breathe-count'>{s}</div></div>",
                        unsafe_allow_html=True,
                    )
                time.sleep(1)
    st.session_state["step"] = 2
    st.rerun()


# 抽牌引导语（来自 logic_mapping_2 · 量子观测视角）
INTRO_BEFORE_DRAW = "这次观测将聚焦于当下的时间线切片，如同面对多棱镜的一个切面——它不预言未来，只映照此刻心理光谱中的一种可能颜色。你的觉察与选择，始终是书写故事的主体。"
INTRO_AFTER_DRAW = "这张牌如同今日心理风景的一帧快照，提供了一个对话的起点。所有解读都是可探讨、可质疑、可重新诠释的。你今天如何理解这份「镜像」？"
INTRO_REVERSED = "这张牌以逆位呈现，如同镜子被稍稍偏移了一个角度。它邀请我们观察同一种原型能量在当下可能呈现的另一种状态——或许是更内在的、正在调整的、或需要被温柔关注的一面。"

MBTI_OPTIONS = ["—", "INFP", "INFJ", "INTP", "INTJ", "ENFP", "ENFJ", "ENTP", "ENTJ", "ISFP", "ISFJ", "ISTP", "ISTJ", "ESFP", "ESFJ", "ESTP", "ESTJ"]
WEATHER_OPTIONS = ["—", "晴", "阴", "雨", "雪", "雾", "风", "多云"]
HELPLINE_REGION_OPTIONS = {"自动": "auto", "中国大陆": "CN", "香港": "HK", "台湾": "TW", "美国": "US", "英国": "GB", "日本": "JP", "韩国": "KR", "澳大利亚": "AU", "加拿大": "CA", "新加坡": "SG", "其他": "DEFAULT"}


def render_sidebar():
    """侧边栏：生理期模式、天气、危机热线地区（心情与 MBTI 已隐藏，解牌不参考）"""
    with st.sidebar:
        st.markdown("### 今日状态")
        period_mode = st.checkbox("生理期模式", value=False, help="开启后进入静谧修护模式，强调接纳与停顿")
        weather = st.selectbox("天气", options=WEATHER_OPTIONS, help="呼应当下氛围")
        region_label = st.selectbox(
            "危机热线地区",
            options=list(HELPLINE_REGION_OPTIONS.keys()),
            help="检测到危机倾向时展示当地心理援助热线；选「自动」则尝试按 IP 推断",
        )
        st.session_state["helpline_region"] = HELPLINE_REGION_OPTIONS.get(region_label, "auto")
    return period_mode, weather if weather != "—" else None


def render_ritual_screen():
    """抽牌仪式：牌背 -> 翻牌 -> 正面 + 解读渐入"""
    inject_morandi_css()
    st.markdown('<style>[data-testid="stSidebar"] { display: none !important; }</style>', unsafe_allow_html=True)

    drawn = st.session_state.get("drawn_card", {})
    if not drawn:
        st.session_state["step"] = 2
        st.rerun()

    card_name = drawn.get("card_name", "")
    narrative = drawn.get("narrative", "")
    artwork = drawn.get("artwork", {})

    phase = st.session_state.get("ritual_phase", "back")

    st.markdown("## aujourd'hui")
    st.markdown('<p class="subtitle">L\'image de soi</p>', unsafe_allow_html=True)
    st.caption("今日镜像 · 照见当下")

    if phase == "back":
        st.markdown(
            '<div style="text-align:center; margin:2rem 0;">'
            '<p style="font-size:0.9rem; letter-spacing:0.2em; color:#6A6A7A; margin-bottom:1rem;">轻轻触碰，翻开你的牌</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        # 牌背即按钮：点击牌背直接跳转，不单独「开始抽牌」
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            back_data = _local_image_as_data_url(BACK_IMAGE_PATH) if BACK_IMAGE_PATH.exists() else None
            if back_data:
                st.markdown(
                    f"""
                    <style>
                    [data-testid="column"]:nth-child(2) .stButton > button {{
                        width: 180px; height: 300px; margin: 0 auto;
                        display: block; background: url("{back_data}") center/cover no-repeat;
                        border: none; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                        cursor: pointer; color: transparent; font-size: 0;
                    }}
                    [data-testid="column"]:nth-child(2) .stButton {{ display: flex; justify-content: center; }}
                    @media (max-width: 768px) {{ [data-testid="column"]:nth-child(2) .stButton > button {{ width: 150px; height: 250px; }} }}
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <style>
                    [data-testid="column"]:nth-child(2) .stButton > button {
                        width: 180px; height: 300px; margin: 0 auto;
                        display: block; background: linear-gradient(135deg, #D4C4D8 0%, #C8B8CC 50%, #DCD4E0 100%);
                        border: 1px solid rgba(139,119,139,0.3); border-radius: 12px;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.08); cursor: pointer; color: transparent; font-size: 0;
                    }
                    [data-testid="column"]:nth-child(2) .stButton { display: flex; justify-content: center; }
                    @media (max-width: 768px) { [data-testid="column"]:nth-child(2) .stButton > button { width: 150px; height: 250px; } }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            if st.button("\u00A0", key="flip_card", help="点击翻开"):
                st.session_state["ritual_phase"] = "reveal"
                st.rerun()
    else:
        # 牌面左、解读右（网页版）；窄屏竖版堆叠
        is_reversed = " · 逆位" in card_name
        col_card, col_text = st.columns([1, 1.5])
        with col_card:
            render_tarot_image(card_name, alt=card_name, reversed=is_reversed)
        with col_text:
            reversed_intro = f"<p style='font-size:0.85rem; color:#6A6A7A; margin-bottom:1rem;'>{INTRO_REVERSED}</p>" if is_reversed else ""
            # 呼吸感：通感锚定（此刻，）单独一行；正文一段；收束句单独一行
            for marker in ["这是一种可能性视角", "今日镜像仅作为美学启发"]:
                if marker in narrative:
                    idx = narrative.find(marker)
                    before = narrative[:idx].strip()
                    closing_full = narrative[idx:].strip()
                    break
            else:
                before = narrative
                closing_full = ""
            # 首句（如 此刻，）单独一行，余下为正文
            if "，" in before:
                idx = before.find("，") + 1
                anchor_line = before[:idx]
                body_line = before[idx:].strip()
            else:
                anchor_line = ""
                body_line = before
            parts = []
            if anchor_line:
                parts.append(f"<p class='mirror-text'>{anchor_line}</p>")
            if body_line:
                parts.append(f"<p class='mirror-text' style='margin-top:0.6rem;'>{body_line}</p>")
            if closing_full:
                parts.append(f"<p class='mirror-text' style='margin-top:1rem;'>{closing_full}</p>")
            narrative_html = "".join(parts) if parts else f"<p class='mirror-text'>{narrative}</p>"
            mirror_html = f"""
            <div class="mirror-output mirror-fade-in">
                <div class="card-name">{card_name}</div>
                {reversed_intro}
                <p class="mirror-text"><strong>[当下叙事]</strong></p>
                <div style="margin-top:0.5rem;">{narrative_html}</div>
                <p class="mirror-text" style="margin-top:1.2rem;"><strong>[名画意境]</strong></p>
                <p class="mirror-text" style="margin-top:0.5rem;">
                {artwork.get('artist','')} · {artwork.get('title','')} ({artwork.get('year','')})<br>
                <a href="{artwork.get('url','#')}" target="_blank" style="color:#6A5A8A;">查看作品</a>
                </p>
                <p class="mirror-text" style="font-size:0.9em; margin-top:0.5rem;">{artwork.get('reason','')}</p>
                <p style="font-size:0.9rem; color:#7A7A8A; margin-top:1.5rem;">{INTRO_AFTER_DRAW}</p>
            </div>
            """
            try:
                st.html(mirror_html)
            except AttributeError:
                st.markdown(mirror_html, unsafe_allow_html=True)

    st.markdown(
        f'<p class="disclaimer">{DISCLAIMER}</p>',
        unsafe_allow_html=True,
    )


def render_card_screen():
    """正式抽牌界面：输入 -> 抽牌前引导语 -> 点击开启镜像 -> 跳转仪式页"""
    inject_morandi_css()

    period_mode, weather = render_sidebar()

    card_names, card_meanings, card_keywords = load_cards_from_logic_mapping()
    if not card_names:
        card_names = list(MAJOR_ARCANA_IMAGES.keys())

    st.markdown("## aujourd'hui")
    st.markdown('<p class="subtitle">L\'image de soi</p>', unsafe_allow_html=True)
    st.caption("今日镜像 · 照见当下")

    st.markdown('<div class="card-screen-wrap">', unsafe_allow_html=True)
    st.markdown(f'<p class="intro-main">{INTRO_BEFORE_DRAW}</p>', unsafe_allow_html=True)
    # 「此刻你在想什么」暂时隐藏，逻辑搁置
    thought = ""

    if st.button("开启镜像", key="open_mirror_btn", type="primary"):
        # 抽牌与牌义：见 draw_logic.py
        def get_meaning(cn: str, base: str) -> str:
            return card_meanings.get(cn) or card_meanings.get(base) or CARD_DATA.get(base, {}).get("raw", "照见当下的自己。")

        card_pool = build_card_pool(card_names)
        card_name, base_meaning = draw_one_card(card_pool, get_meaning)
        # 解牌不参考心情、MBTI，仅保留生理期与天气
        narrative, artwork = generate_narrative(
            card_name, mood=0, period_mode=period_mode, base_meaning=base_meaning, thought=thought,
            mbti=None, weather=weather, card_keywords=card_keywords,
        )

        st.session_state["drawn_card"] = {
            "card_name": card_name,
            "narrative": narrative,
            "artwork": artwork,
        }
        st.session_state["ritual_phase"] = "back"
        st.session_state["step"] = 3
        st.rerun()

    st.markdown(
        f'<p class="disclaimer-secondary">{DISCLAIMER}</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="aujourd'hui · 今日镜像",
        page_icon="◐",
        layout="centered",
        initial_sidebar_state="auto",
    )

    if "step" not in st.session_state:
        st.session_state["step"] = 0

    step = st.session_state["step"]

    if step == 0:
        render_opening_screen()
    elif step == 1:
        render_breathing_screen()
    elif step == 3:
        render_ritual_screen()
    else:
        render_card_screen()


if __name__ == "__main__":
    main()
