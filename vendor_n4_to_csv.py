#!/usr/bin/env python3
# Convert a simple N4 vendor sheet (whitespace- or comma-separated) into a clean CSV with consistent headers.
# Usage examples:
#   python vendor_n4_to_csv.py --in N4.txt --out vendor_datasheet_N4.csv
#   type N4.txt | python vendor_n4_to_csv.py --stdin --out vendor_datasheet_N4.csv
#
# This version fixes a bug where any row starting with "svc..." was incorrectly
# treated as a header and discarded. We now only skip a true header line whose
# first field is exactly "svc" (case-insensitive), optionally followed by "comparison", etc.

import sys
import argparse
import csv
import re
from typing import List, Optional

HEADERS = [
    "svc",
    "comparison",
    "tokens_saved_pct",
    "retry_drop_pct",
    "latency_saved_pct",
    "unit_cost_saved_pct",
    "RSI_pool_env_delta",
    "weekly_savings_usd",
]

number_like = re.compile(r"^[+-]?\d+(?:\.\d+)?$")

def split_line(line: str) -> List[str]:
    # Note: also merges unquoted currency like $182,400 into a single token
    s = line.strip()
    if not s:
        return []
    # Prefer CSV if commas are present
    if "," in s:
        # Use csv to respect quoted fields
        reader = csv.reader([s])
        row = next(reader)
        row = [col.strip() for col in row if col is not None]
        # Merge unquoted currency fragments like $182,400 -> $182400
        merged = []
        i = 0
        while i < len(row):
            tok = row[i]
            if tok.startswith("$"):
                j = i + 1
                extra = []
                while j < len(row) and re.fullmatch(r"\d{3}", row[j]):
                    extra.append(row[j])
                    j += 1
                if extra:
                    merged.append(tok + "".join(extra))
                    i = j
                    continue
                merged.append(tok)
                i += 1
            else:
                merged.append(tok)
                i += 1
        return merged
    # Fallback: split on any whitespace
    return re.split(r"\s+", s)

def is_header(fields: List[str]) -> bool:
    """
    Treat as header only if the first field is exactly 'svc' (case-insensitive),
    not 'svcA', 'svc1', etc. We optionally allow 'comparison' next.
    """
    if not fields:
        return False
    f0 = fields[0].strip().lower()
    if f0 != "svc":
        return False
    # Stronger signal if the second field is 'comparison'
    if len(fields) > 1 and fields[1].strip().lower() == "comparison":
        return True
    # If first field is exactly 'svc' and there are many column names,
    # still consider it a header.
    return True

def find_usd_token(tokens: List[str]) -> Optional[int]:
    """
    Find the index of the rightmost token that looks like a currency amount,
    e.g. '$182,400' or '$182400'. Returns index or None.
    """
    for i in range(len(tokens) - 1, -1, -1):
        t = tokens[i].strip()
        if t.startswith("$"):
            return i
    return None

def coerce_int_from_currency(tok: str) -> int:
    # Strip non-digits and parse
    digits = re.sub(r"[^\d]", "", tok)
    if not digits:
        raise ValueError(f"cannot parse integer from currency token: {tok!r}")
    return int(digits)

def parse_row(tokens: List[str]) -> dict:
    """
    Expect the layout:
      svc, comparison..., <tokens_saved_pct> <retry_drop_pct> <latency_saved_pct> <unit_cost_saved_pct> <RSI_pool_env_delta> $<weekly_savings_usd>
    'comparison' may contain spaces or commas depending on source format.
    """
    if len(tokens) < 7:
        raise ValueError(f"row too short: {tokens}")

    usd_idx = find_usd_token(tokens)
    if usd_idx is None:
        # try to find a trailing pure integer as dollars
        for i in range(len(tokens) - 1, -1, -1):
            if re.fullmatch(r"\d+", tokens[i].strip()):
                usd_idx = i
                break
    if usd_idx is None:
        raise ValueError(f"cannot find USD or integer amount token in: {tokens}")

    # We expect 5 numeric-ish tokens immediately before the USD token
    tail_start = usd_idx - 5
    if tail_start < 1:
        raise ValueError(f"not enough fields before USD token: {tokens}")

    head = tokens[:tail_start]
    tail = tokens[tail_start:usd_idx]
    usd_tok = tokens[usd_idx]

    # Head: first field is svc, the rest join into comparison
    svc = head[0].strip()
    comparison = " ".join(h.strip() for h in head[1:]).strip()

    # Tail: 4 numeric percentages + 1 RSI delta (string allowed)
    try:
        tokens_saved_pct    = float(tail[0])
        retry_drop_pct      = float(tail[1])
        latency_saved_pct   = float(tail[2])
        unit_cost_saved_pct = float(tail[3])
    except Exception as e:
        raise ValueError(f"failed to parse numeric percentages from tail={tail} in row={tokens}: {e}")

    RSI_pool_env_delta = tail[4].strip()

    # USD
    if usd_tok.strip().startswith("$"):
        weekly_savings_usd = coerce_int_from_currency(usd_tok)
    else:
        # already a pure integer
        weekly_savings_usd = int(usd_tok)

    return {
        "svc": svc,
        "comparison": comparison,
        "tokens_saved_pct": tokens_saved_pct,
        "retry_drop_pct": retry_drop_pct,
        "latency_saved_pct": latency_saved_pct,
        "unit_cost_saved_pct": unit_cost_saved_pct,
        "RSI_pool_env_delta": RSI_pool_env_delta,
        "weekly_savings_usd": weekly_savings_usd,
    }

def main():
    ap = argparse.ArgumentParser(description="Normalize N4 vendor sheet to CSV.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--in", dest="infile", help="Path to input TXT/CSV/TSV")
    src.add_argument("--stdin", action="store_true", help="Read from STDIN")
    ap.add_argument("--out", dest="outfile", required=True, help="Path to output CSV")
    args = ap.parse_args()

    # Read raw lines
    if args.infile:
        with open(args.infile, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    else:
        raw_lines = sys.stdin.read().splitlines()

    rows = []
    for ln in raw_lines:
        # Skip empty and comment lines
        if not ln.strip() or ln.strip().startswith("#"):
            continue

        fields = split_line(ln)
        if not fields:
            continue

        # Skip only a *real* header
        if is_header(fields):
            # Heuristic: if it also looks like data (USD at end with 5 numeric fields before),
            # treat it as data rather than header.
            if fields and fields[0].strip().lower() == "svc":
                try:
                    usd_idx = find_usd_token(fields)
                    looks_like_data = usd_idx is not None and (usd_idx - 5) >= 1
                except Exception:
                    looks_like_data = False
                if not looks_like_data:
                    continue

        try:
            row = parse_row(fields)
            rows.append(row)
        except Exception as e:
            print(f"[WARN] Skipping line due to parse error: {e}\n  LINE: {ln.strip()}", file=sys.stderr)

    # Write CSV
    with open(args.outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows -> {args.outfile}")

if __name__ == "__main__":
    main()
