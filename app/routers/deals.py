from fastapi import APIRouter
import httpx, json, time

router = APIRouter()

_cache: dict = {"data": [], "ts": 0}
_CACHE_TTL = 1800  # 30 minutes


@router.get("")
async def get_deals():
    if time.time() - _cache["ts"] < _CACHE_TTL:
        return _cache["data"]

    with open("config.json") as f:
        page_size = json.load(f).get("deals_page_size", 8)

    deals = []

    async with httpx.AsyncClient(timeout=10) as client:
        # CheapShark top deals
        try:
            r = await client.get(
                "https://www.cheapshark.com/api/1.0/deals",
                params={"pageSize": page_size, "sortBy": "DealRating", "onSale": 1},
            )
            for d in r.json():
                deals.append({
                    "source": "Steam/PC",
                    "title": d["title"],
                    "sale_price": d["salePrice"],
                    "normal_price": d["normalPrice"],
                    "savings": round(float(d["savings"])),
                    "thumb": d.get("thumb"),
                    "url": f"https://www.cheapshark.com/redirect?dealID={d['dealID']}",
                    "free": float(d["salePrice"]) == 0,
                })
        except Exception:
            pass

        # Epic free games
        try:
            r = await client.get(
                "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions",
                params={"locale": "en-US", "country": "US", "allowCountries": "US"},
            )
            elements = (
                r.json()
                .get("data", {})
                .get("Catalog", {})
                .get("searchStore", {})
                .get("elements", [])
            )
            for game in elements:
                promos = (game.get("promotions") or {}).get("promotionalOffers", [])
                if promos:
                    orig = game.get("price", {}).get("totalPrice", {}).get("originalPrice", 0)
                    slug = game.get("productSlug") or game.get("urlSlug", "")
                    deals.append({
                        "source": "Epic",
                        "title": game["title"],
                        "sale_price": "0.00",
                        "normal_price": str(round(orig / 100, 2)),
                        "savings": 100,
                        "thumb": next(
                            (img["url"] for img in game.get("keyImages", []) if img.get("type") == "Thumbnail"),
                            None,
                        ),
                        "url": f"https://store.epicgames.com/en-US/p/{slug}",
                        "free": True,
                    })
        except Exception:
            pass

    _cache["data"] = deals
    _cache["ts"] = time.time()
    return deals
