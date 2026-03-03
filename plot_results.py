"""
Generate LoCoMo benchmark comparison charts — one file per chart.

Outputs:
  charts/01_overall.png
  charts/02_by_category.png
  charts/03_radar.png
  charts/04_heatmap.png
  charts/05_per_record.png
"""

import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

matplotlib.rcParams["figure.dpi"] = 150
matplotlib.rcParams["font.family"] = "DejaVu Sans"

os.makedirs("charts", exist_ok=True)

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
    #               single   multi   temporal  open    overall
    "MemoryLake":   [96.79,  91.84,  91.28,   85.42,  94.03],
    "EverMemOS":    [96.08,  91.13,  89.72,   70.83,  92.32],
    "Full-context": [94.93,  90.43,  87.95,   71.88,  91.21],
    "Zep":          [90.84,  81.91,  77.26,   75.00,  85.22],
    "MemOS":        [85.37,  79.43,  75.08,   64.58,  80.76],
    "MemU":         [74.91,  72.34,  43.61,   54.17,  66.67],
    "Mem0":         [68.97,  61.70,  58.26,   50.00,  64.20],
}

PER_RECORD = {
    "record":   ["R1",   "R2",   "R3",   "R4",   "R5",   "R6",   "R7",   "R8",   "R9",   "R10"],
    "single":   [100.00, 95.45,  96.51,  97.30,  96.26,  96.77,  98.80,  95.76,  94.52,  96.55],
    "multi":    [ 84.38, 100.00, 96.77,  94.59,  83.87,  86.67, 100.00,  85.71,  97.30,  93.75],
    "temporal": [100.00, 100.00, 96.30,  92.50,  80.77,  87.50,  85.29,  97.62,  84.85,  84.38],
    "open":     [100.00,  None,  87.50,  72.73,  85.71,  42.86,  76.92, 100.00,  92.31, 100.00],
    "overall":  [ 96.71,  97.53, 96.05,  94.47,  91.01,  89.43,  94.00,  95.29,  92.95,  93.67],
}

CATEGORIES = ["Single-hop", "Multi-hop", "Temporal", "Open-domain"]
CAT_KEYS   = ["single", "multi", "temporal", "open"]

# ── Theme ─────────────────────────────────────────────────────────────────────

BG       = "#0f1117"
CARD_BG  = "#161b27"
GRID_CLR = "#252d3d"
TEXT_CLR = "#e2e8f0"
MUTED    = "#64748b"

PALETTE = [
    "#38bdf8",  # MemoryLake  – sky blue
    "#a78bfa",  # EverMemOS   – purple
    "#fbbf24",  # Full-context – amber
    "#34d399",  # Zep          – emerald
    "#f87171",  # MemOS        – red
    "#94a3b8",  # MemU         – slate
    "#818cf8",  # Mem0         – indigo
]

SOURCE = (
    "Data: MemoryLake results from this repo  ·  "
    "Competitor results: EverMind-AI/EverMemOS (GPT-4.1-mini)  ·  "
    "Benchmark: LoCoMo — SNAP Research"
)


def new_fig(w, h, title):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG)
    fig.suptitle(title, fontsize=14, fontweight="bold", color=TEXT_CLR, y=0.97)
    ax.set_facecolor(CARD_BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    ax.tick_params(colors=TEXT_CLR)
    ax.xaxis.label.set_color(TEXT_CLR)
    ax.yaxis.label.set_color(TEXT_CLR)
    return fig, ax


def add_source(fig):
    fig.text(0.5, 0.01, SOURCE, ha="center", va="bottom",
             fontsize=7, color=MUTED)


def save(fig, name):
    path = f"charts/{name}"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"Saved → {path}")


# ── 1. Overall score — horizontal bar ────────────────────────────────────────

fig, ax = new_fig(9, 5, "LoCoMo Benchmark — Overall Score")
ax.grid(axis="x", color=GRID_CLR, linewidth=0.7, zorder=0)
ax.grid(axis="y", visible=False)

