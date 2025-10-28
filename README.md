# SSM-AI - alignment lane beside AI scores (values unchanged). Order-invariant, reproducible (SHA-256). Observation-only.

![GitHub Release](https://img.shields.io/github/v/release/OMPSHUNYAYA/Symbolic-Mathematical-AI?style=flat&logo=github) ![GitHub Stars](https://img.shields.io/github/stars/OMPSHUNYAYA/Symbolic-Mathematical-AI?style=flat&logo=github) ![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-blue?style=flat&logo=creative-commons) ![CI](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/actions/workflows/ssm-ai-ci.yml/badge.svg)

## Intro

Shunyaya Symbolic Mathematical AI (SSM-AI) adds a transparent alignment lane beside the AI scores you already trust, so teams can see stability vs. fragility early without changing the numbers.
The classical value stays sacred by construction (`phi((m,a)) = m`), while the lane `a` highlights calm versus risk at a glance.
It is observation-only, order-invariant, and reproducible (SHA-256), designed to drop in with zero retraining or vendor lock-in.

## Why it matters

- Same decisions, earlier clarity: the AI score stays exactly as is; SSM-AI adds a simple lane that highlights stability vs. fragility at a glance.
- Fewer surprises: bands (A++/A+/A0/A-/A--) make drift visible early, so course-corrections happen before it hurts outcomes.
- Zero rework: plug in beside current models, dashboards, and reviews. No retraining, no vendor lock-in, no disruption.
- Works across use cases: ranking, retrieval, evaluators, tool-calling, ensembles. One lane, many surfaces.
- Consistent and fair: results do not depend on ordering or batching, which makes comparisons easier across teams and time.
- Easy to share and audit: a tiny set of defaults and a reproducible knobs fingerprint let anyone reproduce what you see.
- Low lift to try: one quickstart script and a short checklist are enough to evaluate fit on real workloads.

## Documents (Preview)

**Executive Brief v1.8 (PDF):** [Preview](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/blob/main/Brief_SSM-AI_ver%201.8.pdf) • [Download](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/raw/main/Brief_SSM-AI_ver%201.8.pdf)

**SSM-AI v1.8 - Detailed Pack (PDF):** [Preview](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/blob/main/SSM-AI_ver%201.8.pdf) • [Download](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/raw/main/SSM-AI_ver%201.8.pdf)

**Public README Note (TXT):** [Preview](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/blob/main/README_Public.txt) • [Download](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/raw/main/README_Public.txt)

**Getting Started (TXT):** [Preview](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/blob/main/GETTING_STARTED.txt) • [Download](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/raw/main/GETTING_STARTED.txt)

**Calibration (TXT):** [Preview](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/blob/main/CALIBRATION.txt) • [Download](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/raw/main/CALIBRATION.txt)

**Quickstart demo (PY):** [Preview](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/blob/main/ssm_ai_quickstart.py) • [Download](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/raw/main/ssm_ai_quickstart.py)

**Verification tests (PY):** [Preview](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/blob/main/ssm_ai_verify.py) • [Download](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/raw/main/ssm_ai_verify.py)

**N4 vendor sheet -> CSV helper (PY):** [Preview](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/blob/main/vendor_n4_to_csv.py) • [Download](https://github.com/OMPSHUNYAYA/Symbolic-Mathematical-AI/raw/main/vendor_n4_to_csv.py)

## Quick try

Quick try: `python ssm_ai_quickstart.py`  
Verify: `python ssm_ai_verify.py`

## Technical note (ASCII, one screen)

Canonicals: `phi((m,a)) = m`; `a := clamp(a, -1+eps_a, +1-eps_a)`
Bands: `A++: a>=0.90`, `A+: a>=0.60`, `A0: -0.60 < a < +0.60`, `A-: -0.90 < a <= -0.60`, else `A--: a <= -0.90`
Order-invariant fuse (U/W rule): `a_out := tanh( (SUM w*atanh(a)) / max(SUM w, eps_w) )`
Chooser (bounded RSI for ranking/sorts): use `a` lane to separate calm vs. fragile candidates
Lane arithmetic (score-safe): mul/div is via rapidity domain (tanh/atanh)
Defaults: `eps_a=1e-6`, `eps_w=1e-12`

All original AI scores remain unchanged and continue driving decisions; the `a` lane adds stability awareness without altering outcomes.

## License

(c) The Authors of Shunyaya Framework and Shunyaya Symbolic Mathematics. Released under CC BY-NC 4.0 (non-commercial, with attribution).
Observation-only; not for operational, safety-critical, or legal decision-making.
We do not redistribute third-party raw data unless the licence explicitly permits it.
No warranty. No endorsement or affiliation implied.

## GitHub Topics (Repo → About)
shunyaya • ssm • ssm-ai • symbolic-mathematics • ai • alignment • stability • bands • hysteresis • sdi • entropy • order-invariance • reproducibility • csv • python • ascii • research
