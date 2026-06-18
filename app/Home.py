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

飲食店の売上データを分析し、将来の売上・来客数・商品別注文数を予測するダッシュボードです。

### 機能
- 📊 **分析ダッシュボード**：過去の売上データを可視化
- 🔮 **売上予測**：日付・天気・気温から売上・来客数を予測

### 使用技術
- Python / pandas / matplotlib
- LightGBM / Prophet
- Streamlit

### データについて
- 想定店舗：個人経営の小規模ラーメン店
- データ期間：2023年1月〜2024年12月
- ※本アプリはダミーデータを使用しています
""")

st.markdown("---")
st.caption("左のサイドバーからページを選択してください")