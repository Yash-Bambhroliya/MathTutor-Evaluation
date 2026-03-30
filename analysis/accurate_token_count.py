import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from transformers import AutoTokenizer

print("Loading Qwen3-8B tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen3-8B",
    trust_remote_code=True,
)
print(f"Tokenizer loaded. Vocab size: {tokenizer.vocab_size}\n")

# Update these paths to point to your results files
RESULTS_DIR = "results"

with open(f"{RESULTS_DIR}/eval_results_v2.json", encoding='utf-8') as f:
    v2 = json.load(f)
with open(f"{RESULTS_DIR}/base_eval_results.json", encoding='utf-8') as f:
    base = json.load(f)

def count_tokens(text):
    return len(tokenizer.encode(text, add_special_tokens=False))

print("=" * 60)
print("ACCURATE TOKEN COUNT (Qwen3 tokenizer, in-domain only)")
print("=" * 60)

for ptype in ["concept", "problem", "misconception", "confusion"]:
    b_tokens = [count_tokens(r["response"]) for r in base if r.get("type") == ptype]
    v_tokens = [count_tokens(r["response"]) for r in v2 if r.get("type") == ptype]
    if b_tokens and v_tokens:
        ba = sum(b_tokens)/len(b_tokens)
        va = sum(v_tokens)/len(v_tokens)
        print(f"  {ptype:15s}: base={ba:.0f} tokens  v2={va:.0f} tokens  (V2 is {(1-va/ba)*100:.0f}% shorter)")

# Overall in-domain
b_all = [count_tokens(r["response"]) for r in base if r.get("type") != "ood"]
v_all = [count_tokens(r["response"]) for r in v2 if r.get("type") != "ood"]
ba = sum(b_all)/len(b_all)
va = sum(v_all)/len(v_all)

print(f"\n  OVERALL (in-domain):")
print(f"    Base:  {ba:.0f} tokens avg  (total: {sum(b_all)} tokens across {len(b_all)} prompts)")
print(f"    V2:    {va:.0f} tokens avg  (total: {sum(v_all)} tokens across {len(v_all)} prompts)")
print(f"    V2 is {(1-va/ba)*100:.0f}% shorter")
print(f"    Saved: {sum(b_all) - sum(v_all)} tokens across {len(b_all)} prompts")
