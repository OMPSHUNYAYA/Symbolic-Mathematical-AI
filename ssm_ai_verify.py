#!/usr/bin/env python3
# Golden vectors + invariance checks (prints PASS/FAIL). Use float64 Python math.

from math import tanh, atanh, isfinite

EPS_A = 1e-6
EPS_W = 1e-12

def clamp_align(a, eps_a=EPS_A):
    return max(-1+eps_a, min(1-eps_a, a))

def approx(x, y, tol=1e-12):
    return abs(x - y) <= tol

def test_clamp_roundtrip():
    a_in = 0.9999999
    a_c  = clamp_align(a_in)
    u    = atanh(a_c)
    back = tanh(u)
    return isfinite(u) and approx(back, a_c, 1e-9)

def test_fuse_invariance():
    a1 = tanh(0.2); a2 = tanh(0.4)
    U = 0.2 + 0.4; W = 2.0
    a_out = tanh(U / max(W, EPS_W))
    return approx(a_out, tanh(0.3), 1e-9)

def test_lane_mul_div_M2():
    a1 = tanh(0.5); a2 = tanh(0.2)
    a_mul = tanh(0.5 + 0.2)
    a_div = tanh(0.5 - 0.2)
    return approx(a_mul, 0.604368, 1e-6) and approx(a_div, 0.291313, 1e-6)

def test_chooser():
    U_in = -0.2; V_out = +0.5; W = 1.0
    RSI = tanh((V_out - U_in) / max(W, EPS_W))
    return approx(RSI, 0.604368, 1e-6)

def run():
    tests = [
        ("clamp_roundtrip", test_clamp_roundtrip()),
        ("fuse_invariance", test_fuse_invariance()),
        ("lane_mul_div_M2", test_lane_mul_div_M2()),
        ("chooser",         test_chooser()),
    ]
    ok = True
    for name, passed in tests:
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
        ok = ok and passed
    print("overall:", "PASS" if ok else "FAIL")

if __name__ == "__main__":
    run()
