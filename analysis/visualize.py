"""
Visualize MathTutor evaluation results.
Generates comparison charts for Base vs FT-1 vs FT-2.

Usage:
    pip install matplotlib
    python analysis/visualize.py

Outputs:
    charts/scores_comparison.png
    charts/pedagogy_by_type.png
    charts/efficiency.png
"""

import json, os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.size'] = 10

os.makedirs("charts", exist_ok=True)

# Load corrected results
with open("results/llm_judge_results_v1_corrected.json", encoding='utf-8') as f:
    v1_data = json.load(f)

with open("results/llm_judge_results_v2_corrected.json", encoding='utf-8') as f:
    v2_data = json.load(f)

# Extract scores
base_v1 = v1_data["base_scores_corrected"]
ft1 = v1_data["tuned_v1_scores_corrected"]
base_v2 = v2_data["base_scores_corrected"]
ft2 = v2_data["tuned_v2_scores_corrected"]

# ============================================================
# Chart 1: Overall scores comparison (Base vs FT-1 vs FT-2)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))

metrics = ["correctness", "pedagogy", "structure", "faithfulness", "refusal"]
labels = ["Correctness\n(in-domain)", "Pedagogy\n(in-domain)", "Structure\n(all)", "Faithfulness\n(all)", "Refusal\n(OOD)"]

base_scores = [base_v2[m]["avg"] for m in metrics]
ft1_scores = [ft1[m]["avg"] for m in metrics]
ft2_scores = [ft2[m]["avg"] for m in metrics]

x = range(len(metrics))
width = 0.25

bars1 = ax.bar([i - width for i in x], base_scores, width, label="Base Qwen3-8B", color="#95a5a6", edgecolor="white")
bars2 = ax.bar(x, ft1_scores, width, label="FT-1 (r=32, 526 ex)", color="#e67e22", edgecolor="white")
bars3 = ax.bar([i + width for i in x], ft2_scores, width, label="FT-2 (r=16, 612 ex)", color="#27ae60", edgecolor="white")

ax.set_ylabel("Score (1-5)")
ax.set_title("MathTutor Evaluation: Base vs FT-1 vs FT-2 (Corrected)")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylim(2.5, 5.2)
ax.legend(loc="lower right")
ax.grid(axis="y", alpha=0.3)

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7.5)

fig.tight_layout()
fig.savefig("charts/scores_comparison.png", dpi=150, bbox_inches="tight")
print("Saved charts/scores_comparison.png")

# ============================================================
# Chart 2: Pedagogy by prompt type (Base vs FT-1 vs FT-2)
# ============================================================
fig, ax = plt.subplots(figsize=(9, 5))

types = ["concept", "problem", "misconception", "confusion"]
type_labels = ["Concept", "Problem", "Misconception", "Confusion"]

# Get per-type pedagogy
base_ped = [base_v1.get("per_type_pedagogy", {}).get(t, {}).get("avg", 0) for t in types]
ft1_ped = [ft1.get("per_type_pedagogy", {}).get(t, {}).get("avg", 0) for t in types]
ft2_ped = [ft2.get("per_type_pedagogy", {}).get(t, {}).get("avg", 0) for t in types]

x = range(len(types))
width = 0.25

bars1 = ax.bar([i - width for i in x], base_ped, width, label="Base", color="#95a5a6", edgecolor="white")
bars2 = ax.bar(x, ft1_ped, width, label="FT-1", color="#e67e22", edgecolor="white")
bars3 = ax.bar([i + width for i in x], ft2_ped, width, label="FT-2", color="#27ae60", edgecolor="white")

ax.set_ylabel("Pedagogy Score (1-5)")
ax.set_title("Pedagogy by Prompt Type: The Confusion Fix")
ax.set_xticks(x)
ax.set_xticklabels(type_labels)
ax.set_ylim(2.5, 5.2)
ax.legend()
ax.grid(axis="y", alpha=0.3)



for bars in [bars1, bars2, bars3]:
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7.5)

fig.tight_layout()
fig.savefig("charts/pedagogy_by_type.png", dpi=150, bbox_inches="tight")
print("Saved charts/pedagogy_by_type.png")

# ============================================================
# Chart 3: Efficiency comparison
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(12, 4))

# Response tokens
ax = axes[0]
vals = [317, 168, 187]
colors = ["#95a5a6", "#e67e22", "#27ae60"]
bars = ax.bar(["Base", "FT-1", "FT-2"], vals, color=colors, edgecolor="white")
ax.set_ylabel("Avg Tokens")
ax.set_title("Response Length\n(in-domain, Qwen3 tokenizer)")
for bar, v in zip(bars, vals):
    ax.annotate(str(v), xy=(bar.get_x() + bar.get_width()/2, v),
                xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10)

# Trainable params
ax = axes[1]
vals = [87.3, 43.6]
bars = ax.bar(["FT-1", "FT-2"], vals, color=["#e67e22", "#27ae60"], edgecolor="white")
ax.set_ylabel("Millions")
ax.set_title("Trainable Parameters")
for bar, v in zip(bars, vals):
    ax.annotate(f"{v}M", xy=(bar.get_x() + bar.get_width()/2, v),
                xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10)

# VRAM
ax = axes[2]
vals = [17.8, 7.2]
bars = ax.bar(["FT-1", "FT-2"], vals, color=["#e67e22", "#27ae60"], edgecolor="white")
ax.set_ylabel("GB")
ax.set_title("Training VRAM")
for bar, v in zip(bars, vals):
    ax.annotate(f"{v} GB", xy=(bar.get_x() + bar.get_width()/2, v),
                xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10)

fig.suptitle("FT-2: Better Scores with Fewer Resources", fontsize=13, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig("charts/efficiency.png", dpi=150, bbox_inches="tight")
print("Saved charts/efficiency.png")

print("\nAll charts saved to charts/ directory.")
