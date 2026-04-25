
import os
import math
import random
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="我到底等了多久？",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Mobile-first CSS
# -----------------------------
st.markdown(
    """
    <style>
    :root {
        --card-bg: rgba(255, 255, 255, 0.82);
        --ink: #352f44;
        --muted: #6c6478;
        --accent: #ff8fab;
        --accent2: #8ecae6;
        --soft: #fff1f5;
        --line: rgba(255, 143, 171, 0.22);
    }
    .stApp {
        background:
            radial-gradient(circle at top left, #ffe5ec 0, transparent 28%),
            radial-gradient(circle at top right, #dff6ff 0, transparent 28%),
            linear-gradient(180deg, #fff8fb 0%, #f9fbff 100%);
        color: var(--ink);
    }
    [data-testid="stHeader"] { background: rgba(255, 248, 251, 0.72); }
    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 3rem;
        max-width: 980px;
    }
    h1, h2, h3 { letter-spacing: -0.02em; }
    .hero {
        padding: 1.5rem 1.3rem;
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(255, 241, 245, 0.98), rgba(235, 248, 255, 0.96));
        border: 1px solid rgba(255, 143, 171, 0.26);
        box-shadow: 0 18px 46px rgba(255, 143, 171, 0.16);
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: clamp(2rem, 7vw, 4.2rem);
        font-weight: 900;
        line-height: 1.03;
        color: #2d2438;
        margin-bottom: 0.55rem;
    }
    .hero-subtitle {
        font-size: clamp(1rem, 3.3vw, 1.28rem);
        color: #665a75;
        line-height: 1.7;
    }
    .pill-row { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1rem; }
    .pill {
        display: inline-block;
        padding: .36rem .72rem;
        border-radius: 999px;
        background: white;
        border: 1px solid rgba(255, 143, 171, 0.28);
        color: #594d66;
        font-size: .88rem;
    }
    .section-card {
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: 0 12px 36px rgba(88, 63, 94, 0.08);
        padding: 1rem 1rem 1.15rem 1rem;
        margin: 1rem 0;
    }
    .section-title {
        font-size: 1.42rem;
        font-weight: 850;
        margin-bottom: .15rem;
        color: #342b40;
    }
    .section-desc {
        color: #766b82;
        line-height: 1.65;
        margin-bottom: .65rem;
    }
    .metric-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,246,249,0.92));
        border: 1px solid rgba(255, 143, 171, 0.23);
        border-radius: 22px;
        padding: 1rem .9rem;
        min-height: 128px;
        box-shadow: 0 10px 26px rgba(255, 143, 171, 0.12);
    }
    .metric-label { color: #776c83; font-size: .92rem; margin-bottom: .28rem; }
    .metric-value { color: #2f2639; font-size: 2rem; font-weight: 900; line-height: 1.05; }
    .metric-note { color: #8a7e96; font-size: .86rem; margin-top: .5rem; line-height: 1.45; }
    .snark {
        background: #fff7fb;
        border-left: 5px solid #ff8fab;
        padding: .85rem .95rem;
        border-radius: 16px;
        color: #574c63;
        line-height: 1.7;
        margin: .7rem 0 .5rem 0;
    }
    .rank-card {
        background: #ffffffcc;
        border: 1px solid rgba(142, 202, 230, .32);
        border-radius: 20px;
        padding: .85rem .95rem;
        margin-bottom: .7rem;
        box-shadow: 0 8px 24px rgba(142, 202, 230, 0.10);
    }
    .rank-title { font-weight: 850; color: #2f2639; font-size: 1.05rem; }
    .rank-meta { color: #746980; font-size: .9rem; margin: .18rem 0 .35rem 0; }
    .rank-snark { color: #5f536d; line-height: 1.55; }
    .final-card {
        padding: 1.2rem;
        border-radius: 26px;
        background: linear-gradient(135deg, #fff1f5 0%, #e8f8ff 100%);
        border: 1px solid rgba(255, 143, 171, .30);
        box-shadow: 0 18px 44px rgba(255, 143, 171, 0.15);
        line-height: 1.85;
        font-size: 1.02rem;
    }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    .stSelectbox, .stMultiSelect, .stSlider { background: transparent; }
    @media (max-width: 640px) {
        .block-container { padding-left: .9rem; padding-right: .9rem; }
        .section-card { padding: .9rem .78rem; border-radius: 22px; }
        .metric-card { min-height: 118px; }
        .metric-value { font-size: 1.65rem; }
        .hero { padding: 1.15rem 1rem; border-radius: 24px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_FILE = "interaction_data.xlsx"

@st.cache_data
def load_data():
    path_candidates = [DATA_FILE, os.path.join(os.path.dirname(__file__), DATA_FILE), "/mnt/data/interaction_data(1).xlsx", "/mnt/data/interaction_data.xlsx"]
    path = next((p for p in path_candidates if os.path.exists(p)), None)
    if path is None:
        st.error("找不到 interaction_data.xlsx。请把 Excel 文件和 app.py 放在同一个文件夹里。")
        st.stop()

    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    df["Notes"] = df["Notes"].fillna("")
    df["Queue_Number"] = pd.to_numeric(df["Queue_Number"], errors="coerce")
    df["Waiting_Time_hr"] = pd.to_numeric(df["Waiting_Time_hr"], errors="coerce").fillna(0)
    df["Waiting_Time_min"] = (df["Waiting_Time_hr"] * 60).round(0).astype(int)
    df["Date_Display"] = df["Date"].astype(str)
    df["Date_dt"] = pd.to_datetime("2026/" + df["Date"].astype(str), errors="coerce")
    df["Start_dt"] = pd.to_datetime("2026/" + df["Date"].astype(str) + " " + df["Start_Time"].astype(str), errors="coerce")
    df["End_dt"] = pd.to_datetime("2026/" + df["Date"].astype(str) + " " + df["End_Time"].astype(str), errors="coerce")
    df["Actual_dt"] = pd.to_datetime("2026/" + df["Date"].astype(str) + " " + df["Actual_Time"].astype(str), errors="coerce")

    # If actual time crosses midnight, push by one day. Rare, but safe.
    mask = df["Actual_dt"] < df["Start_dt"]
    df.loc[mask, "Actual_dt"] = df.loc[mask, "Actual_dt"] + pd.Timedelta(days=1)

    df["Activity_Duration_min"] = ((df["End_dt"] - df["Start_dt"]).dt.total_seconds() / 60).round(0)
    df["Expected_dt"] = df["Actual_dt"] - pd.to_timedelta(df["Waiting_Time_min"], unit="m")
    df["Expected_Time"] = df["Expected_dt"].dt.strftime("%H:%M")
    df["Start_Hour"] = df["Start_dt"].dt.hour + df["Start_dt"].dt.minute / 60

    def time_slot(h):
        if pd.isna(h): return "未知"
        if h < 14: return "午场"
        if h < 17: return "下午场"
        return "晚场"

    def delay_level(x):
        if x <= 0.5: return "正常区"
        if x <= 1: return "微崩区"
        if x <= 2: return "中崩区"
        return "大崩区"

    df["Time_Slot"] = df["Start_Hour"].apply(time_slot)
    df["Delay_Level"] = df["Waiting_Time_hr"].apply(delay_level)
    df["Severe_Delay"] = df["Waiting_Time_hr"] > 1
    df["Record_Label"] = df["Person"] + "｜" + df["Date_Display"] + "｜" + df["Start_Time"].astype(str) + "-" + df["End_Time"].astype(str)
    return df


def fmt_hr(x):
    if pd.isna(x):
        return "-"
    return f"{x:.2f}h"


def fmt_min(x):
    if pd.isna(x):
        return "-"
    return f"{int(round(x))}min"


def section(title, desc=""):
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div><div class="section-desc">{desc}</div>', unsafe_allow_html=True)


def end_section():
    st.markdown('</div>', unsafe_allow_html=True)


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def snark(text):
    st.markdown(f'<div class="snark">{text}</div>', unsafe_allow_html=True)


def rank_snark(row, rank):
    wait = row["Waiting_Time_hr"]
    person = row["Person"]
    date = row["Date_Display"]
    if wait >= 3:
        return f"{date} 这一场直接封神，等到 {wait:.1f} 小时，已经可以给等待颁一个全勤奖。"
    if wait >= 2.2:
        return f"这不是互动，这是大型耐力赛。{person} 的时间黑洞属性在这一场非常明显。"
    if wait >= 2:
        return "一小时活动，两小时等待，时间管理反向教学。"
    if wait >= 1.5:
        return "已经进入‘我是不是应该先去吃个饭’的心理阶段。"
    return "虽然没到崩溃区，但也足够让人把手机电量刷掉一截。"


def movie_equiv(hours):
    return hours / 2

def milk_tea_equiv(hours):
    return hours * 2

def song_equiv(hours):
    return hours * 60 / 4

def drama_equiv(hours):
    return hours * 60 / 45


def plot_layout(fig, height=360):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=42, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.62)",
        font=dict(family="Arial, sans-serif", size=13, color="#463d52"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(90,70,100,.12)")
    return fig


raw = load_data()

# -----------------------------
# Hero
# -----------------------------
st.markdown(
    """
    <div class="hero">
      <div class="hero-title">我到底等了多久？</div>
      <div class="hero-subtitle">线下互动延迟研究报告｜一份不严肃但很认真的排队受害者数据分析</div>
      <div class="pill-row">
        <span class="pill">⏳ 等待宇宙</span>
        <span class="pill">💗 小红书风</span>
        <span class="pill">🤡 吐槽友好</span>
        <span class="pill">📱 手机优先</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Filters
# -----------------------------
with st.container():
    st.markdown("### 🎛️ 先调一下你的等待视角")
    c1, c2 = st.columns(2)
    with c1:
        person = st.multiselect("互动对象", sorted(raw["Person"].dropna().unique()), default=sorted(raw["Person"].dropna().unique()))
        session_type = st.multiselect("互动类型", sorted(raw["Session_Type"].dropna().unique()), default=sorted(raw["Session_Type"].dropna().unique()))
    with c2:
        delay_order = ["正常区", "微崩区", "中崩区", "大崩区"]
        delay_level = st.multiselect("等待等级", delay_order, default=delay_order)
        slot_order = ["午场", "下午场", "晚场", "未知"]
        time_slot = st.multiselect("时间段", [x for x in slot_order if x in raw["Time_Slot"].unique()], default=[x for x in slot_order if x in raw["Time_Slot"].unique()])

filtered = raw[
    raw["Person"].isin(person)
    & raw["Session_Type"].isin(session_type)
    & raw["Delay_Level"].isin(delay_level)
    & raw["Time_Slot"].isin(time_slot)
].copy()

if filtered.empty:
    st.warning("这个筛选组合下没有数据。换个筛选条件看看，别把等待宇宙筛没了。")
    st.stop()

# -----------------------------
# 1. Opening / intro
# -----------------------------
section("1｜欢迎来到线下互动等待宇宙", "这里没有商业机密，只有排队、延迟、等待，以及一点点崩溃。")
snark("本报告的核心研究问题：我到底是去互动的，还是去练习耐心的？")
end_section()

# -----------------------------
# 2. KPI overview
# -----------------------------
section("2｜今日受害者总览", "先看大数字。每一个指标背后，都是一次‘快到了吧’的错觉。")
mean_wait = filtered["Waiting_Time_hr"].mean()
max_wait = filtered["Waiting_Time_hr"].max()
min_wait = filtered["Waiting_Time_hr"].min()
over_1 = (filtered["Waiting_Time_hr"] > 1).sum()
over_1_rate = (filtered["Waiting_Time_hr"] > 1).mean()
total_wait = filtered["Waiting_Time_hr"].sum()

m1, m2 = st.columns(2)
with m1:
    metric_card("平均等待时间", fmt_hr(mean_wait), "平均每次都要多等一段时间，属于‘已经习惯但还是会无语’的程度。")
with m2:
    metric_card("最惨一次", fmt_hr(max_wait), "不是等待，是一个完整下午的修行。")
m3, m4 = st.columns(2)
with m3:
    metric_card("最快一次", fmt_hr(min_wait), "原来准时真的存在，只是比较稀有。")
with m4:
    metric_card("超过 1 小时", f"{over_1} 次", f"占当前筛选数据的 {over_1_rate:.0%}，每一次都是对热爱的压力测试。")
end_section()

# -----------------------------
# 3. Person comparison
# -----------------------------
section("3｜人物对比：谁更容易让我等？", "讲李貌 vs 沫宸，看看谁更像本阶段‘时间黑洞’候选人。")
by_person = filtered.groupby("Person", as_index=False).agg(
    平均等待小时=("Waiting_Time_hr", "mean"),
    最大等待小时=("Waiting_Time_hr", "max"),
    超过一小时比例=("Severe_Delay", "mean"),
    场次数=("Waiting_Time_hr", "count"),
)
fig = px.bar(by_person, x="Person", y="平均等待小时", color="Person", text=by_person["平均等待小时"].map(lambda x: f"{x:.2f}h"), title="平均等待时间对比")
fig.update_traces(textposition="outside")
st.plotly_chart(plot_layout(fig), use_container_width=True)
if len(by_person) >= 2:
    worst = by_person.sort_values("平均等待小时", ascending=False).iloc[0]
    snark(f"从当前筛选数据看，<b>{worst['Person']}</b> 是本阶段‘时间黑洞’候选人，平均等待 <b>{worst['平均等待小时']:.2f} 小时</b>。见到本人之前，先通过耐心测试。")
else:
    one = by_person.iloc[0]
    snark(f"当前只看 <b>{one['Person']}</b>：平均等待 <b>{one['平均等待小时']:.2f} 小时</b>，样本数 {int(one['场次数'])} 场。")
end_section()

# -----------------------------
# 4. Top 5 worst waits
# -----------------------------
section("4｜最惨排行榜 Top 5", "这几场建议单独载入史册：不是互动，是耐力项目。")
top5 = filtered.sort_values("Waiting_Time_hr", ascending=False).head(5).reset_index(drop=True)
for i, row in top5.iterrows():
    st.markdown(
        f"""
        <div class="rank-card">
          <div class="rank-title">Top {i+1}｜{row['Person']}｜{row['Date_Display']}｜等待 {row['Waiting_Time_hr']:.2f}h</div>
          <div class="rank-meta">{row['Start_Time']} - {row['End_Time']}｜{row['Session_Type']}｜领到的号：{'' if pd.isna(row['Queue_Number']) else int(row['Queue_Number'])}｜备注：{row['Notes'] or '无'}</div>
          <div class="rank-snark">{rank_snark(row, i+1)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
end_section()

# -----------------------------
# 5. Delay level distribution
# -----------------------------
section("5｜等待等级分布", "把等待分成四个区：正常区、微崩区、中崩区、大崩区。")
level_order = ["正常区", "微崩区", "中崩区", "大崩区"]
level_df = filtered.groupby(["Delay_Level", "Person"], as_index=False).size()
level_df["Delay_Level"] = pd.Categorical(level_df["Delay_Level"], categories=level_order, ordered=True)
level_df = level_df.sort_values("Delay_Level")
fig = px.bar(level_df, x="Delay_Level", y="size", color="Person", barmode="group", title="等待等级分布")
st.plotly_chart(plot_layout(fig), use_container_width=True)
snark("0–0.5h 是正常区，0.5–1h 是微崩区，1–2h 是中崩区，2h+ 是大崩区。超过 2 小时，建议自动解锁‘等待大师’称号。")
end_section()

# -----------------------------
# 6. Queue number metaphysics
# -----------------------------
section("6｜排队号玄学研究", "排队号越大，真的越惨吗？理论上每个号 3 分钟，现实中每个号可能附带随机剧情。")
queue_df = filtered.dropna(subset=["Queue_Number"]).copy()
if not queue_df.empty:
    fig = px.scatter(
        queue_df,
        x="Queue_Number",
        y="Waiting_Time_hr",
        color="Person",
        symbol="Session_Type",
        size="Waiting_Time_min",
        hover_data=["Date_Display", "Start_Time", "End_Time", "Actual_Time", "Notes"],
        trendline="ols" if len(queue_df) >= 3 else None,
        title="领到的号 vs 等待时间",
    )
    st.plotly_chart(plot_layout(fig), use_container_width=True)
    corr = queue_df[["Queue_Number", "Waiting_Time_hr"]].corr().iloc[0, 1] if len(queue_df) >= 2 else float("nan")
    snark(f"当前筛选下，排队号和等待时间的相关系数约为 <b>{corr:.2f}</b>。排队号只是开始，等待时间才是命运。")
else:
    st.info("当前筛选下没有可用的排队号数据。")
end_section()

# -----------------------------
# 7. Single vs double
# -----------------------------
section("7｜单人 vs 双人研究", "双人互动听起来更幸福，但排队体验可能也更考验心态。")
by_type = filtered.groupby("Session_Type", as_index=False).agg(平均等待小时=("Waiting_Time_hr", "mean"), 场次数=("Waiting_Time_hr", "count"))
fig = px.bar(by_type, x="Session_Type", y="平均等待小时", color="Session_Type", text=by_type["平均等待小时"].map(lambda x: f"{x:.2f}h"), title="单人/双人平均等待对比")
fig.update_traces(textposition="outside")
st.plotly_chart(plot_layout(fig), use_container_width=True)
if len(by_type) > 1:
    slower = by_type.sort_values("平均等待小时", ascending=False).iloc[0]
    snark(f"当前数据里，<b>{slower['Session_Type']}</b> 平均等待更久，约 <b>{slower['平均等待小时']:.2f} 小时</b>。当然样本量也要看，玄学不能完全替代统计学。")
else:
    snark("当前筛选下只有一种互动类型，所以暂时不能公平比较。")
end_section()

# -----------------------------
# 8. Timeline
# -----------------------------
section("8｜我的等待情绪走势图", "每一个点，都是一次‘是不是快到了’的心理波动。")
timeline = filtered.sort_values(["Date_dt", "Start_dt"])
fig = px.line(
    timeline,
    x="Date_dt",
    y="Waiting_Time_hr",
    color="Person",
    markers=True,
    hover_data=["Date_Display", "Session_Type", "Queue_Number", "Start_Time", "Actual_Time", "Notes"],
    title="按日期查看等待时间变化",
)
fig.update_xaxes(tickformat="%m/%d")
st.plotly_chart(plot_layout(fig), use_container_width=True)
end_section()

# -----------------------------
# 9. Total wait converter
# -----------------------------
section("9｜总等待时间换算器", "把等待时间换成更有画面感的单位，方便发给朋友一起沉默。")
movie = movie_equiv(total_wait)
tea = milk_tea_equiv(total_wait)
songs = song_equiv(total_wait)
drama = drama_equiv(total_wait)
c1, c2 = st.columns(2)
with c1:
    metric_card("累计等待", fmt_hr(total_wait), "这是当前筛选条件下，你贡献给等待宇宙的总时长。")
with c2:
    metric_card("约等于电影", f"{movie:.1f} 部", "按每部电影 2 小时粗略换算。")
c3, c4 = st.columns(2)
with c3:
    metric_card("约等于奶茶", f"{tea:.0f} 杯", "按每小时可以喝 2 杯奶茶的精神速度换算。")
with c4:
    metric_card("约等于歌曲", f"{songs:.0f} 首", "按每首歌 4 分钟计算，足够开一场私人歌单马拉松。")
snark(f"你累计等待了 <b>{total_wait:.2f} 小时</b>，约等于看完 <b>{movie:.1f}</b> 部电影、刷完 <b>{drama:.1f}</b> 集综艺，或者听完 <b>{songs:.0f}</b> 首歌。数据会说话，等待会沉默。")
end_section()

# -----------------------------
# 10. Final card
# -----------------------------
section("10｜本次等待研究结论", "最后，用一张适合截图的结论卡收尾。")
most_common_level = filtered["Delay_Level"].value_counts().idxmax()
final_line = f"当前最常见的等待等级是 <b>{most_common_level}</b>，平均等待 <b>{mean_wait:.2f} 小时</b>。"
st.markdown(
    f"""
    <div class="final-card">
    综合来看，这份数据证明了一件事：<br>
    <b>爱可以让人排队，但数据会记录一切。</b><br><br>
    {final_line}<br><br>
    如果下次还要去，我建议：<br>
    1. 带充电宝；<br>
    2. 带吃的；<br>
    3. 不要太相信预计时间；<br>
    4. 提前做好“等待 1 小时起步”的心理建设。<br><br>
    研究结论：互动是短暂的，等待是漫长的，但截图发朋友吐槽是永恒的。
    </div>
    """,
    unsafe_allow_html=True,
)
end_section()

with st.expander("📄 查看当前筛选后的原始数据"):
    show_cols = ["Person", "Date_Display", "Start_Time", "End_Time", "Session_Type", "Queue_Number", "Actual_Time", "Expected_Time", "Waiting_Time_hr", "Waiting_Time_min", "Delay_Level", "Time_Slot", "Notes"]
    st.dataframe(filtered[show_cols].rename(columns={"Date_Display":"Date"}), use_container_width=True, hide_index=True)

st.caption("Made for fun. 非官方、非严肃、但每一分钟都是真实等待。")
