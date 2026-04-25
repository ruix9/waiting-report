
import os
import math

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="我到底等了多久？",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --card-bg: rgba(255, 255, 255, 0.84);
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
    .note-box {
        background: rgba(255,255,255,.75);
        border: 1px dashed rgba(255, 143, 171, .48);
        border-radius: 18px;
        color: #6a5e77;
        padding: .85rem .95rem;
        line-height: 1.7;
        margin: .7rem 0 1rem 0;
        font-size: .96rem;
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
    .persona-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(245,251,255,0.92));
        border: 1px solid rgba(142, 202, 230, .30);
        border-radius: 22px;
        padding: 1rem;
        min-height: 190px;
        box-shadow: 0 10px 26px rgba(142, 202, 230, 0.12);
    }
    .persona-name { font-size: 1.25rem; font-weight: 900; color: #2f2639; margin-bottom: .35rem; }
    .persona-tag { display: inline-block; padding: .26rem .62rem; border-radius: 999px; background: #fff1f5; color: #7a4052; font-size: .85rem; margin-bottom: .65rem; }
    .persona-text { color: #5f536d; line-height: 1.7; }
    .final-card {
        padding: 1.25rem;
        border-radius: 26px;
        background: linear-gradient(135deg, #fff1f5 0%, #e8f8ff 100%);
        border: 1px solid rgba(255, 143, 171, .30);
        box-shadow: 0 18px 44px rgba(255, 143, 171, 0.15);
        line-height: 1.9;
        font-size: 1.04rem;
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
    path_candidates = [
        DATA_FILE,
        os.path.join(os.path.dirname(__file__), DATA_FILE),
        "/mnt/data/interaction_data(1).xlsx",
        "/mnt/data/interaction_data.xlsx",
    ]
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

    mask = df["Actual_dt"] < df["Start_dt"]
    df.loc[mask, "Actual_dt"] = df.loc[mask, "Actual_dt"] + pd.Timedelta(days=1)

    df["Expected_dt"] = df["Actual_dt"] - pd.to_timedelta(df["Waiting_Time_min"], unit="m")
    df["Expected_Time"] = df["Expected_dt"].dt.strftime("%H:%M")
    df["Start_Hour"] = df["Start_dt"].dt.hour + df["Start_dt"].dt.minute / 60

    def time_slot(h):
        if pd.isna(h):
            return "未知"
        if h < 14:
            return "午场"
        if h < 17:
            return "下午场"
        return "晚场"

    def wait_level(x):
        if x < 0.5:
            return "🙂 还不错"
        if x < 1:
            return "😐 开始漫长"
        if x < 2:
            return "😶 有点久了"
        return "😵 已经放空"

    df["Time_Slot"] = df["Start_Hour"].apply(time_slot)
    df["Wait_Level"] = df["Waiting_Time_hr"].apply(wait_level)
    df["Severe_Delay"] = df["Waiting_Time_hr"] > 1
    df["Record_Label"] = df["Person"] + "｜" + df["Date_Display"] + "｜" + df["Start_Time"].astype(str) + "-" + df["End_Time"].astype(str)
    return df


def fmt_hr(x):
    if pd.isna(x):
        return "-"
    return f"{x:.2f}h"


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


def rank_snark(row):
    wait = row["Waiting_Time_hr"]
    if wait >= 3:
        return "这一次多等了 3 小时，已经可以完整经历：看时间 → 刷手机 → 再看时间 → 接受现实。"
    if wait >= 2.2:
        return "这一场属于等待界的加长版，时间长到奶茶都可以从冰变常温。"
    if wait >= 2:
        return "这个时长已经很有存在感，足够让人把附近路线都研究一遍。"
    if wait >= 1.5:
        return "已经进入‘我是不是可以先去转一圈再回来’的心理阶段。"
    if wait >= 1:
        return "超过一小时，属于会让人开始认真计算手机电量的程度。"
    return "虽然没到大场面，但也足够让人多看几次时间。"


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

st.markdown(
    """
    <div class="hero">
      <div class="hero-title">我到底等了多久？</div>
      <div class="hero-subtitle">线下互动等待实录｜一份不完全理性、但很真实的等待小报告</div>
      <div class="pill-row">
        <span class="pill">⏳ 等待宇宙</span>
        <span class="pill">💗 小红书风</span>
        <span class="pill">🤡 轻吐槽</span>
        <span class="pill">📱 手机优先</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="note-box">
    <b>小说明：</b><br>
    这里的“等待时间”，不是正常排队要等的时间，<br>
    而是“感觉差不多该轮到你了，但又没轮到”的那一段 🙂<br><br>
    简单说：都是那些开始反复看时间的瞬间。
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown("### 🎛️ 先调一下你的等待视角")
    c1, c2 = st.columns(2)
    with c1:
        person = st.multiselect("互动对象", sorted(raw["Person"].dropna().unique()), default=sorted(raw["Person"].dropna().unique()))
        session_type = st.multiselect("互动类型", sorted(raw["Session_Type"].dropna().unique()), default=sorted(raw["Session_Type"].dropna().unique()))
    with c2:
        level_order = ["🙂 还不错", "😐 开始漫长", "😶 有点久了", "😵 已经放空"]
        wait_level = st.multiselect("等待等级", level_order, default=level_order)
        slot_order = ["午场", "下午场", "晚场", "未知"]
        time_slot = st.multiselect(
            "时间段",
            [x for x in slot_order if x in raw["Time_Slot"].unique()],
            default=[x for x in slot_order if x in raw["Time_Slot"].unique()],
        )

filtered = raw[
    raw["Person"].isin(person)
    & raw["Session_Type"].isin(session_type)
    & raw["Wait_Level"].isin(wait_level)
    & raw["Time_Slot"].isin(time_slot)
].copy()

if filtered.empty:
    st.warning("这个筛选组合下没有数据。换个筛选条件看看，别把等待宇宙筛没了。")
    st.stop()

section("1｜欢迎来到线下互动等待宇宙", "一开始只是觉得有点久，后来发现，好像每次都不短。")
snark("本报告的核心问题：我到底是去互动的，还是去顺便练习时间管理的？")
end_section()

section("2｜今日等待总览", "先看大数字。每一个指标背后，都是一次“应该差不多了吧”的循环。")
mean_wait = filtered["Waiting_Time_hr"].mean()
max_wait = filtered["Waiting_Time_hr"].max()
min_wait = filtered["Waiting_Time_hr"].min()
over_1 = (filtered["Waiting_Time_hr"] > 1).sum()
over_1_rate = (filtered["Waiting_Time_hr"] > 1).mean()
total_wait = filtered["Waiting_Time_hr"].sum()

m1, m2 = st.columns(2)
with m1:
    metric_card("平均等待时间", fmt_hr(mean_wait), "平均每次多等了这么久，属于那种：明明已经提前算好了时间，结果还是不够用的情况。")
with m2:
    metric_card("最久一次", fmt_hr(max_wait), "最多多等了这么久，时间长到可以从“马上就到”变成“那也不着急了”。")
m3, m4 = st.columns(2)
with m3:
    metric_card("最快一次", fmt_hr(min_wait), "也有几次几乎没多等，说明“刚刚好轮到”这种事，确实发生过。")
with m4:
    metric_card("超过 1 小时", f"{over_1} 次", f"占当前筛选数据的 {over_1_rate:.0%}，基本经历了好几轮“应该差不多了吧”的循环。")
end_section()

section("3｜等待时间 Top 5", "都有点记忆点。Top 5 的共同特点是：等的时候很长，回头看又有点好笑。")
top5 = filtered.sort_values("Waiting_Time_hr", ascending=False).head(5).reset_index(drop=True)
for i, row in top5.iterrows():
    queue_text = "无" if pd.isna(row["Queue_Number"]) else str(int(row["Queue_Number"]))
    st.markdown(
        f"""
        <div class="rank-card">
          <div class="rank-title">Top {i+1}｜{row['Person']}｜{row['Date_Display']}｜等待 {row['Waiting_Time_hr']:.2f}h</div>
          <div class="rank-meta">{row['Start_Time']} - {row['End_Time']}｜{row['Session_Type']}｜领到的号：{queue_text}｜备注：{row['Notes'] or '无'}</div>
          <div class="rank-snark">{rank_snark(row)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
end_section()

section("4｜等待等级分布", "把等待分成四个状态：还不错、开始漫长、有点久了、已经放空。")
level_df = filtered.groupby(["Wait_Level", "Person"], as_index=False).size()
level_df["Wait_Level"] = pd.Categorical(level_df["Wait_Level"], categories=level_order, ordered=True)
level_df = level_df.sort_values("Wait_Level")
fig = px.bar(level_df, x="Wait_Level", y="size", color="Person", barmode="group", title="等待等级分布")
st.plotly_chart(plot_layout(fig), use_container_width=True)
snark("大部分时间其实还在可接受范围，但偶尔也会进入一种“我已经不知道自己在等什么了”的状态。")
end_section()

section("5｜总等待时间换算器", "把等待时间换成更有画面感的单位，方便发给朋友一起沉默三秒。")
days = total_wait / 24
movies = total_wait / 2
milk_tea = total_wait / 0.75
mall_laps = total_wait / 0.35
c1, c2 = st.columns(2)
with c1:
    metric_card("累计等待", fmt_hr(total_wait), "这是当前筛选条件下，你贡献给等待宇宙的总时长。")
with c2:
    metric_card("约等于", f"{days:.2f} 天", "如果换成天数，也是一段很完整的时间了。")
c3, c4 = st.columns(2)
with c3:
    metric_card("约等于电影", f"{movies:.1f} 部", "按每部电影 2 小时粗略换算。")
with c4:
    metric_card("约等于奶茶变常温", f"{milk_tea:.0f} 杯", "按一杯冰奶茶 45 分钟逐渐失去灵魂粗略换算。")
snark(
    f"""
    到目前为止，<br>
    你一共多等了 <b>{total_wait:.2f} 小时</b><br><br>
    ≈ <b>{days:.2f}</b> 天<br>
    ≈ <b>{movies:.1f}</b> 部电影<br>
    ≈ <b>{milk_tea:.0f}</b> 杯奶茶从冰变常温的时间<br>
    ≈ 在商场里走到不知道第 <b>{mall_laps:.0f}</b> 圈的程度<br><br>
    （也≈ 一些本可以更早见到他们的时间）
    """
)
end_section()

section("6｜单人 vs 双人研究", "人多，真的会更慢吗？")
by_type = filtered.groupby("Session_Type", as_index=False).agg(平均等待小时=("Waiting_Time_hr", "mean"), 场次数=("Waiting_Time_hr", "count"))
fig = px.bar(by_type, x="Session_Type", y="平均等待小时", color="Session_Type", text=by_type["平均等待小时"].map(lambda x: f"{x:.2f}h"), title="单人/双人平均等待对比")
fig.update_traces(textposition="outside")
st.plotly_chart(plot_layout(fig), use_container_width=True)
if len(by_type) > 1:
    slower = by_type.sort_values("平均等待小时", ascending=False).iloc[0]
    snark(f"直觉告诉我们：人多应该更热闹。数据告诉我们：<b>{slower['Session_Type']}</b> 的平均等待更久一点。毕竟两个人，总比一个人更难结束对话一点点。")
else:
    snark("当前筛选下只有一种互动类型，所以暂时不能公平比较。")
end_section()

section("7｜我的等待情绪走势图", "每一个点，都是一次“快到了吧”的判断。有的对了，有的……再等等。")
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

section("8｜人物对比：是不是哪里不太对？", "后来越看越觉得不太对：这些等待，真的只是时间问题吗？")
by_person = filtered.groupby("Person", as_index=False).agg(
    平均等待小时=("Waiting_Time_hr", "mean"),
    最大等待小时=("Waiting_Time_hr", "max"),
    超过一小时比例=("Severe_Delay", "mean"),
    波动程度=("Waiting_Time_hr", "std"),
    场次数=("Waiting_Time_hr", "count"),
)
by_person["波动程度"] = by_person["波动程度"].fillna(0)

if len(by_person) >= 2:
    avg_winner = by_person.sort_values("平均等待小时", ascending=False).iloc[0]
    stable_winner = by_person.sort_values("波动程度", ascending=True).iloc[0]
    snark(
        f"""
        如果一定要总结的话：<br><br>
        更容易让人多等一点的是：<b>{avg_winner['Person']}</b><br>
        更稳定一点的是：<b>{stable_winner['Person']}</b><br><br>
        一个是“偶尔会突然慢很多”，一个是“节奏更可预期一点”。
        """
    )

pcols = st.columns(2)
for idx, (_, row) in enumerate(by_person.sort_values("Person").iterrows()):
    name = row["Person"]
    if "讲" in name:
        tag = "稳定输出型"
        text = "不会特别离谱，但基本不会完全不慢。属于那种：“今天应该也差不多会等一下”的类型。"
    elif "沫" in name:
        tag = "随机波动型"
        text = "平时还好，但偶尔会直接进入“时间加长模式”。有一点点开盲盒的感觉。"
    else:
        tag = "等待宇宙成员"
        text = "样本不多，但每一条记录都有自己的故事。"
    with pcols[idx % 2]:
        st.markdown(
            f"""
            <div class="persona-card">
              <div class="persona-name">👤 {name}</div>
              <div class="persona-tag">{tag}</div>
              <div class="persona-text">
                平均等待：<b>{row['平均等待小时']:.2f}h</b><br>
                最久一次：<b>{row['最大等待小时']:.2f}h</b><br>
                超过 1 小时比例：<b>{row['超过一小时比例']:.0%}</b><br><br>
                {text}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

fig = px.bar(
    by_person,
    x="Person",
    y="平均等待小时",
    color="Person",
    text=by_person["平均等待小时"].map(lambda x: f"{x:.2f}h"),
    title="谁更容易让人多等一点",
)
fig.update_traces(textposition="outside")
st.plotly_chart(plot_layout(fig), use_container_width=True)

compare_long = by_person.melt(
    id_vars="Person",
    value_vars=["最大等待小时", "波动程度"],
    var_name="指标",
    value_name="小时",
)
fig = px.bar(compare_long, x="指标", y="小时", color="Person", barmode="group", title="谁更容易突然变久 / 谁更稳定一点")
st.plotly_chart(plot_layout(fig), use_container_width=True)

fig = px.bar(
    by_person,
    x="Person",
    y="超过一小时比例",
    color="Person",
    text=by_person["超过一小时比例"].map(lambda x: f"{x:.0%}"),
    title="超过 1 小时比例对比",
)
fig.update_traces(textposition="outside")
fig.update_yaxes(tickformat=".0%")
st.plotly_chart(plot_layout(fig), use_container_width=True)
end_section()

section("9｜本次等待小结", "最后，用一张适合截图的结论卡收尾。")
most_common_level = filtered["Wait_Level"].value_counts().idxmax()
final_line = f"当前最常见的等待状态是 <b>{most_common_level}</b>，平均等待 <b>{mean_wait:.2f} 小时</b>。"
st.markdown(
    f"""
    <div class="final-card">
    综合来看，这份数据证明了一件事：<br><br>
    <b>爱可以让人排队，<br>
    但数据会记录一切。</b><br><br>
    {final_line}<br><br>
    不过好像也还好，<br>
    毕竟最后，<br>
    还是等到了。<br><br>
    但如果真的要说的话，<br>
    这些时间，<br>
    也不只是“等”。<br><br>
    它们更像是：<br>
    一次次在人群里慢慢靠近的过程。<br><br>
    所以好像也没有那么浪费。
    </div>
    """,
    unsafe_allow_html=True,
)
end_section()

with st.expander("📄 查看当前筛选后的原始数据"):
    show_cols = [
        "Person", "Date_Display", "Start_Time", "End_Time", "Session_Type",
        "Queue_Number", "Actual_Time", "Expected_Time", "Waiting_Time_hr",
        "Waiting_Time_min", "Wait_Level", "Time_Slot", "Notes"
    ]
    st.dataframe(filtered[show_cols].rename(columns={"Date_Display": "Date", "Wait_Level": "等待等级"}), use_container_width=True, hide_index=True)

st.caption("Made for fun. 非官方、非严肃、但每一分钟都是真实等待。")
