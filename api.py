# aujourdhui — 今日镜像 · 后端 API
# 供 Uni-app/Taro 等前端调用：POST /api/draw 返回抽牌结果 + 叙事 + 名画
#
# 本地运行：uvicorn api:app --reload
# 接口文档：http://127.0.0.1:8000/docs

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 从 app 引用牌库、叙事与配图逻辑（主端为 Uni-app H5/小程序 + 本 API）
from app import (
    CARD_DATA,
    MAJOR_ARCANA_IMAGES,
    load_cards_from_logic_mapping,
    generate_narrative,
    get_tarot_image_url,
)
from draw_logic import build_card_pool, draw_one_card, match_artwork

app = FastAPI(
    title="aujourdhui · 今日镜像",
    description="抽牌与解读 API，入参仅保留抽出的牌（牌名+牌义+关键词）。",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/draw")
def draw():
    """
    抽一张牌，生成叙事与名画匹配。
    无入参；返回 card_name, base_meaning, narrative, artwork, card_image_url。
    """
    card_names, card_meanings, card_keywords = load_cards_from_logic_mapping()
    if not card_names:
        card_names = list(MAJOR_ARCANA_IMAGES.keys())

    def get_meaning(cn: str, base: str) -> str:
        return (
            card_meanings.get(cn)
            or card_meanings.get(base)
            or CARD_DATA.get(base, {}).get("raw", "照见当下的自己。")
        )

    card_pool = build_card_pool(card_names)
    card_name, base_meaning = draw_one_card(card_pool, get_meaning)
    narrative, artwork = generate_narrative(card_name, base_meaning, card_keywords)
    card_image_url = get_tarot_image_url(card_name)

    # 去除 AI/Markdown 格式残留（宪章：前端不得展示 ** 等痕迹）
    def strip_markdown(s: str) -> str:
        return (s or "").replace("**", "")

    narrative = strip_markdown(narrative)
    artwork = dict(artwork)
    if artwork.get("reason"):
        artwork["reason"] = strip_markdown(artwork["reason"])

    # artwork 中 year 可能为 int（artwork_minor），统一成 str 便于 JSON
    aw = artwork
    if "year" in aw and aw["year"] is not None:
        aw["year"] = str(aw["year"])

    return {
        "card_name": card_name,
        "base_meaning": base_meaning,
        "narrative": narrative,
        "artwork": aw,
        "card_image_url": card_image_url,
    }


@app.get("/")
def root():
    return {"service": "aujourdhui · 今日镜像", "docs": "/docs"}
