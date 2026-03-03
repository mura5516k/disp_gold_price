from __future__ import annotations

import csv
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

GOLD_USD_URL = "https://stooq.com/q/d/l/?s=xauusd&i=d"
USDJPY_URL = "https://stooq.com/q/d/l/?s=usdjpy&i=d"
TROY_OUNCE_TO_GRAM = 31.1034768
ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "gold_data.json"


def load_close_by_date(url: str) -> dict[str, float]:
    with urllib.request.urlopen(url, timeout=20) as resp:
        raw = resp.read().decode("utf-8", errors="replace")

    reader = csv.DictReader(io.StringIO(raw))
    out: dict[str, float] = {}
    for row in reader:
        date = row.get("Date")
        close = row.get("Close")
        if not date or not close:
            continue
        try:
            out[date] = float(close)
        except ValueError:
            continue
    return out


def main() -> None:
    gold_by_date = load_close_by_date(GOLD_USD_URL)
    usdjpy_by_date = load_close_by_date(USDJPY_URL)

    dates = sorted(set(gold_by_date.keys()) & set(usdjpy_by_date.keys()))
    rows = []
    for date in dates:
        gold_usd_oz = gold_by_date[date]
        usd_jpy = usdjpy_by_date[date]
        jpy_per_gram = (gold_usd_oz * usd_jpy) / TROY_OUNCE_TO_GRAM
        rows.append(
            {
                "date": date,
                "jpyPerGram": round(jpy_per_gram, 2),
                "usdPerOunce": round(gold_usd_oz, 4),
                "usdJpy": round(usd_jpy, 4),
            }
        )

    payload = {
        "source": {"goldUsd": GOLD_USD_URL, "usdJpy": USDJPY_URL},
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "unit": "JPY/g",
        "data": rows,
    }

    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_FILE} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
