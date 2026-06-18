# 🍜 飲食店売上予測ダッシュボード

飲食店の売上データを分析し、将来の売上を予測するWebアプリです。

---

## 📊 デモ画像

※ スクリーンショットをここに追加予定

---

## 🎯 プロジェクト概要

| 項目 | 内容 |
|---|---|
| **想定店舗** | 個人経営の小規模ラーメン店 |
| **データ期間** | 2023年1月〜2024年12月（2年分） |
| **データ** | ダミーデータ（実データへの対応可能） |
| **予測精度** | MAPE 9.5%（LightGBM） |

---

## 🔧 使用技術

- **言語**：Python 3.x
- **分析・ML**：pandas / matplotlib / LightGBM / Prophet
- **Webアプリ**：Streamlit
- **管理**：Git / GitHub

---

## 📁 ディレクトリ構成

```
restaurant-sales-forecast/
├── data/
│   └── raw/                  # CSVデータ
├── notebooks/
│   ├── 01_EDA.ipynb          # 探索的データ分析
│   ├── 02_model_training.ipynb    # LightGBM学習
│   └── 03_prophet_training.ipynb  # Prophet学習
├── ml/
│   └── models/               # 学習済みモデル（.pkl）
├── app/
│   ├── Home.py               # トップページ
│   └── pages/
│       ├── 1_分析ダッシュボード.py
│       └── 2_売上予測.py
└── README.md
```

---

## 🚀 セットアップ手順

```bash
# リポジトリのクローン
git clone https://github.com/t-ozawa-free/restaurant-sales-forecast.git
cd restaurant-sales-forecast

# 仮想環境の作成・有効化
python -m venv .venv
.venv\Scripts\activate  # Windows

# ライブラリのインストール
pip install -r requirements.txt

# Streamlitの起動
cd app
streamlit run Home.py
```

---

## 📈 機能一覧

### 分析ダッシュボード
- KPIサマリー（総売上・総会計数・平均客単価・1日平均売上）
- 月別売上推移
- 曜日別売上
- 天気別会計数
- 商品別注文数・売上ランキング
- ランチ vs ディナー比較
- 期間フィルター（年・月）

### 売上予測
- LightGBMによる条件付き売上予測（日付・天気・気温を入力）
- Prophetによる90日間の売上トレンド予測
- 週次・年次季節性の分解グラフ

---

## 🔍 分析のポイント

EDAで発見した主な傾向：

- **曜日**：土曜が最多、月・火が最低（LightGBMの特徴量重要度でも1位）
- **天気**：雨・雪の日は来客数が激減（合計売上に影響、客単価には影響なし）
- **季節**：7・8月（夏休み）・12月（年末）が繁忙期、1・2月が閑散期

---

## 🔮 今後の拡張予定

- 来客数予測・商品別注文数予測の追加
- 実データのアップロード機能
- 天気予報API連携による1週間分の自動売上予測
- cronによる日次自動学習の仕組み
- デプロイ（Streamlit Cloud）

---

## 👤 作者

**t.ozawa**  
フリーランスAI・データエンジニア志望  
C/組み込み系 → AI・データサイエンス領域へ転向中