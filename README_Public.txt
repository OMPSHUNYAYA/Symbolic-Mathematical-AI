# SSM-AI — Public Demo Bundle (v1.8)

## Intro (brief)

This bundle ships a tiny, **read-only** lane and chooser demo for LLM decoding, retrieval, and tool loops.  
The **value lane** `m` is never modified; collapse parity holds: `phi((m,a)) = m`.  
The **alignment lane** `a` is bounded and composable via rapidity (`u := atanh(a)`, `a := tanh(u)`).  
Streaming fuse is order-invariant by the `U/W` rule: `U += w*atanh(a)`, `W += w`, `a_out := tanh( U / max(W, eps_w) )`.  
Chooser is bounded: `RSI := tanh( (V_out - U_in) / max(W_in, eps_w) )`. Optional calm gate: `RSI_env := g_t * RSI` or `RSI_env := tanh( g_t * atanh(RSI) )`.  
Defaults: `eps_a = 1e-6`, `eps_w = 1e-12`. All formulas are plain ASCII.

## What’s included (public research release)

- **Python demos:** `ssm_ai_quickstart.py` (end-to-end demo), `ssm_ai_verify.py` (golden vectors)
- **Helper:** `vendor_n4_to_csv.py` (TSV/whitespace → clean CSV with consistent headers)
- **Docs:** `docs/Brief_SSM-AI_ver 1.8.pdf`, `docs/SSM-AI_ver 1.8.pdf`
- **Logs (created at runtime):** CSV lines with `U/W/RSI/RSI_env/band` suitable for replay

**Non-commercial evaluation and internal tooling only for the documents.** Classical measurements remain unchanged; the lane is supplemental.

---

## Repo layout (suggested)

SSM-AI/
├─ ssm_ai_quickstart.py
├─ ssm_ai_verify.py
├─ vendor_n4_to_csv.py
├─ README.md
├─ README.txt
├─ GETTING_STARTED.txt
├─ CALIBRATION.txt
├─ docs/
│ ├─ Brief_SSM-AI_ver 1.8.pdf
│ └─ SSM-AI_ver 1.8.pdf
└─ logs/ # optional outputs (created at runtime)


## Tutorial — 2-minute walkthrough

### 1) Demo (no inputs required) — Windows
python ssm_ai_quickstart.py

### 1) Demo (no inputs required) — macOS / Linux
python3 ssm_ai_quickstart.py

### Outputs (console)

- Candidate `RSI`, `RSI_env`, band labels
- Fuse check: `a_out ≈ 0.291313` from `U=0.6`, `W=2` via `a_out := tanh(U/max(W, eps_w))`

### What to look for

- `phi((m,a)) = m` holds: `m` stays the classical value
- `a` and `RSI` are inside `(-1,+1)` with bands `A++/A+/A0/A-/A--`
- Gate is alignment-only: `RSI_env := g_t * RSI` or `RSI_env := tanh(g_t * atanh(RSI))`; `m` unchanged

### 2) Verify math invariants (golden vectors) — Windows
python ssm_ai_verify.py

### 2) Verify math invariants (golden vectors) — macOS / Linux
python3 ssm_ai_verify.py

Expected output:
clamp_roundtrip: PASS
fuse_invariance: PASS
lane_mul_div_M2: PASS
chooser: PASS
overall: PASS

Formulas under test:
- Clamp then map to rapidity: a_c := clamp(a, -1+eps_a, +1-eps_a), u := atanh(a_c)
- Order/shard invariance: a_out := tanh( sum(u) / max(sum(w), eps_w) )
- Lane mul/div (M2): a' := tanh( atanh(a1) +/- atanh(a2) )

### 3) Optional: Convert your N4 vendor sheet to clean CSV — Windows
:: Place your N4 text as N4.txt (whitespace/TSV ok), then run:
python vendor_n4_to_csv.py --in N4.txt --out vendor_datasheet_N4.csv

### 3) Optional: Convert your N4 vendor sheet to clean CSV — macOS / Linux
# Place your N4 text as N4.txt (whitespace/TSV ok), then run:
python3 vendor_n4_to_csv.py --in N4.txt --out vendor_datasheet_N4.csv

CSV header produced:
svc,comparison,tokens_saved_pct,retry_drop_pct,latency_saved_pct,unit_cost_saved_pct,RSI_pool_env_delta,weekly_savings_usd

## CSV schema (logs, replay-ready) — per-decision row (suggested)
iso_utc, svc, knobs_hash, dtype, m, a, U, W, RSI, g_t, RSI_env, band, division_policy, note

Replay invariants:
- a_out == tanh( sum(U) / max(sum(W), eps_w) )
- RSI == tanh( (V_out - U_in) / max(W_in, eps_w) )
- phi((m,a)) = m
- Zero-evidence guard: if W_in == 0, then RSI := 0, band := "A0", reason insufficient_evidence

CLI essentials (math & knobs):
- Clamp: a := clamp(a, -1+eps_a, +1-eps_a)
- Bands: A++: a>=+0.90, A+: +0.60<=a<+0.90, A0: -0.60<a<+0.60, A-: -0.90<a<=-0.60, A--: a<=-0.90
- Hysteresis (optional): promote only if x >= tau + h_up; demote only if x <= tau - h_dn
- Collapse parity: phi((m,a)) = m
- Fusion (multi-cue): a_out := tanh( (SUM w*atanh(a_i)) / max(SUM w, eps_w) )
- Weights: default w := |m|^gamma with gamma = 1 (use w := 1 for apples-to-apples)
- Gate: RSI_env := g_t * RSI  OR  RSI_env := tanh( g_t * atanh(RSI) )
- Defaults: eps_a=1e-6, eps_w=1e-12 (use eps_w >= 1e-8 if float32), dtype="float64" preferred

Notes for pilots:
- Fix a manifest once for a pilot; share the knobs_hash with results
- Prefer stable windows and clear CSV stamps; let the lane move, not the rule
- Start with the demo, then wire simple lens terms to produce e_in/e_out and RSI in your pipeline
- For SSM-Search (Symbolic Search), rank by RSI or RSI_env while keeping classical retrieval scores m_retrieval intact

License:
(c) The Authors of Shunyaya Framework and Shunyaya Symbolic Mathematics.
Released under CC BY-NC 4.0 (non-commercial, with attribution). Observation-only; non-commercial evaluation and internal tooling.
No warranty; use at your own risk. No redistribution of third-party raw data unless the licence explicitly permits it.
