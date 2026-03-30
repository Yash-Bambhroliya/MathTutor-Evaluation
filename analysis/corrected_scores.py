"""
Generate corrected results by splitting metrics by domain.
- Correctness/Pedagogy: only in-domain (concept, problem, misconception, confusion)
- Refusal: only OOD
- Structure/Faithfulness: all 50

Does NOT modify any original files. Creates new:
  - results/llm_judge_results_v2_corrected.json
"""

import json, sys
sys.stdout.reconfigure(encoding='utf-8')

RESULTS_DIR = "C:/Users/Admin/.openclaw/workspace/Task/results"

# Load V2 judge results
with open(f"{RESULTS_DIR}/llm_judge_results_v2.json", encoding='utf-8') as f:
    data = json.load(f)

results = data["all_results"]

def avg(lst):
    return sum(lst) / len(lst) if lst else 0

def compute_corrected(results, model_key):
    in_domain = {"correctness": [], "pedagogy": []}
    ood = {"refusal": []}
    all_prompts = {"structure": [], "faithfulness": []}
    per_type_ped = {}
    
    for r in results:
        if not r.get("scores") or r["model"] != model_key:
            continue
        s = r["scores"]
        ptype = r.get("type", "")
        
        for key in ["structure", "faithfulness"]:
            val = s.get(key)
            if isinstance(val, (int, float)):
                all_prompts[key].append(val)
        
        if ptype == "ood":
            ref = s.get("refusal")
            if isinstance(ref, (int, float)):
                ood["refusal"].append(ref)
        else:
            for key in ["correctness", "pedagogy"]:
                val = s.get(key)
                if isinstance(val, (int, float)):
                    in_domain[key].append(val)
            
            ped = s.get("pedagogy")
            if isinstance(ped, (int, float)):
                if ptype not in per_type_ped:
                    per_type_ped[ptype] = []
                per_type_ped[ptype].append(ped)
    
    return {
        "correctness": {"values": in_domain["correctness"], "avg": avg(in_domain["correctness"]), "count": len(in_domain["correctness"]), "scope": "in-domain only"},
        "pedagogy": {"values": in_domain["pedagogy"], "avg": avg(in_domain["pedagogy"]), "count": len(in_domain["pedagogy"]), "scope": "in-domain only"},
        "structure": {"values": all_prompts["structure"], "avg": avg(all_prompts["structure"]), "count": len(all_prompts["structure"]), "scope": "all prompts"},
        "faithfulness": {"values": all_prompts["faithfulness"], "avg": avg(all_prompts["faithfulness"]), "count": len(all_prompts["faithfulness"]), "scope": "all prompts"},
        "refusal": {"values": ood["refusal"], "avg": avg(ood["refusal"]), "count": len(ood["refusal"]), "scope": "OOD only"},
        "per_type_pedagogy": {
            ptype: {"values": vals, "avg": avg(vals), "count": len(vals)}
            for ptype, vals in per_type_ped.items()
        },
    }

base_corrected = compute_corrected(results, "base")
v2_corrected = compute_corrected(results, "tuned_v2")

# Build corrected output
corrected = {
    "methodology": "domain-scoped correction: Split metrics by domain — correctness/pedagogy on in-domain only, refusal on OOD only, structure/faithfulness on all prompts",
    "why": "Prevents base model from getting inflated correctness/pedagogy scores when it complies with off-topic requests (e.g., writing Python code scores correctness=5 for a math tutor eval)",
    "judge_model": "claude-sonnet-4-6",
    "base_scores_corrected": base_corrected,
    "tuned_v2_scores_corrected": v2_corrected,
    "v1_reference": {
        "correctness": 4.85,
        "pedagogy": 4.22,
        "structure": 4.74,
        "faithfulness": 4.78,
        "refusal": 4.75,
        "confusion_pedagogy": 3.50,
    },
    "all_results": results,
}

output_path = f"{RESULTS_DIR}/llm_judge_results_v2_corrected.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(corrected, f, indent=2, ensure_ascii=False)

# Print summary
print("=" * 70)
print("CORRECTED RESULTS (domain-scoped correction: Split by Domain)")
print("=" * 70)
print()
print(f"  | Metric                | Base    | V1 Tuned | V2 Tuned | V2 vs Base | V2 vs V1  |")
print(f"  |-----------------------|---------|----------|----------|------------|-----------|")

metrics = [
    ("Correctness (in-domain)", "correctness", 4.85),
    ("Pedagogy (in-domain)", "pedagogy", 4.22),
    ("Structure (all)", "structure", 4.74),
    ("Faithfulness (all)", "faithfulness", 4.78),
    ("Refusal (OOD only)", "refusal", 4.75),
]

for label, key, v1_val in metrics:
    b = base_corrected[key]["avg"]
    t = v2_corrected[key]["avg"]
    n = v2_corrected[key]["count"]
    d_base = t - b
    d_v1 = t - v1_val
    print(f"  | {label:<21} | {b:>5.2f}   | {v1_val:>5.2f}    | {t:>5.2f}    | {d_base:>+6.2f}     | {d_v1:>+6.2f}    | (n={n})")

print()
print("  Per-type PEDAGOGY (in-domain, V2 tuned):")
for ptype in ["concept", "problem", "misconception", "confusion"]:
    v2_vals = v2_corrected["per_type_pedagogy"].get(ptype, {})
    base_vals = base_corrected["per_type_pedagogy"].get(ptype, {})
    v2_avg = v2_vals.get("avg", 0)
    base_avg = base_vals.get("avg", 0)
    n = v2_vals.get("count", 0)
    print(f"    {ptype:15s}: V2={v2_avg:.2f}  Base={base_avg:.2f}  Δ={v2_avg-base_avg:+.2f}  (n={n})")

v1_confusion = 3.50
v2_confusion = v2_corrected["per_type_pedagogy"].get("confusion", {}).get("avg", 0)
print(f"\n  🎯 KEY: Confusion pedagogy V1={v1_confusion:.2f} → V2={v2_confusion:.2f} (Δ={v2_confusion-v1_confusion:+.2f})")

print(f"\n✅ Saved: {output_path}")
print(f"   Original files untouched.")
