import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
import sys
import os
from datetime import date

# prefectures.pyのパスを通す
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from prefectures import PREFECTURES

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

# 天気コードを日本語に変換
def weathercode_to_japanese(code):
    if code <= 2:
        return "晴れ"
    elif code == 3:
        return "曇り"
    elif 51 <= code <= 67 or 80 <= code <= 99:
        return "雨"
    elif 71 <= code <= 77:
        return "雪"
    else:
        return "曇り"

# 天気アイコン
def weather_to_icon(weather):
    icons = {"晴れ": "☀️", "曇り": "☁️", "雨": "🌧️", "雪": "❄️"}
    return icons.get(weather, "")

# 予測特徴量の作成
def make_features(target_date, weather, temperature):
    return pd.DataFrame({
        "day_of_week": [target_date.weekday()],
        "month": [target_date.month],
        "year": [target_date.year],
        "temperature": [temperature],
        "is_weekend": [1 if target_date.weekday() >= 5 else 0],
        "weather_晴れ": [1 if weather == "晴れ" else 0],
        "weather_曇り": [1 if weather == "曇り" else 0],
        "weather_雨": [1 if weather == "雨" else 0],
        "weather_雪": [1 if weather == "雪" else 0],
    })

# ===== 1週間自動予測 =====
st.subheader("🗓️ 1週間の売上予測（天気予報連携）")

# 大阪固定
prefecture = "大阪府"

if st.button("1週間の予測を取得", type="primary"):
    lat = PREFECTURES[prefecture]["lat"]
    lon = PREFECTURES[prefecture]["lon"]

    st.info(f"📍 店舗所在地：{prefecture}（天気予報取得先）")
    # 天気予報APIの呼び出し
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "weathercode"
            ],
            "timezone": "Asia/Tokyo",
            "forecast_days": 7
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()["daily"]

        # 予測テーブルの作成
        day_labels = ["月", "火", "水", "木", "金", "土", "日"]
        results = []

        for i in range(7):
            target_date = pd.to_datetime(data["time"][i]).date()
            avg_temp = (data["temperature_2m_max"][i] + data["temperature_2m_min"][i]) / 2
            weather = weathercode_to_japanese(data["weathercode"][i])
            pred_sales = model.predict(make_features(target_date, weather, avg_temp))[0]

            results.append({
                "日付": target_date.strftime("%m/%d"),
                "曜日": day_labels[target_date.weekday()],
                "天気": f"{weather_to_icon(weather)} {weather}",
                "平均気温": f"{avg_temp:.1f}℃",
                "予測売上": f"¥{pred_sales:,.0f}円",
                "予測売上（万円）": round(pred_sales / 10000, 1),
            })

        results_df = pd.DataFrame(results)

        # テーブル表示
        st.dataframe(
            results_df.drop(columns=["予測売上（万円）"]),
            width="stretch",
            hide_index=True
        )

        # 棒グラフ表示
        import matplotlib.pyplot as plt
        import japanize_matplotlib

        fig, ax = plt.subplots(figsize=(10, 4))
        colors = ["coral" if r["曜日"] in ["土", "日"] else "steelblue" for r in results]
        ax.bar(
            [f'{r["日付"]}({r["曜日"]})' for r in results],
            [r["予測売上（万円）"] for r in results],
            color=colors
        )
        ax.set_title(f"{prefecture}・1週間の売上予測", fontsize=14)
        ax.set_xlabel("日付")
        ax.set_ylabel("予測売上（万円）")
        ax.legend(handles=[
            plt.Rectangle((0,0),1,1, color="coral", label="土日"),
            plt.Rectangle((0,0),1,1, color="steelblue", label="平日")
        ])
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        st.caption("※ 予測誤差の目安：± ¥6,300円程度（RMSE基準）")

    except Exception as e:
        st.error(f"天気予報の取得に失敗しました。通信環境を確認してください。（{e}）")

st.markdown("---")

# ===== 手動入力による予測 =====
st.subheader("📋 条件を指定して予測する")

col1, col2, col3 = st.columns(3)

with col1:
    input_date = st.date_input("予測日", value=date.today())

with col2:
    weather = st.selectbox("天気", ["晴れ", "曇り", "雨", "雪"])

with col3:
    temperature = st.slider("気温（℃）", min_value=-10, max_value=40, value=20)

st.markdown("---")

if st.button("予測する", type="primary"):

    input_df = make_features(input_date, weather, temperature)
    pred_sales = model.predict(input_df)[0]

    st.subheader("📊 予測結果")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="予測売上", value=f"¥{pred_sales:,.0f}円")
    with col2:
        st.metric(label="予測売上（万円）", value=f"¥{pred_sales/10000:.1f}万円")
    with col3:
        day_labels = ["月", "火", "水", "木", "金", "土", "日"]
        st.metric(label="曜日", value=day_labels[input_date.weekday()])

    st.markdown("---")
    st.caption("※ 予測誤差の目安：± ¥6,300円程度（RMSE基準）")

st.markdown("---")

# ===== Prophet予測グラフ =====
st.subheader("📈 今後90日間の売上トレンド（Prophet）")

@st.cache_resource
def load_prophet_model():
    with open("../ml/models/prophet_model.pkl", "rb") as f:
        prophet_model = pickle.load(f)
    return prophet_model

prophet_model = load_prophet_model()

future = prophet_model.make_future_dataframe(periods=90)
forecast = prophet_model.predict(future)

import matplotlib.pyplot as plt
import japanize_matplotlib

sales_df = pd.read_csv("../data/raw/sales.csv")
sales_df["date"] = pd.to_datetime(sales_df["date"])
daily_df = sales_df.groupby("date")["total"].sum().reset_index()

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(daily_df["date"], daily_df["total"] / 10000,
        color="steelblue", label="実績", linewidth=1, alpha=0.7)
ax.plot(forecast["ds"], forecast["yhat"] / 10000,
        color="orange", label="予測", linewidth=1)
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