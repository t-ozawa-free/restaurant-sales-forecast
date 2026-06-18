import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import date

st.set_page_config(page_title="売上予測", page_icon="🔮", layout="wide")
st.title("🔮 売上予測")
st.markdown("---")

# モデル読み込み
@st.cache_resource
def load_model():
    with open("../ml/models/sales_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("../ml/models/feature_cols.pkl", "rb") as f:
        feature_cols = pickle.load(f)
    return model, feature_cols

model, feature_cols = load_model()

# ===== 入力フォーム =====
st.subheader("📋 予測条件を入力してください")

col1, col2, col3 = st.columns(3)

with col1:
    input_date = st.date_input("予測日", value=date.today())

with col2:
    weather = st.selectbox("天気", ["晴れ", "曇り", "雨", "雪"])

with col3:
    temperature = st.slider("気温（℃）", min_value=-10, max_value=40, value=20)

st.markdown("---")

# ===== 予測実行 =====
if st.button("予測する", type="primary"):

    # 特徴量の作成
    input_df = pd.DataFrame({
        "day_of_week": [input_date.weekday()],
        "month": [input_date.month],
        "year": [input_date.year],
        "temperature": [temperature],
        "is_weekend": [1 if input_date.weekday() >= 5 else 0],
        "weather_晴れ": [1 if weather == "晴れ" else 0],
        "weather_曇り": [1 if weather == "曇り" else 0],
        "weather_雨": [1 if weather == "雨" else 0],
        "weather_雪": [1 if weather == "雪" else 0],
    })

    # 予測
    pred_sales = model.predict(input_df)[0]

    # ===== 結果表示 =====
    st.subheader("📊 予測結果")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="予測売上",
            value=f"¥{pred_sales:,.0f}円"
        )
    with col2:
        st.metric(
            label="予測売上（万円）",
            value=f"¥{pred_sales/10000:.1f}万円"
        )
    with col3:
        day_labels = ["月", "火", "水", "木", "金", "土", "日"]
        st.metric(
            label="曜日",
            value=day_labels[input_date.weekday()]
        )

    # 予測の根拠
    st.markdown("---")
    st.caption(f"※ 予測誤差の目安：± ¥6,300円程度（RMSE基準）")


st.markdown("---")

# ===== Prophet予測グラフ =====
st.subheader("📈 今後90日間の売上トレンド（Prophet）")

@st.cache_resource
def load_prophet_model():
    with open("../ml/models/prophet_model.pkl", "rb") as f:
        prophet_model = pickle.load(f)
    return prophet_model

prophet_model = load_prophet_model()

# 将来90日分の予測
future = prophet_model.make_future_dataframe(periods=90)
forecast = prophet_model.predict(future)

# グラフ描画
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd

# 実績データ読み込み
sales_df = pd.read_csv("../data/raw/sales.csv")
sales_df["date"] = pd.to_datetime(sales_df["date"])
daily_df = sales_df.groupby("date")["total"].sum().reset_index()

fig, ax = plt.subplots(figsize=(14, 5))

# 実績値
ax.plot(daily_df["date"], daily_df["total"] / 10000,
        color="steelblue", label="実績", linewidth=1, alpha=0.7)

# 予測値
ax.plot(forecast["ds"], forecast["yhat"] / 10000,
        color="orange", label="予測", linewidth=1)

# 信頼区間
ax.fill_between(
    forecast["ds"],
    forecast["yhat_lower"] / 10000,
    forecast["yhat_upper"] / 10000,
    alpha=0.3, color="orange", label="信頼区間"
)

ax.set_xlabel("日付")
ax.set_ylabel("売上（万円）")
ax.legend()
ax.tick_params(axis="x", rotation=45)
plt.tight_layout()
st.pyplot(fig)
plt.close()

# 季節性の分解グラフ
st.subheader("📊 売上の構成要素分解")
col1, col2 = st.columns(2)

with col1:
    st.caption("週次季節性（曜日パターン）")
    weekly = forecast[["ds", "weekly"]].copy()
    weekly["day"] = weekly["ds"].dt.day_name()
    weekly_avg = weekly.groupby("day")["weekly"].mean()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels_jp = ["月", "火", "水", "木", "金", "土", "日"]
    weekly_avg = weekly_avg.reindex(day_order)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(day_labels_jp, weekly_avg.values / 10000, color="steelblue")
    ax.set_xlabel("曜日")
    ax.set_ylabel("売上への影響（万円）")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.caption("年次季節性（月パターン）")
    yearly = forecast[["ds", "yearly"]].copy()
    yearly["month"] = yearly["ds"].dt.month
    yearly_avg = yearly.groupby("month")["yearly"].mean()

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(range(1, 13), yearly_avg.values / 10000, color="steelblue")
    ax.set_xlabel("月")
    ax.set_ylabel("売上への影響（万円）")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([f"{m}月" for m in range(1, 13)])
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()