scores = [DATA[s][4] for s in SYSTEMS]
y = np.arange(len(SYSTEMS))
bars = ax.barh(y, scores, color=PALETTE, edgecolor="none", height=0.55, zorder=3)
bars[0].set_edgecolor("#38bdf8")
bars[0].set_linewidth(1.8)

ax.set_yticks(y)
ax.set_yticklabels(SYSTEMS, fontsize=11)
ax.set_xlabel("F1 Score (%)", fontsize=10)
ax.set_xlim(55, 103)
ax.invert_yaxis()

for bar, score, sys in zip(bars, scores, SYSTEMS):
    ax.text(score + 0.4, bar.get_y() + bar.get_height() / 2,
            f"{score:.2f}%", va="center", ha="left",
            color=TEXT_CLR, fontsize=9.5, fontweight="bold")

ax.text(56.2, 0, " #1 ", va="center", ha="left", fontsize=8, fontweight="bold",
        color=BG, bbox=dict(boxstyle="round,pad=0.3", facecolor="#38bdf8", edgecolor="none"))

fig.subplots_adjust(left=0.18, right=0.95, top=0.90, bottom=0.12)
add_source(fig)
save(fig, "01_overall.png")

# ── 2. Score by question type — grouped bar ───────────────────────────────────

fig, ax = new_fig(10, 6, "LoCoMo Benchmark — Score by Question Type")
ax.grid(axis="y", color=GRID_CLR, linewidth=0.7, zorder=0)
ax.grid(axis="x", visible=False)

n_sys  = len(SYSTEMS)
n_cats = len(CATEGORIES)
width  = 0.10
x      = np.arange(n_cats)

for i, (sys, color) in enumerate(zip(SYSTEMS, PALETTE)):
    vals   = [DATA[sys][j] for j in range(4)]
    offset = (i - n_sys / 2 + 0.5) * width
    ax.bar(x + offset, vals, width=width * 0.9,
           color=color, edgecolor="none", zorder=3, label=sys)

ax.set_xticks(x)
ax.set_xticklabels(CATEGORIES, fontsize=11)
ax.set_ylabel("F1 Score (%)", fontsize=10)
ax.set_ylim(35, 112)
ax.legend(fontsize=9, ncol=4, loc="upper right",
          facecolor=CARD_BG, edgecolor=GRID_CLR, labelcolor=TEXT_CLR,
          columnspacing=0.9, handlelength=1.3)

fig.subplots_adjust(left=0.10, right=0.97, top=0.90, bottom=0.12)
add_source(fig)
save(fig, "02_by_category.png")

# ── 3. Radar chart — top 4 systems ────────────────────────────────────────────

fig = plt.figure(figsize=(7, 7), facecolor=BG)
fig.suptitle("LoCoMo Benchmark — Category Breakdown (Top 4 Systems)",
             fontsize=13, fontweight="bold", color=TEXT_CLR, y=0.97)
ax = fig.add_subplot(111, projection="polar")
ax.set_facecolor(CARD_BG)

angles = np.linspace(0, 2 * np.pi, n_cats, endpoint=False).tolist()
angles += angles[:1]

top4 = SYSTEMS[:4]
for sys, color in zip(top4, PALETTE[:4]):
    vals = [DATA[sys][j] for j in range(4)] + [DATA[sys][0]]
    lw = 2.8 if sys == "MemoryLake" else 1.6
    ax.plot(angles, vals, color=color, linewidth=lw, zorder=3)
    ax.fill(angles, vals, color=color, alpha=0.10, zorder=2)
    ax.scatter(angles[:-1], vals[:-1], color=color, s=40, zorder=4)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(CATEGORIES, color=TEXT_CLR, fontsize=11)
