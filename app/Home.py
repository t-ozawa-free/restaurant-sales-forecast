import streamlit as st

st.set_page_config(
    page_title="飲食店売上予測ダッシュボード",
    page_icon="🍜",
    layout="wide"
)

st.title("🍜 飲食店売上予測ダッシュボード")
st.markdown("---")

st.markdown("""
## このアプリについて

飲食店の売上データを分析し、天気予報と連携して将来の売上を予測するダッシュボードです。

### 機能
- 📊 **分析ダッシュボード**：過去の売上データを可視化（期間フィルター付き）
- 🗓️ **1週間売上予測**：天気予報API連携による自動予測
- 🔮 **売上予測**：日付・天気・気温を指定して売上を予測
- 📈 **トレンド分析**：Prophetによる90日間の売上トレンドと季節性分解

### 使用技術
- Python / pandas / matplotlib
- LightGBM / Prophet
- Streamlit
- Open-Meteo API（天気予報）

### データについて
- 想定店舗：個人経営の小規模ラーメン店（大阪府）
- データ期間：2023年1月〜2024年12月
- ※本アプリはダミーデータを使用しています
""")

st.markdown("---")
st.caption("左のサイドバーからページを選択してください")