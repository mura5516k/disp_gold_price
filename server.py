from __future__ import annotations

import csv
import io
import json
import urllib.request
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "0.0.0.0"
PORT = 8000
GOLD_USD_URL = "https://stooq.com/q/d/l/?s=xauusd&i=d"
USDJPY_URL = "https://stooq.com/q/d/l/?s=usdjpy&i=d"
TROY_OUNCE_TO_GRAM = 31.1034768

ROOT = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/gold"):
            self.handle_gold_api()
            return
        return super().do_GET()

    def handle_gold_api(self):
        try:
            gold_by_date = self.load_close_by_date(GOLD_USD_URL)
            usdjpy_by_date = self.load_close_by_date(USDJPY_URL)

            dates = sorted(set(gold_by_date.keys()) & set(usdjpy_by_date.keys()))
            rows = []
            for date in dates:
                gold_usd_oz = gold_by_date[date]
                usdjpy = usdjpy_by_date[date]
                jpy_per_g = (gold_usd_oz * usdjpy) / TROY_OUNCE_TO_GRAM
                rows.append(
                    {
                        "date": date,
                        "jpyPerGram": round(jpy_per_g, 2),
                        "usdPerOunce": round(gold_usd_oz, 4),
                        "usdJpy": round(usdjpy, 4),
                    }
                )

            payload = {
                "source": {"goldUsd": GOLD_USD_URL, "usdJpy": USDJPY_URL},
                "fetchedAt": datetime.now(timezone.utc).isoformat(),
                "unit": "JPY/g",
                "data": rows,
            }

            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:  # pragma: no cover - simple local server
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    @staticmethod
    def load_close_by_date(url: str) -> dict[str, float]:
        with urllib.request.urlopen(url, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")

        reader = csv.DictReader(io.StringIO(raw))
        data = {}
        for row in reader:
            date = row.get("Date")
            close = row.get("Close")
            if not date or not close:
                continue
            try:
                data[date] = float(close)
            except ValueError:
                continue
        return data


if __name__ == "__main__":
    print(f"Serving: http://localhost:{PORT}")
    with ThreadingHTTPServer((HOST, PORT), Handler) as server:
        server.serve_forever()
