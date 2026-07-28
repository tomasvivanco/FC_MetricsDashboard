#!/usr/bin/env python3
"""
Validate a Fab City Index 3.0 submission CSV before you commit it.

Runs the same rules the dashboard applies, so a file that passes here will load
cleanly in the matrix. Dependency-free — standard library only.

    python3 scripts/validate_submission.py data/submissions/boston-table4.csv
    python3 scripts/validate_submission.py            # validates everything in data/submissions/

Exit code 0 = clean, 1 = errors found.
"""

import csv
import json
import os
import re
import sys
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_JS = os.path.join(REPO, "assets", "data.js")
SUBMISSIONS = os.path.join(REPO, "data", "submissions")

REQUIRED = ["cell", "indicator", "value", "unit", "observation_date",
            "source", "scale_min", "scale_max"]

C_RESET, C_RED, C_YEL, C_GRN, C_DIM = "\033[0m", "\033[31m", "\033[33m", "\033[32m", "\033[2m"
if not sys.stdout.isatty():
    C_RESET = C_RED = C_YEL = C_GRN = C_DIM = ""


def load_schema_version():
    """Read SCHEMA_VERSION from assets/data.js — same source the dashboard uses."""
    with open(DATA_JS, encoding="utf-8") as fh:
        m = re.search(r'const SCHEMA_VERSION\s*=\s*"([^"]+)"', fh.read())
    return m.group(1) if m else None


def load_cells():
    """Pull cell keys, indicator names, units and directions straight out of
    assets/data.js so this script can never drift from the dashboard."""
    with open(DATA_JS, encoding="utf-8") as fh:
        src = fh.read()

    start = src.find("const CELLS = {")
    if start == -1:
        sys.exit("Could not find CELLS in assets/data.js — has the file moved?")

    cells, current = {}, None
    for line in src[start:].splitlines():
        m = re.match(r'\s*"([a-z]+:[a-z]+)":\s*\{', line)
        if m:
            current = m.group(1)
            cells[current] = []
            continue
        if current:
            mi = re.search(r'\{\s*name:"([^"]+)",\s*unit:"([^"]+)",\s*direction:"(dido|pito)"', line)
            if mi:
                cells[current].append({
                    "name": mi.group(1), "unit": mi.group(2), "direction": mi.group(3)
                })
        if re.match(r"^\};", line) and cells:
            break
    return cells


def norm(s):
    return re.sub(r"\s+", "", (s or "").strip().lower())


def validate(path, cells):
    errors, warnings, ok = [], [], 0

    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
        if not rows:
            errors.append(("file", "File has a header but no data rows."))
            return errors, warnings, ok
        header = [h.strip().lower() for h in (rows[0].keys() if rows else [])]

    missing = [c for c in REQUIRED if c not in header]
    if missing:
        errors.append(("header", "Missing required column(s): " + ", ".join(missing)))
        return errors, warnings, ok

    ours = load_schema_version()
    if ours and "schema_version" in header:
        theirs = (rows[0].get("schema_version") or "").strip()
        if theirs and theirs != ours:
            if theirs.split(".")[0] != ours.split(".")[0]:
                errors.append(("header", f"schema_version {theirs} is a MAJOR version behind the dashboard's {ours} — "
                                         "indicator names/units have changed incompatibly. Re-check every row."))
            else:
                warnings.append(("header", f"schema_version {theirs} vs dashboard {ours} — minor difference "
                                           "(indicators were only added); the file will load."))
    elif ours and "schema_version" not in header:
        warnings.append(("header", f"No schema_version column. Add one (current: {ours}) so future model "
                                   "changes warn you instead of silently misreading this file."))

    seen = set()
    for i, raw in enumerate(rows, start=2):     # start=2: row 1 is the header
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in raw.items()}
        cell, ind = r.get("cell", ""), r.get("indicator", "")
        where = f"row {i} ({cell or '?'} · {ind or '?'})"

        if cell not in cells:
            errors.append((where, f"Unknown cell key '{cell}'. Use pillar:scale, e.g. environmental:community"))
            continue

        defs = cells[cell]
        match = next((d for d in defs if norm(d["name"]) == norm(ind)), None)
        if not match:
            names = "; ".join(d["name"] for d in defs) or "(none defined)"
            errors.append((where, f"Indicator not defined in that cell. Valid: {names}"))
            continue

        key = (cell, norm(ind), r.get("observation_date", ""))
        if key in seen:
            warnings.append((where, "Duplicate cell + indicator + date — the later row will overwrite the earlier one."))
        seen.add(key)

        try:
            val = float(r["value"])
        except (ValueError, KeyError):
            errors.append((where, f"value '{r.get('value')}' is not a number"))
            continue

        try:
            lo, hi = float(r["scale_min"]), float(r["scale_max"])
        except ValueError:
            errors.append((where, "scale_min and scale_max must both be numbers so the value can be normalised"))
            continue
        if lo == hi:
            errors.append((where, "scale_min and scale_max are equal — nothing can be scaled against a zero-width range"))
            continue
        if not (min(lo, hi) <= val <= max(lo, hi)):
            warnings.append((where, f"value {val} sits outside the stated range {lo}–{hi}; it will be clamped"))

        d = r.get("observation_date", "")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            errors.append((where, f"observation_date '{d}' must be ISO format YYYY-MM-DD"))
        else:
            try:
                y, m, dd = (int(x) for x in d.split("-"))
                if date(y, m, dd) > date.today():
                    warnings.append((where, "observation_date is in the future"))
            except ValueError:
                errors.append((where, f"observation_date '{d}' is not a real date"))

        if not r.get("source"):
            errors.append((where, "source is required — a value nobody can re-check is not evidence"))
        elif len(r["source"]) < 8:
            warnings.append((where, f"source '{r['source']}' is very short. 'City data' is not a source; name the dataset."))

        if norm(r.get("unit")) != norm(match["unit"]):
            warnings.append((where, f"unit '{r.get('unit')}' differs from the expected '{match['unit']}'"))

        ok += 1

    return errors, warnings, ok


def main():
    cells = load_cells()
    args = sys.argv[1:]

    if args:
        paths = args
    else:
        paths = [os.path.join(SUBMISSIONS, f)
                 for f in sorted(os.listdir(SUBMISSIONS)) if f.endswith(".csv")]
        if not paths:
            print("No CSV files in data/submissions/ yet.")
            return 0

    total_err = 0
    for p in paths:
        rel = os.path.relpath(p, REPO)
        if not os.path.exists(p):
            print(f"{C_RED}✗{C_RESET} {rel} — file not found")
            total_err += 1
            continue

        errors, warnings, ok = validate(p, cells)
        total_err += len(errors)

        if errors:
            print(f"{C_RED}✗ {rel}{C_RESET} — {len(errors)} error(s), {ok} row(s) would load")
        elif warnings:
            print(f"{C_YEL}⚠ {rel}{C_RESET} — clean, {ok} row(s) will load, {len(warnings)} thing(s) to look at")
        else:
            print(f"{C_GRN}✓ {rel}{C_RESET} — clean, {ok} row(s) will load")

        for where, msg in errors:
            print(f"    {C_RED}error{C_RESET}  {where}: {msg}")
        for where, msg in warnings:
            print(f"    {C_YEL}warn {C_RESET}  {where}: {msg}")

    if total_err:
        print(f"\n{C_RED}{total_err} error(s) to fix before committing.{C_RESET}")
        return 1
    print(f"\n{C_GRN}All good.{C_RESET} {C_DIM}Add your file to data/submissions/index.json and open a pull request.{C_RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
