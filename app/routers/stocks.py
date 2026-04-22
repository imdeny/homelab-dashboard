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
            hist = yf.Ticker(symbol).history(period="5d")
            if len(hist) < 2:
                raise ValueError("Not enough data")
            price = round(float(hist["Close"].iloc[-1]), 2)
            prev = round(float(hist["Close"].iloc[-2]), 2)
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
