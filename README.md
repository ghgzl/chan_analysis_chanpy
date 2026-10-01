# 缠论分析 · chan.py 网页版

基于 **chan.py**（经典纯 Python 缠论框架）的 A 股缠论分析网页应用，可部署到 **Streamlit Community Cloud（免费）** 或本地运行。

## 功能

- 自由输入**股票名称或代码**（支持模糊匹配，如「京东方A」「000725」「中国平安」）
- 自由输入**开始/结束时间**（默认 2024-01-01 ~ 最新交易日）
- **K 线不足 600 根提醒**
- **K 线图局部放大/缩小**：滚轮缩放 + 底部滑块 + 双击复位
- 缠论分析（chan.py 引擎）：笔 / 线段 / 中枢 / **三类买卖点** / **背驰判断**
- 数据源：akshare(东财) → yfinance 兜底（海外服务器可用）

## 目录结构

```
chan_analysis_chanpy/
├── streamlit_app.py      # 网页主程序
├── requirements.txt      # Python 依赖
├── start.bat             # Windows 一键启动
└── chanlib/              # vendored chan.py 源码（chanpy/chan.py）
    ├── Chan.py
    ├── ChanConfig.py
    ├── DataAPI/
    │   ├── YfDataSrc.py  # ★ 自定义数据源：akshare→yfinance
    │   └── ...
    └── ...
```

> chan.py 没有 PyPI 包（PyPI 上的 `chanpy` 是无关的 CSP 库），因此把源码随仓库 vendored，保证部署与本地一致。

## 本地运行（Windows）

1. 安装 [Python 3.11+](https://www.python.org/downloads/)（安装时勾选 **Add Python to PATH**）
2. 双击 `start.bat`，自动安装依赖并启动，浏览器自动打开 http://localhost:8501
3. 或手动运行：
   ```
   pip install -r requirements.txt
   streamlit run streamlit_app.py
   ```

## 部署到 Streamlit Cloud（免费，¥0）

1. 把本目录推送到你的 GitHub 仓库（Public）
2. 打开 https://share.streamlit.io → **Create app**
3. 选择仓库、分支 `main`、主文件 `streamlit_app.py` → **Deploy**
4. 完成。以后每次 push 代码自动更新。

## 数据源说明

- **yfinance（Yahoo）**：海外服务器首选（Streamlit Cloud 环境）
- **akshare（东方财富 → 新浪）**：本地/国内网络优先

## 与 czsc 版的关系

本应用由 `chan_analysis_web`（czsc 0.9.51 版）改造而来，UI/数据源/可视化框架完全复用，
仅把缠论计算层替换为 chan.py（`CChan` → `bi_list / zs_list / bs_point_lst`）。
背驰判断沿用原 chan_analysis.py 口径（最后两笔幅度对比），买卖点使用 chan.py 原生形态学识别。
