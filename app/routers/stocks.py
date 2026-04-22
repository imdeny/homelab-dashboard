from fastapi import APIRouter
import yfinance as yf
import json, time

router = APIRouter()

_cache: dict = {"data": [], "ts": 0}
_CACHE_TTL = 300  # 5 minutes


@router.get("")
def get_stocks():
    if time.time() - _cache["ts"] < _CACHE_TTL:
        return _cache["data"]

    with open("config.json") as f:
        tickers = json.load(f).get("stocks", [])

    results = []
    for symbol in tickers:
        try:
            info = yf.Ticker(symbol).fast_info
            price = round(info.last_price, 2)
            prev = round(info.previous_close, 2)
            change = round(price - prev, 2)
            results.append({
                "ticker": symbol,
                "price": price,
                "prev_close": prev,
                "change": change,
                "change_pct": round(change / prev * 100, 2),
            })
        except Exception as e:
            results.append({"ticker": symbol, "error": str(e)})

    _cache["data"] = results
    _cache["ts"] = time.time()
    return results
