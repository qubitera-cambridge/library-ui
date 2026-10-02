# library-ui

The documentation site for [QuAlgLib](https://github.com/qubitera-cambridge/library-core) — a
browsable index of quantum algorithms, generated directly from
[`library-core`](https://github.com/qubitera-cambridge/library-core)'s own metadata, explanations,
and live demo output. Not a separate, hand-maintained set of docs that can drift from the code.

This repo contains no algorithm content of its own — it depends on `library-core` via pip (see
`requirements-*.txt`) and only knows about algorithms through its public API
(`library_core.list_algorithms()`, `get_explanation()`, `get_provenance()`, `run_demo()`).

## Why two stages

Generating a demo means actually *running* an algorithm's real code via `library_core.run_demo()`
— which needs that algorithm's SDK installed (Qiskit, Cirq, ...). Rendering the site into
Markdown/HTML needs none of that — just the pre-computed results plus `library_core`'s pure-Python
metadata access. Mixing these into one step would mean every docs build needs every SDK installed
simultaneously. So the build is two separate tox environments:

1. **Per-framework demo generation** (`tox -e qiskit-docs`, and a `<framework>-docs` env for each
   SDK `library-core` adds — see `tox.ini`). Runs `scripts/generate_demo_outputs.py --framework
   <name>`, which calls `library_core.run_demo(algo_id, framework)` for every algorithm that has
   one, and caches the JSON result under `demo_cache/<algo-id>.json`. An algorithm with no
   `demo()` yet is skipped, not failed.
2. **Framework-agnostic rendering** (`tox -e docs`). Runs `scripts/render_docs.py`, which calls
   `library_core.list_algorithms()`/`get_explanation()`/`get_provenance()` (always present —
   `get_explanation`/`get_provenance` return `None` if the algorithm has none) and the cached demo
   JSON (optional), and renders each through `website/templates/algorithm.md.j2` into `build/`.
   Then `mkdocs build` turns that into the final static site at `site/`. Neither this nor Stage 1's
   rendering needs library-core's algorithm *implementations* imported — `list_algorithms()` only
   parses `metadata.yaml`.

```bash
pip install -r requirements-qiskit.txt   # or: tox -e qiskit-docs
tox -e qiskit-docs   # generate demo output for all Qiskit algorithms in library-core
tox -e docs          # render pages + build the static site into site/
```

Nothing under `build/`, `demo_cache/`, or `site/` is committed — all of it is fully derived from
`library-core` (pinned via `requirements-*.txt`) and regenerated on every build. Only
`website/templates/` (hand-written Jinja2) and this repo's own `mkdocs.yml`/`requirements-*.txt`
are checked in.

## Running locally

```bash
tox -e qiskit-docs
tox -e docs
# open site/index.html, or:
pip install -r requirements-docs.txt && mkdocs serve
```

## Updating the pinned library-core version

`requirements-*.txt` pin `library-core` to a git URL with no ref, so a plain `pip install` always
fetches the latest `main`. Pin to a specific commit (`...library-core.git@<sha>`) for a
reproducible build, and bump it deliberately when you want this site to pick up new algorithms.
