import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib

st.set_page_config(page_title="分析ダッシュボード", page_icon="📊", layout="wide")
st.title("📊 分析ダッシュボード")
st.markdown("---")

# データ読み込み
@st.cache_data
def load_data():
    sales_df = pd.read_csv("../data/raw/sales.csv")
    detail_df = pd.read_csv("../data/raw/sale_details.csv")
    sales_df["date"] = pd.to_datetime(sales_df["date"])
    # 欠損値チェック
    if sales_df.isnull().sum().sum() > 0:
        st.warning("売上データに欠損値が検出されました")
    return sales_df, detail_df

sales_df, detail_df = load_data()

# ===== サイドバー：期間フィルター =====
st.sidebar.header("🔍 期間フィルター")

years = sorted(sales_df["date"].dt.year.unique())
selected_years = st.sidebar.multiselect(
    "年を選択",
    options=years,
    default=years
)

months = list(range(1, 13))
month_labels = {i: f"{i}月" for i in months}
selected_months = st.sidebar.multiselect(
    "月を選択",
    options=months,
    format_func=lambda x: month_labels[x],
    default=months
)

# フィルター適用
filtered_df = sales_df[
    (sales_df["date"].dt.year.isin(selected_years)) &
    (sales_df["date"].dt.month.isin(selected_months))
].copy()

# detail_dfもフィルターに連動させる
filtered_detail_df = detail_df[detail_df["sale_id"].isin(filtered_df["sale_id"])]

# フィルター結果が空の場合
if len(filtered_df) == 0:
    st.warning("選択した期間にデータがありません。期間を変更してください。")
    st.stop()

# ===== KPI指標 =====
st.subheader("📈 KPI サマリー")

total_sales = filtered_df["total"].sum()
total_count = len(filtered_df)
avg_sales = filtered_df["total"].mean()
daily_avg = filtered_df.groupby("date")["total"].sum().mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="総売上", value=f"¥{total_sales/10000:.0f}万円")
with col2:
    st.metric(label="総会計数", value=f"{total_count:,}件")
with col3:
    st.metric(label="平均客単価", value=f"¥{avg_sales:,.0f}円")
with col4:
    st.metric(label="1日平均売上", value=f"¥{daily_avg/10000:.1f}万円")

st.markdown("---")

# ===== 月別売上推移 =====
st.subheader("📅 月別売上推移")
filtered_df.loc[:, "year_month"] = filtered_df["date"].dt.to_period("M")
monthly_sales = filtered_df.groupby("year_month")["total"].sum().reset_index()
monthly_sales["year_month"] = monthly_sales["year_month"].astype(str)

fig, ax = plt.subplots(figsize=(14, 4))
ax.bar(monthly_sales["year_month"], monthly_sales["total"] / 10000, color="steelblue")
ax.set_xlabel("年月")
ax.set_ylabel("売上合計（万円）")
ax.tick_params(axis="x", rotation=45)
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

# ===== 曜日別・天気別 =====
col1, col2 = st.columns(2)

with col1:
    st.subheader("📆 曜日別売上")
    day_labels = ["月", "火", "水", "木", "金", "土", "日"]
    filtered_df.loc[:, "day_of_week"] = filtered_df["date"].dt.dayofweek
    daily_sales = filtered_df.groupby("day_of_week")["total"].sum().reset_index()
    daily_sales["day_label"] = daily_sales["day_of_week"].map(lambda x: day_labels[x])

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(daily_sales["day_label"], daily_sales["total"] / 10000, color="steelblue")
    ax.set_xlabel("曜日")
    ax.set_ylabel("売上合計（万円）")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("🌤️ 天気別会計数")
    weather_sales = filtered_df.groupby("weather")["total"].agg(["sum", "mean", "count"]).reset_index()
    weather_sales.columns = ["weather", "sum", "mean", "count"]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(weather_sales["weather"], weather_sales["count"], color="steelblue")
    ax.set_xlabel("天気")
    ax.set_ylabel("会計数（件）")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

st.markdown("---")

# ===== 商品別売上ランキング =====
st.subheader("🍜 商品別注文数ランキング")
item_count = filtered_detail_df.groupby("item_name")["quantity"].sum().reset_index()
item_count = item_count.sort_values("quantity", ascending=True)

fig, ax = plt.subplots(figsize=(14, 6))
ax.barh(item_count["item_name"], item_count["quantity"], color="steelblue")
ax.set_xlabel("注文数（件）")
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

# 商品別売上合計ランキング
st.subheader("💰 商品別売上合計ランキング")
item_sales = filtered_detail_df.groupby("item_name")["price"].sum().reset_index()
item_sales = item_sales.sort_values("price", ascending=True)

fig, ax = plt.subplots(figsize=(14, 6))
ax.barh(item_sales["item_name"], item_sales["price"] / 10000, color="steelblue")
ax.set_xlabel("売上合計（万円）")
plt.tight_layout()
st.pyplot(fig)
plt.close()

st.markdown("---")

# ===== ランチ vs ディナー =====
st.subheader("🕐 ランチ vs ディナー")

def get_time_zone(time_str):
    hour = int(time_str.split(":")[0])
    if 11 <= hour <= 14:
        return "ランチ"
    elif 17 <= hour <= 22:
        return "ディナー"
    else:
        return "その他"

filtered_df.loc[:, "time_zone"] = filtered_df["time"].apply(get_time_zone)

timezone_sales = filtered_df.groupby("time_zone").agg(
    売上合計=("total", "sum"),
    会計数=("sale_id", "count"),
    平均売上=("total", "mean")
).reset_index()

col1, col2, col3 = st.columns(3)

with col1:
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(timezone_sales["time_zone"], timezone_sales["売上合計"] / 10000, color="steelblue")
    ax.set_title("時間帯別・合計売上")
    ax.set_xlabel("時間帯")
    ax.set_ylabel("売上合計（万円）")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col2:
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(timezone_sales["time_zone"], timezone_sales["会計数"], color="steelblue")
    ax.set_title("時間帯別・会計数")
    ax.set_xlabel("時間帯")
    ax.set_ylabel("会計数（件）")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

with col3:
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(timezone_sales["time_zone"], timezone_sales["平均売上"], color="steelblue")
    ax.set_title("時間帯別・平均売上（1会計あたり）")
    ax.set_xlabel("時間帯")
    ax.set_ylabel("平均売上（円）")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()