ax.set_ylim(60, 100)
ax.set_yticks([65, 75, 85, 95])
ax.set_yticklabels(["65", "75", "85", "95"], color=MUTED, fontsize=8)
ax.spines["polar"].set_edgecolor(GRID_CLR)
ax.yaxis.grid(color=GRID_CLR, linewidth=0.7)
ax.xaxis.grid(color=GRID_CLR, linewidth=0.7)

legend_patches = [mpatches.Patch(color=PALETTE[i], label=top4[i]) for i in range(4)]
ax.legend(handles=legend_patches, loc="lower center", bbox_to_anchor=(0.5, -0.14),
          fontsize=9.5, ncol=4, facecolor=CARD_BG, edgecolor=GRID_CLR,
          labelcolor=TEXT_CLR, columnspacing=1.0, handlelength=1.2)

fig.subplots_adjust(top=0.90, bottom=0.12)
add_source(fig)
save(fig, "03_radar.png")

# ── 4. Heatmap — all systems × categories ────────────────────────────────────

fig, ax = new_fig(8, 5.5, "LoCoMo Benchmark — Score Heatmap")
ax.grid(visible=False)

matrix = np.array([[DATA[s][j] for j in range(4)] for s in SYSTEMS])
cmap = LinearSegmentedColormap.from_list(
    "dark_cyan", ["#1e3a5f", "#0ea5e9", "#bae6fd"], N=256)
im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=40, vmax=100)

ax.set_xticks(range(n_cats))
ax.set_xticklabels(CATEGORIES, fontsize=11, color=TEXT_CLR)
ax.set_yticks(range(len(SYSTEMS)))
ax.set_yticklabels(SYSTEMS, fontsize=11, color=TEXT_CLR)
ax.tick_params(bottom=False, left=False)

for i in range(len(SYSTEMS)):
    for j in range(n_cats):
        val = matrix[i, j]
        ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                fontsize=10, fontweight="bold",
                color="#0f1117" if val >= 75 else TEXT_CLR)

cb = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
cb.ax.tick_params(labelcolor=TEXT_CLR, labelsize=8)
cb.ax.set_facecolor(CARD_BG)

fig.subplots_adjust(left=0.15, right=0.93, top=0.90, bottom=0.10)
add_source(fig)
save(fig, "04_heatmap.png")

# ── 5. Per-record line chart ──────────────────────────────────────────────────

fig, ax = new_fig(11, 5.5, "MemoryLake — Per-Record Scores by Question Type")
ax.grid(axis="y", color=GRID_CLR, linewidth=0.7, zorder=0)
ax.grid(axis="x", visible=False)

records = PER_RECORD["record"]
x_r     = np.arange(len(records))

LINE_COLORS = {"single": "#38bdf8", "multi": "#a78bfa",
               "temporal": "#fbbf24", "open": "#34d399"}
LINE_LABELS = {"single": "Single-hop", "multi": "Multi-hop",
               "temporal": "Temporal", "open": "Open-domain"}

for key in CAT_KEYS:
    y = np.array([v if v is not None else np.nan for v in PER_RECORD[key]], dtype=float)
    ax.plot(x_r, y, color=LINE_COLORS[key], linewidth=2,
            marker="o", markersize=6, label=LINE_LABELS[key], zorder=3)

overall = np.array(PER_RECORD["overall"], dtype=float)
ax.plot(x_r, overall, color=TEXT_CLR, linewidth=2.5,
        linestyle="--", marker="D", markersize=6, label="Overall", zorder=4)

ax.set_xticks(x_r)
ax.set_xticklabels(records, fontsize=11)
ax.set_ylabel("F1 Score (%)", fontsize=10)
ax.set_ylim(30, 110)
ax.legend(fontsize=10, loc="lower right", ncol=5,
          facecolor=CARD_BG, edgecolor=GRID_CLR, labelcolor=TEXT_CLR,
          columnspacing=1.0)

fig.subplots_adjust(left=0.08, right=0.97, top=0.90, bottom=0.12)
add_source(fig)
save(fig, "05_per_record.png")
