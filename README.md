# 金価格トレンド (JPY/g)

1年・1か月・1週間の金価格推移を、日本円ベース (`JPY/g`) で表示するWebページです。

## 公開URL

GitHub Pages公開後のURL:

- https://mura5516k.github.io/disp_gold_price/

ローカル (`localhost`) で開いている場合でも、QRコードには上記公開URLを表示します。

## ローカル起動

```bash
python server.py
```

または `start_server.bat` を実行し、`http://localhost:8000` を開いてください。

## データ更新

- `scripts/update_gold_data.py` が `gold_data.json` を生成します。
- GitHub Actions (`.github/workflows/update-gold-data.yml`) が毎日自動更新します。

## GitHub Pages 設定

1. GitHub リポジトリの `Settings` を開く
2. `Pages` を開く
3. `Build and deployment` の `Source` を `Deploy from a branch` に設定
4. Branch を `main` / Folder を `/ (root)` に設定して保存

数分後に公開URLへ反映されます。
