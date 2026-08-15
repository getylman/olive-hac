#!/usr/bin/env python3
"""Assemble landing/config.json from meta + section fragments.

Contract (plan/WORK_PACKAGES.md):
  landing/meta/meta.json       -> {"title": str, "theme": {...}}
  landing/meta/overrides.json  -> [ {...}, ... ]
  landing/sections/NN-name.json -> {"type":...,"props":{...}} or [ ... ]

Fragments merge in lexicographic filename order. Deterministic, stdlib only.

Usage:
  python3 tools/assemble.py [--sections DIR] [--out FILE]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_DIR = os.path.join(ROOT, "landing", "meta")
FRAGMENT_RE = re.compile(r"^\d\d-[\w.-]+\.json$")

errors = []
warnings = []


def die():
    if errors:
        print("ASSEMBLY FAILED:", file=sys.stderr)
        for e in errors:
            print("  ERROR " + e, file=sys.stderr)
        sys.exit(1)


def load(path, what):
    if not os.path.isfile(path):
        errors.append(f"{what}: missing file {os.path.relpath(path, ROOT)}")
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        errors.append(f"{what}: invalid JSON in {os.path.relpath(path, ROOT)} — {exc}")
        return None


def main():
    argv = sys.argv[1:]
    sections_dir = os.path.join(ROOT, "landing", "sections")
    out_path = os.path.join(ROOT, "landing", "config.json")
    if "--sections" in argv:
        sections_dir = os.path.abspath(argv[argv.index("--sections") + 1])
    if "--out" in argv:
        out_path = os.path.abspath(argv[argv.index("--out") + 1])

    meta_raw = load(os.path.join(META_DIR, "meta.json"), "meta")
    overrides = load(os.path.join(META_DIR, "overrides.json"), "overrides")

    if meta_raw is not None and not isinstance(meta_raw, dict):
        errors.append("meta: meta.json must be an object")
        meta_raw = None
    if overrides is not None and not isinstance(overrides, list):
        errors.append("overrides: overrides.json must be an array")
        overrides = None

    if not os.path.isdir(sections_dir):
        errors.append(f"sections: no directory {os.path.relpath(sections_dir, ROOT)}")
    die()

    names = sorted(n for n in os.listdir(sections_dir) if FRAGMENT_RE.match(n))
    skipped = [
        n for n in sorted(os.listdir(sections_dir))
        if n.endswith(".json") and not FRAGMENT_RE.match(n)
    ]
    for n in skipped:
        warnings.append(f"skipped (name must be NN-name.json): {n}")

    prefixes = {}
    sections = []
    for name in names:
        prefixes.setdefault(name[:2], []).append(name)
        frag = load(os.path.join(sections_dir, name), f"section {name}")
        if frag is None:
            continue
        items = frag if isinstance(frag, list) else [frag]
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{name}[{i}]: fragment entries must be objects")
                continue
            if "type" not in item:
                errors.append(f"{name}[{i}]: object has no \"type\" key")
                continue
            item.setdefault("props", {})
            sections.append(item)

    for pref, group in sorted(prefixes.items()):
        if len(group) > 1:
            warnings.append(f"duplicate prefix {pref}: {', '.join(group)} — order is by full name")

    if not sections:
        errors.append("no section fragments found")
    die()

    config = {
        "meta": {
            "title": meta_raw.get("title", ""),
            "theme": meta_raw.get("theme", {}),
            "overrides": overrides,
        },
        "sections": sections,
    }
    # carry any extra meta keys the meta owner chose to set
    for k, v in meta_raw.items():
        if k not in ("title", "theme"):
            config["meta"].setdefault(k, v)

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    for w in warnings:
        print("  warn  " + w)
    print(f"assembled -> {os.path.relpath(out_path, ROOT)}")
    print(f"  {len(names)} fragment file(s), {len(sections)} section(s), "
          f"{len(overrides)} override(s)")
    print("  order: " + ", ".join(s["type"] for s in sections))


if __name__ == "__main__":
    main()
