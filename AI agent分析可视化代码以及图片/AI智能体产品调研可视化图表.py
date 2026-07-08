"""
AI智能体平台横向对比 - Python可视化代码
======================================
依赖：pandas, numpy, matplotlib
说明：本脚本只提供基础图表框架，配色、字体、标注、个人分析结论请自行调优
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# ========== 1. 基础配置（按需调整字体/分辨率/DPI） ==========
# macOS系统可改为 "PingFang SC"；Windows改为 "Microsoft YaHei"
rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
rcParams["axes.unicode_minus"] = False
rcParams["figure.dpi"] = 150
rcParams["savefig.dpi"] = 200
rcParams["savefig.bbox"] = "tight"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ========== 2. 读取数据 ==========
score_path = os.path.join(OUT_DIR, "01_五维综合评分.csv")
detail_path = os.path.join(OUT_DIR, "02_核心指标明细.csv")
df_score = pd.read_csv(score_path)
df_detail = pd.read_csv(detail_path)

DIMS = ["核心能力", "易用部署", "生态场景", "成本风控", "人群落地"]
PLATFORMS = df_score["平台"].tolist()
SCORES = df_score[DIMS].values  # shape (5,5)

# ========== 3. 图1：五维能力雷达图 ==========
def plot_radar():
    N = len(DIMS)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # 闭合

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#9B59B6"]

    for idx, (name, scores) in enumerate(zip(PLATFORMS, SCORES)):
        values = scores.tolist() + [scores[0]]
        ax.plot(angles, values, "o-", linewidth=2, label=name, color=colors[idx])
        ax.fill(angles, values, alpha=0.10, color=colors[idx])

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(DIMS, fontsize=11)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=8, color="gray")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_title("五款AI智能体平台·五维能力雷达图（10分制）", fontsize=14, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.10), fontsize=9)

    out = os.path.join(OUT_DIR, "radar.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] 雷达图已保存：{out}")

# ========== 4. 图2：场景适配柱状图（加权总分对比） ==========
def plot_bar_total():
    fig, ax = plt.subplots(figsize=(9, 5))
    totals = df_score["加权总分"].values
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#9B59B6"]
    bars = ax.bar(PLATFORMS, totals, color=colors, width=0.55, edgecolor="white")

    for bar, val in zip(bars, totals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.05, f"{val:.1f}",
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylim(0, 10)
    ax.set_ylabel("加权总分（10分制）", fontsize=11)
    ax.set_title("五款AI智能体平台·综合能力总分对比", fontsize=14, pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    out = os.path.join(OUT_DIR, "bar_total.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] 总分柱状图已保存：{out}")

# ========== 5. 图3：场景适配分组柱状图（按维度对比） ==========
def plot_bar_dimension():
    fig, ax = plt.subplots(figsize=(20, 8))
    x = np.arange(len(DIMS))
    n = len(PLATFORMS)
    width = 0.15
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#9B59B6"]

    for i, (name, color) in enumerate(zip(PLATFORMS, colors)):
        offset = (i - n / 2 + 0.5) * width
        ax.bar(x + offset, SCORES[i], width, label=name, color=color, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(DIMS, fontsize=11)
    ax.set_ylim(0, 10)
    ax.set_ylabel("评分（10分制）", fontsize=11)
    ax.set_title("五款AI智能体平台·五大维度分项对比", fontsize=14, pad=12)
    ax.legend(loc="upper right", fontsize=9, ncol=5)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    out = os.path.join(OUT_DIR, "bar_dimension.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] 维度分项柱状图已保存：{out}")

# ========== 6. 图4：核心指标横向对比（上下文窗口/RAG/插件数） ==========
def plot_bar_core_metrics():
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    metrics = [
        ("上下文窗口K", "上下文窗口大小（K Tokens）", "#45B7D1"),
        ("RAG准确率pct", "RAG检索准确率（%）", "#4ECDC4"),
        ("工具调用插件数", "插件/工具数量（个）", "#FFA07A"),
    ]
    for ax, (col, title, color) in zip(axes, metrics):
        # 处理"模型无关""自带Key"等非数值：Dify上下文填1024做占位（可改）
        series = df_detail[col].copy()
        if col == "上下文窗口K":
            series = series.replace({"模型无关": 1024})
        if col == "工具调用插件数":
            series = series.replace({"-": 0})
        vals = pd.to_numeric(series, errors="coerce").fillna(0).values
        bars = ax.barh(df_detail["平台"], vals, color=color, edgecolor="white")
        for i, (bar, v, pname) in enumerate(zip(bars, vals, df_detail["平台"])):
            if col == "上下文窗口K" and pname == "Dify":
                label = "模型无关"
            elif col == "RAG准确率pct" and pname == "Dify":
                label = f"{int(v)}"
            elif col == "工具调用插件数" and pname in ["文心智能体", "通义百炼", "豆包"]:
                label = str(int(v)) if v > 0 else "少量"
            else:
                label = f"{int(v)}" if float(v).is_integer() else f"{v:.0f}"
            ax.text(v + max(vals) * 0.02, bar.get_y() + bar.get_height()/2,
                    label, va="center", fontsize=9)
        ax.set_title(title, fontsize=11)
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", alpha=0.4)
        ax.set_axisbelow(True)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
    plt.suptitle("五款AI智能体平台·核心硬指标对比", fontsize=14, y=1.02)
    plt.subplots_adjust(wspace=0.5)
    out = os.path.join(OUT_DIR, "bar_core_metrics.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] 核心指标横向对比图已保存：{out}")

# ========== 入口 ==========
if __name__ == "__main__":
    plot_radar()
    plot_bar_total()
    plot_bar_dimension()
    plot_bar_core_metrics()
    print("\n全部图表生成完毕，请自行调参配色、字体与标注。")
