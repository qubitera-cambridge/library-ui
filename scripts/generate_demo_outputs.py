#!/usr/bin/env python3
"""Stage 1 of the documentation site build: run each algorithm's `demo()`
(via library_core) and cache the result as JSON.

Must run inside the tox environment matching the algorithms' framework (e.g.
`tox -e qiskit-docs`) — calling run_demo() actually imports and executes real
algorithm code, so that framework's SDK must be installed alongside
library-core. Stage 2 (render_docs.py) deliberately needs none of that — see
README.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import library_core

REPO_ROOT = Path(__file__).resolve().parent.parent
DEMO_CACHE_DIR = REPO_ROOT / "demo_cache"


def generate_for_framework(framework: str, only_ids: list[str] | None = None) -> int:
    DEMO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    generated, skipped = 0, 0

    for meta in library_core.list_algorithms():
        algo_id = meta["id"]
        if only_ids is not None and algo_id not in only_ids:
            continue

        frameworks = {impl.get("framework") for impl in meta.get("implementations", [])}
        if framework not in frameworks:
            continue

        try:
            result = library_core.run_demo(algo_id, framework)
        except AttributeError:
            print(f"skip (no demo()): {algo_id}")
            skipped += 1
            continue

        out_path = DEMO_CACHE_DIR / f"{algo_id}.json"
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"generated: {algo_id} -> {out_path.relative_to(REPO_ROOT)}")
        generated += 1

    print(f"\n{generated} demo(s) generated, {skipped} algorithm(s) skipped (no demo() yet)")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", required=True)
    parser.add_argument(
        "ids", nargs="*", help="Scope to these algorithm ids only (default: all)"
    )
    args = parser.parse_args()
    sys.exit(generate_for_framework(args.framework, args.ids or None))
