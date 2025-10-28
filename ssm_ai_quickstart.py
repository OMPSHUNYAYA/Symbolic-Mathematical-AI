#!/usr/bin/env python3
# Minimal, dependency-free SSM-AI quickstart: clamp -> atanh/tanh -> U/W -> RSI -> optional gate
# All formulas in plain ASCII, observation-only: phi((m,a)) = m

from math import tanh, atanh
from typing import List, Tuple, Dict

# ---------- knobs (safe defaults) ----------
EPS_A = 1e-6        # clamp margin for alignment
EPS_W = 1e-12       # denominator guard for means (>=1e-8 if float32)
GAMMA = 1.0         # weights: w := |m|^gamma  (set to 0 for uniform)

# ---------- helpers ----------
def clamp_align(a: float, eps_a: float = EPS_A) -> float:
    lo, hi = -1.0 + eps_a, 1.0 - eps_a
    return min(hi, max(lo, a))

def band_of(x: float) -> str:
    # A++: x >= +0.90; A+: +0.60 <= x < +0.90; A0: -0.60 < x < +0.60; A-: -0.90 < x <= -0.60; A--: x <= -0.90
    if x >= 0.90: return "A++"
    if x >= 0.60: return "A+"
    if x > -0.60: return "A0"
    if x > -0.90: return "A-"
    return "A--"

# ---------- lens -> alignment ----------
def map_to_alignment(e_in: float, e_out: float, c: float = 1.0, eps_a: float = EPS_A) -> Tuple[float, float]:
    # a_in := tanh(-c*e_in), a_out := tanh(+c*e_out)
    a_in  = clamp_align(tanh(-c * e_in), eps_a)
    a_out = clamp_align(tanh(+c * e_out), eps_a)
    return a_in, a_out

# ---------- order-invariant RSI chooser ----------
def rsi_from_items(items: List[Tuple[float, float, float]], eps_w: float = EPS_W, eps_a: float = EPS_A) -> float:
    # items: list of (e_in, e_out, w); U += w*atanh(a); W += w; RSI := tanh((V_out - U_in)/max(W, eps_w))
    U_in = V_out = W = 0.0
    for e_in, e_out, w in items:
        a_in, a_out = map_to_alignment(e_in, e_out, c=1.0, eps_a=eps_a)
        U_in  += w * atanh(a_in)
        V_out += w * atanh(a_out)
        W     += w
    if W <= 0:
        return 0.0
    return tanh((V_out - U_in) / max(W, eps_w))

# ---------- calm gate (alignment-only) ----------
def apply_gate(RSI: float, g_t: float, mode: str = "mul", eps_a: float = EPS_A) -> float:
    # RSI_env := g_t * RSI     or     RSI_env := tanh( g_t * atanh(RSI) )
    x = clamp_align(RSI, eps_a)
    y = g_t * x if mode == "mul" else tanh(g_t * atanh(x))
    return clamp_align(y, eps_a)

# ---------- demo: beam pick ----------
def demo_beam():
    # Two candidates with simple lens items (e_in, e_out, w); weights can be |m|^gamma or 1
    candA = [ (0.2, 0.5, 1.0) ]                      # supportive out > in
    candB = [ (0.3, 0.4, 1.0) ]
    g_t = 0.81                                        # example calm gate
    RSI_A = rsi_from_items(candA); RSI_B = rsi_from_items(candB)
    RSIe_A = apply_gate(RSI_A, g_t, mode="mul"); RSIe_B = apply_gate(RSI_B, g_t, mode="mul")
    pick = "A" if RSIe_A >= RSIe_B else "B"
    print(f"RSI_A={RSI_A:.6f}, RSIe_A={RSIe_A:.6f}, band_A={band_of(RSIe_A)}")
    print(f"RSI_B={RSI_B:.6f}, RSIe_B={RSIe_B:.6f}, band_B={band_of(RSIe_B)}")
    print(f"PICK={pick} by RSI_env; classical m unchanged via phi((m,a)) = m")

# ---------- demo: pool in u-space ----------
def demo_pool():
    # a1 = tanh(0.2) = 0.197375; a2 = tanh(0.4) = 0.379949; U=0.2+0.4=0.6; W=2; a_out=tanh(0.3)=0.291313
    a1 = clamp_align(tanh(0.2)); a2 = clamp_align(tanh(0.4))
    U = atanh(a1) + atanh(a2); W = 2.0
    a_out = tanh(U / max(W, EPS_W))
    print(f"a_out={a_out:.6f} (expect ~0.291313)")

if __name__ == "__main__":
    print("== SSM-AI quickstart ==")
    demo_beam()
    demo_pool()
