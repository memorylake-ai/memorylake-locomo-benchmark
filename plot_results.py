"""
Generate LoCoMo benchmark comparison charts.
Outputs: benchmark_comparison.png
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

matplotlib.rcParams["figure.dpi"] = 150
matplotlib.rcParams["font.family"] = "DejaVu Sans"

# ── Data ──────────────────────────────────────────────────────────────────────

SYSTEMS = [
    "MemoryLake",
    "EverMemOS",
    "Full-context",
    "Zep",
    "MemOS",
    "MemU",
    "Mem0",
]

DATA = {
    #              single   multi   temporal  open    overall
    "MemoryLake":  [96.79,  91.84,  91.28,   85.42,  94.03],
    "EverMemOS":   [96.08,  91.13,  89.72,   70.83,  92.32],
    "Full-context":[94.93,  90.43,  87.95,   71.88,  91.21],
    "Zep":         [90.84,  81.91,  77.26,   75.00,  85.22],
    "MemOS":       [85.37,  79.43,  75.08,   64.58,  80.76],
    "MemU":        [74.91,  72.34,  43.61,   54.17,  66.67],
    "Mem0":        [68.97,  61.70,  58.26,   50.00,  64.20],
}

PER_RECORD = {
    "record":    ["R1",    "R2",    "R3",    "R4",    "R5",    "R6",    "R7",    "R8",    "R9",    "R10"],
    "single":    [100.00,  95.45,   96.51,   97.30,   96.26,   96.77,   98.80,   95.76,   94.52,   96.55],
    "multi":     [ 84.38, 100.00,   96.77,   94.59,   83.87,   86.67,  100.00,   85.71,   97.30,   93.75],
    "temporal":  [100.00, 100.00,   96.30,   92.50,   80.77,   87.50,   85.29,   97.62,   84.85,   84.38],
    "open":      [100.00,   None,   87.50,   72.73,   85.71,   42.86,   76.92,  100.00,   92.31,  100.00],
    "overall":   [ 96.71,  97.53,   96.05,   94.47,   91.01,   89.43,   94.00,   95.29,   92.95,   93.67],
}

CATEGORIES  = ["Single-hop", "Multi-hop", "Temporal", "Open-domain"]
CAT_KEYS    = ["single", "multi", "temporal", "open"]

# ── Color palette ─────────────────────────────────────────────────────────────

BG       = "#0f1117"
CARD_BG  = "#1a1f2e"
GRID_CLR = "#2a3045"
TEXT_CLR = "#e2e8f0"
MUTED    = "#64748b"

PALETTE = [
    "#38bdf8",   # MemoryLake  – sky blue
    "#a78bfa",   # EverMemOS   – purple
    "#fbbf24",   # Full-context – amber
    "#34d399",   # Zep          – emerald
    "#f87171",   # MemOS        – red
    "#94a3b8",   # MemU         – slate
    "#818cf8",   # Mem0         – indigo
]

# ── Canvas setup ─────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(18, 14), facecolor=BG)
fig.suptitle(
    "LoCoMo Benchmark  ·  MemoryLake vs. Memory Systems",
    fontsize=18, fontweight="bold", color=TEXT_CLR, y=0.98,
)

# 2×2 grid + bottom row (per-record line chart)
gs = fig.add_gridspec(
    3, 2,
    hspace=0.48, wspace=0.32,
    top=0.93, bottom=0.07,
    left=0.07, right=0.97,
    height_ratios=[1, 1, 0.9],
)

ax_overall  = fig.add_subplot(gs[0, 0])   # horizontal bar – overall
ax_grouped  = fig.add_subplot(gs[0, 1])   # grouped bar – per category
ax_radar    = fig.add_subplot(gs[1, 0], projection="polar")  # radar
ax_heat     = fig.add_subplot(gs[1, 1])   # heatmap
ax_line     = fig.add_subplot(gs[2, :])   # per-record line chart


def style_ax(ax, title):
    ax.set_facecolor(CARD_BG)
    ax.set_title(title, color=TEXT_CLR, fontsize=11, fontweight="bold", pad=10)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    ax.tick_params(colors=TEXT_CLR, labelsize=9)
    ax.xaxis.label.set_color(TEXT_CLR)
    ax.yaxis.label.set_color(TEXT_CLR)
    ax.grid(color=GRID_CLR, linewidth=0.6, zorder=0)


# ── 1. Horizontal bar – overall score ────────────────────────────────────────

style_ax(ax_overall, "Overall Score")
ax_overall.grid(axis="x", color=GRID_CLR, linewidth=0.6, zorder=0)
ax_overall.grid(axis="y", visible=False)

overall_scores = [DATA[s][4] for s in SYSTEMS]
y_pos = np.arange(len(SYSTEMS))
bars = ax_overall.barh(
    y_pos, overall_scores,
    color=PALETTE, edgecolor="none", height=0.6, zorder=3,
)
# Highlight MemoryLake bar with a glow edge
bars[0].set_edgecolor("#38bdf8")
bars[0].set_linewidth(1.5)

ax_overall.set_yticks(y_pos)
ax_overall.set_yticklabels(SYSTEMS, fontsize=9.5)
ax_overall.set_xlabel("F1 Score (%)", fontsize=9)
ax_overall.set_xlim(55, 102)
ax_overall.invert_yaxis()

# Value labels
for bar, score in zip(bars, overall_scores):
    ax_overall.text(
        score + 0.3, bar.get_y() + bar.get_height() / 2,
        f"{score:.2f}%", va="center", ha="left",
        color=TEXT_CLR, fontsize=8.5, fontweight="bold",
    )

# "#1" badge on MemoryLake
ax_overall.text(
    56, 0, " #1 ", va="center", ha="left",
    color=BG, fontsize=7.5, fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.25", facecolor="#38bdf8", edgecolor="none"),
)

# ── 2. Grouped bar – per category ────────────────────────────────────────────

style_ax(ax_grouped, "Score by Question Type")
ax_grouped.grid(axis="y", color=GRID_CLR, linewidth=0.6, zorder=0)
ax_grouped.grid(axis="x", visible=False)

n_cats = len(CATEGORIES)
n_sys  = len(SYSTEMS)
width  = 0.11
x      = np.arange(n_cats)

for i, (sys, color) in enumerate(zip(SYSTEMS, PALETTE)):
    vals   = [DATA[sys][j] for j in range(4)]
    offset = (i - n_sys / 2 + 0.5) * width
    rects  = ax_grouped.bar(
        x + offset, vals,
        width=width * 0.9, color=color, edgecolor="none",
        zorder=3, label=sys,
    )

ax_grouped.set_xticks(x)
ax_grouped.set_xticklabels(CATEGORIES, fontsize=9)
ax_grouped.set_ylabel("F1 Score (%)", fontsize=9)
ax_grouped.set_ylim(35, 108)
ax_grouped.legend(
    fontsize=7.5, ncol=4, loc="upper right",
    facecolor=CARD_BG, edgecolor=GRID_CLR, labelcolor=TEXT_CLR,
    columnspacing=0.8, handlelength=1.2,
)

# ── 3. Radar chart ────────────────────────────────────────────────────────────

ax_radar.set_facecolor(CARD_BG)
ax_radar.set_title("Category Breakdown (Top 4)", color=TEXT_CLR,
                    fontsize=11, fontweight="bold", pad=20)

angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()
angles += angles[:1]  # close the polygon

top4 = SYSTEMS[:4]
for sys, color in zip(top4, PALETTE[:4]):
    vals = [DATA[sys][j] for j in range(4)]
    vals += vals[:1]
    lw = 2.5 if sys == "MemoryLake" else 1.5
    ax_radar.plot(angles, vals, color=color, linewidth=lw, zorder=3)
    ax_radar.fill(angles, vals, color=color, alpha=0.08, zorder=2)
    ax_radar.scatter(angles[:-1], vals[:-1], color=color, s=30, zorder=4)

ax_radar.set_xticks(angles[:-1])
ax_radar.set_xticklabels(CATEGORIES, color=TEXT_CLR, fontsize=9)
ax_radar.set_ylim(60, 100)
ax_radar.set_yticks([65, 75, 85, 95])
ax_radar.set_yticklabels(["65", "75", "85", "95"], color=MUTED, fontsize=7.5)
ax_radar.spines["polar"].set_edgecolor(GRID_CLR)
ax_radar.yaxis.grid(color=GRID_CLR, linewidth=0.6)
ax_radar.xaxis.grid(color=GRID_CLR, linewidth=0.6)

legend_patches = [
    mpatches.Patch(color=PALETTE[i], label=top4[i]) for i in range(4)
]
ax_radar.legend(
    handles=legend_patches, loc="lower left",
    bbox_to_anchor=(-0.18, -0.12), fontsize=8,
    facecolor=CARD_BG, edgecolor=GRID_CLR, labelcolor=TEXT_CLR,
    ncol=2, columnspacing=0.8, handlelength=1.0,
)

# ── 4. Heatmap – full matrix ──────────────────────────────────────────────────

style_ax(ax_heat, "Score Heatmap (All Systems × Categories)")
ax_heat.grid(visible=False)

matrix = np.array([[DATA[s][j] for j in range(4)] for s in SYSTEMS])

# Custom colormap: dark for low, bright cyan for high
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list(
    "dark_cyan", ["#1e3a5f", "#0ea5e9", "#e0f2fe"], N=256
)

im = ax_heat.imshow(matrix, cmap=cmap, aspect="auto", vmin=40, vmax=100)

ax_heat.set_xticks(range(n_cats))
ax_heat.set_xticklabels(CATEGORIES, fontsize=9, color=TEXT_CLR)
ax_heat.set_yticks(range(n_sys))
ax_heat.set_yticklabels(SYSTEMS, fontsize=9, color=TEXT_CLR)
ax_heat.tick_params(bottom=False, left=False)

for i, sys in enumerate(SYSTEMS):
    for j in range(n_cats):
        val  = matrix[i, j]
        dark = val < 75
        ax_heat.text(
            j, i, f"{val:.1f}",
            ha="center", va="center", fontsize=8.5, fontweight="bold",
            color="#0f1117" if not dark else TEXT_CLR,
        )

plt.colorbar(im, ax=ax_heat, fraction=0.03, pad=0.02).ax.tick_params(
    labelcolor=TEXT_CLR, labelsize=8
)

# ── 5. Per-record line chart ──────────────────────────────────────────────────

style_ax(ax_line, "MemoryLake — Per-Record Scores by Question Type")
ax_line.grid(axis="y", color=GRID_CLR, linewidth=0.6, zorder=0)
ax_line.grid(axis="x", visible=False)

records = PER_RECORD["record"]
x_r     = np.arange(len(records))

LINE_COLORS = {"single": "#38bdf8", "multi": "#a78bfa",
               "temporal": "#fbbf24", "open": "#34d399"}
LINE_LABELS = {"single": "Single-hop", "multi": "Multi-hop",
               "temporal": "Temporal", "open": "Open-domain"}

for key in CAT_KEYS:
    vals = PER_RECORD[key]
    # Replace None with NaN for plotting
    y = np.array([v if v is not None else np.nan for v in vals], dtype=float)
    ax_line.plot(
        x_r, y,
        color=LINE_COLORS[key], linewidth=2, marker="o", markersize=5,
        label=LINE_LABELS[key], zorder=3,
    )

# Overall as thick dashed line
overall = np.array(PER_RECORD["overall"], dtype=float)
ax_line.plot(
    x_r, overall,
    color=TEXT_CLR, linewidth=2.2, linestyle="--", marker="D", markersize=5,
    label="Overall", zorder=4,
)

ax_line.set_xticks(x_r)
ax_line.set_xticklabels(records, fontsize=9.5)
ax_line.set_ylabel("F1 Score (%)", fontsize=9)
ax_line.set_ylim(30, 108)
ax_line.legend(
    fontsize=9, loc="lower right",
    facecolor=CARD_BG, edgecolor=GRID_CLR, labelcolor=TEXT_CLR,
    ncol=5, columnspacing=1.0,
)

# ── Source note ───────────────────────────────────────────────────────────────

fig.text(
    0.5, 0.005,
    "MemoryLake results: this repository  ·  "
    "Competitor results: EverMind-AI/EverMemOS evaluation (GPT-4.1-mini as answer LLM)  ·  "
    "Benchmark: LoCoMo — SNAP Research",
    ha="center", va="bottom", fontsize=7.5, color=MUTED,
)

# ── Save ──────────────────────────────────────────────────────────────────────

out = "benchmark_comparison.png"
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
print(f"Saved → {out}")
plt.close(fig)
