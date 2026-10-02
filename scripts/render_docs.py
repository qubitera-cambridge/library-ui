#!/usr/bin/env python3
"""Stage 2 of the documentation site build: render every algorithm's page from
library_core's metadata (always present), EXPLANATION.md (optional, via
library_core.get_explanation), and a cached demo() result (optional, produced
by generate_demo_outputs.py).

Deliberately needs no quantum SDK — library_core.list_algorithms()/
get_explanation() never import an algorithm's actual implementation, only its
metadata.yaml/EXPLANATION.md, which is why this is a separate step from
generate_demo_outputs.py. Output goes to build/, which mkdocs.yml points
`docs_dir` at; nothing here is committed to git.
"""

import json
from pathlib import Path

import jinja2
import library_core

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "website" / "templates"
DEMO_CACHE_DIR = REPO_ROOT / "demo_cache"
BUILD_DIR = REPO_ROOT / "build"


def render_site():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    algorithm_template = env.get_template("algorithm.md.j2")
    index_template = env.get_template("index.md.j2")

    categories = {}

    for meta in library_core.list_algorithms():
        explanation = library_core.get_explanation(meta["id"])
        provenance = library_core.get_provenance(meta["id"])

        demo_cache_path = DEMO_CACHE_DIR / f"{meta['id']}.json"
        demo = json.loads(demo_cache_path.read_text()) if demo_cache_path.exists() else None

        page = algorithm_template.render(
            meta=meta, explanation=explanation, demo=demo, provenance=provenance
        )

        out_path = BUILD_DIR / meta["category"] / f"{meta['id']}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page)
        print(f"rendered: {out_path.relative_to(REPO_ROOT)}")

        categories.setdefault(meta["category"], []).append(meta)

    index_page = index_template.render(categories=categories)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.md").write_text(index_page)
    print(f"rendered: {(BUILD_DIR / 'index.md').relative_to(REPO_ROOT)}")

    total = sum(len(v) for v in categories.values())
    print(f"\n{total} algorithm page(s) rendered across {len(categories)} categor(y/ies)")


if __name__ == "__main__":
    render_site()
