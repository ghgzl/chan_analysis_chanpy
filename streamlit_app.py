# -*- coding: utf-8 -*-
"""
缠论分析网页版（Streamlit）—— chan.py 引擎版
功能：
  1. 自由输入股票名称或代码（支持模糊匹配）
  2. 自由输入开始/结束时间（默认 2024-01-01 ~ 最新交易日）
  3. K线不足 600 根给出提醒
  4. ECharts 交互式K线图：dataZoom 滚轮缩放 + 滑块 + 双击复位
  5. 引擎为 chan.py（经典纯 Python 缠论框架）：分型/笔/线段/中枢/三类买卖点/背驰
部署：Streamlit Community Cloud（免费，绑 GitHub 自动更新）
"""
import pandas as pd
import streamlit as st

from chan_core import (
    DEFAULT_START, MIN_K_LINES,
    get_bars_df, check_bei_chi, format_bsp_type,
    get_stock_map, resolve_symbol,
    run_chan, make_kline_option, ctime_str,
)
from Common.CEnum import BI_DIR

# ==================== 页面基础配置 ====================
st.set_page_config(
    page_title="缠论分析 · chan.py 版",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 缓存股票映射表（每日刷新）
get_stock_map_cached = st.cache_data(ttl=86400, show_spinner=False)(get_stock_map)


# ==================== 主界面 ====================
st.title("📈 缠论分析 · chan.py 版")
st.caption("引擎：chan.py（经典纯 Python 缠论框架）· 数据源：akshare(东财) → yfinance 兜底")

with st.sidebar:
    st.header("⚙️ 分析参数")
    symbol_input = st.text_input(
        "股票名称 / 代码",
        placeholder="例：京东方A、000725、中国平安、601318",
    )
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("开始日期", value=pd.Timestamp(DEFAULT_START).date())
    with date_col2:
        end_date = st.date_input("结束日期", value=pd.Timestamp.today().date())
    analyze_btn = st.button("🚀 开始分析", type="primary", use_container_width=True)

    st.divider()
    st.caption("提示：K线少于 600 根会提醒（默认 2024-01-01 至今约 660+ 个交易日，通常满足）")

if not symbol_input:
    st.info("👈 在左侧输入股票名称或代码，设置起止日期，点击「开始分析」")
    st.stop()

if not analyze_btn:
    st.info("👈 输入已完成，点击左侧「🚀 开始分析」运行缠论分析")
    st.stop()

if start_date >= end_date:
    st.error("开始日期必须早于结束日期")
    st.stop()

# ---- 解析输入 ----
resolved = resolve_symbol(symbol_input, get_stock_map_cached())
if resolved is None:
    st.error(f"未找到「{symbol_input}」对应的股票，请检查名称或直接输入 6 位代码（如 000725）")
    st.stop()
if resolved[0] == "multi":
    code, cands, kind = resolved
    st.warning(f"「{symbol_input}」匹配到多个结果，请选择：")
    labels = {f"{c} · {n}": c for c, n in cands}
    pick = st.selectbox("候选列表", list(labels.keys()))
    code, name, kind = labels[pick], pick.split(" · ")[1], "stock"
else:
    code, name, kind = resolved
    if name is None:
        # 纯代码输入，查名称
        try:
            dfm = get_stock_map_cached()
            row = dfm[dfm["code"] == code]
            name = row.iloc[0]["name"] if not row.empty else code
        except Exception:
            name = code

st.subheader(f"🔍 {name}（{code}）　{kind.upper()}")

# ---- 拉取数据 ----
with st.status(f"正在获取 {name}（{code}）数据…", expanded=True) as status:
    st.write(f"区间：{start_date} ~ {end_date}")
    try:
        df = get_bars_df(code, kind, str(start_date), str(end_date))
        status.update(label=f"✅ 数据获取成功：{len(df)} 根K线", state="complete")
    except Exception as e:
        status.update(label="❌ 数据获取失败", state="error")
        st.error(f"{type(e).__name__}: {str(e)}")
        st.stop()

# ---- 600 根提醒 ----
if len(df) < MIN_K_LINES:
    st.warning(f"⚠️ 当前仅 {len(df)} 根 K 线，不足 {MIN_K_LINES} 根。"
               f"建议把开始日期提前（如 {DEFAULT_START}），以获得更充分的缠论结构。")
else:
    st.success(f"✅ K 线数量 {len(df)} 根，满足 {MIN_K_LINES} 根要求。")

# ---- 缠论分析（chan.py） ----
with st.status("正在进行 chan.py 缠论分析…", expanded=True) as status:
    try:
        kl_list, chan = run_chan(df, code, kind, str(start_date), str(end_date))
        status.update(label="✅ 缠论分析完成", state="complete")
    except Exception as e:
        status.update(label="❌ 缠论分析失败", state="error")
        import traceback
        st.error(f"{type(e).__name__}: {str(e)}\n\n```\n{traceback.format_exc()[-1500:]}\n```")
        st.stop()

# ---- 结果指标 ----
bis = kl_list.bi_list
zss = kl_list.zs_list
bsps = kl_list.bs_point_lst.getSortedBspList()
bc_msg, _, _ = check_bei_chi(kl_list)

last_bi = bis[-1] if bis else None
bi_info = "无"
if last_bi:
    b_klu = last_bi.get_begin_klu()
    e_klu = last_bi.get_end_klu()
    bi_info = (f"{'上涨' if last_bi.dir == BI_DIR.UP else '下跌'} | "
               f"{ctime_str(b_klu.time)}~{ctime_str(e_klu.time)} | "
               f"{last_bi.get_begin_val():.2f} → {last_bi.get_end_val():.2f}")

buy_pts = [format_bsp_type(b) for b in bsps if b.is_buy]
sell_pts = [format_bsp_type(b) for b in bsps if not b.is_buy]
pt_msg = f"买{len(buy_pts)} 卖{len(sell_pts)}"

m1, m2, m3, m4 = st.columns(4)
m1.metric("最新收盘价", f"{df.iloc[-1]['close']:.2f}")
m2.metric("有效K线数", f"{len(df)}")
m3.metric("笔 / 中枢", f"{len(bis)} / {len(zss)}")
m4.metric("买卖点", pt_msg)

st.markdown(f"**最新一笔走势**：{bi_info}")
st.markdown(f"**缠论背驰判断**：{bc_msg}")

# ---- 买卖点明细 ----
st.markdown("**chan.py 三类买卖点识别**")
if bsps:
    if buy_pts:
        col_list = st.columns(min(len(buy_pts), 6))
        for i, b in enumerate(buy_pts):
            with col_list[i % min(len(buy_pts), 6)]:
                st.markdown(f"🟢 {b}")
    if sell_pts:
        col_list2 = st.columns(min(len(sell_pts), 6))
        for i, s in enumerate(sell_pts):
            with col_list2[i % min(len(sell_pts), 6)]:
                st.markdown(f"🔴 {s}")
    with st.expander("📋 买卖点明细（含时间/价格）"):
        rows = []
        for bsp in bsps:
            t = ",".join(x.value for x in bsp.type)
            rows.append({
                "类型": "买" if bsp.is_buy else "卖",
                "级别": t,
                "日期": ctime_str(bsp.klu.time),
                "价格": round(bsp.klu.close, 3),
                "所在笔": bsp.bi.idx,
            })
        st.dataframe(pd.DataFrame(rows))
else:
    st.info("当前区间未识别到形态学买卖点（可能中枢结构不完整或笔数不足）")

# ---- 交互式K线图 ----
st.subheader("📊 K线图（滚轮/滑块缩放 · 双击复位）")
try:
    from streamlit_echarts import st_echarts
    option = make_kline_option(df, kl_list, name, code, pt_msg, bc_msg)
    st_echarts(options=option, height="620px")
except ImportError:
    st.warning("streamlit-echarts 未安装，图表降级显示。请安装后刷新。")
    st.dataframe(df.tail(20))
except Exception as e:
    st.error(f"图表渲染失败：{type(e).__name__}: {str(e)}")

st.divider()
with st.expander("📄 原始数据预览（最近 10 条）"):
    st.dataframe(df.tail(10))
