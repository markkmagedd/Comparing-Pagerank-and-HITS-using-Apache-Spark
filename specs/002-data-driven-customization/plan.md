# Implementation Plan: Data-Driven Customization

**Branch**: `002-data-driven-customization` | **Date**: 2026-03-19 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-data-driven-customization/spec.md`

## Summary

Add two orthogonal data-driven controls to the existing PageRank / HITS web visualization: a **single-select league filter** that restricts the transfer graph to one competition at a time, and a **weight mode toggle** between "Transfer Fee" (monetary value, existing behaviour) and "Transfer Count" (deal-record count). Both controls auto-trigger a debounced re-computation via the existing FastAPI / PySpark pipeline with no manual "Run" button, and display a loading overlay during computation.

## Technical Context

**Language/Version**: Python 3.12 (backend), Vanilla JS (frontend)  
**Primary Dependencies**: FastAPI, PySpark (local mode, `local[1]`), Pydantic v2, Cytoscape.js, Chart.js + DataLabels plugin  
**Storage**: N/A — stateless; `transfers.csv` (532 KB) is the sole data source, read at startup  
**Testing**: pytest (unit + integration); existing fixtures in `tests/unit/test_pyspark.py` and `tests/integration/test_api.py`  
**Target Platform**: Local development server (uvicorn) + any modern browser  
**Performance Goals**: Analysis re-run completes and renders in ≤ 5 seconds from control change (SC-001)  
**Constraints**: No persistence across page loads; single-select league filter; no new external dependencies  
**Scale/Scope**: 124 distinct leagues in dataset; ~N thousand transfer records; single-user local tool

## Constitution Check

*GATE: Must pass before implementation. Re-checked after Phase 1 design.*

| Principle | Pre-Design | Post-Design | Notes |
|-----------|-----------|-------------|-------|
| I. PySpark Scalability First | ✅ | ✅ | League filter and count mode applied as RDD `.filter()` / `.map()` before `reduceByKey(add)` — fully distributed |
| II. Function Modularity & SRP | ✅ | ✅ | `_load_data()` gains `league`+`weight_mode` params; new `get_available_leagues()` standalone function; each concern is isolated |
| III. Safe App Initialization | ✅ | ✅ | No changes to SparkSession lifespan block |
| IV. Robust Data Parsing | ✅ | ✅ | `parse_fee()` unchanged; "count" mode avoids fee parsing entirely; missing/malformed league strings handled by strip + exact match |
| V. Deterministic Output Artifacts | ✅ | ✅ | No new file outputs; visualization remains in-browser |

**No violations — Complexity Justification table not required.**

## Project Structure

### Documentation (this feature)

```text
specs/002-data-driven-customization/
├── plan.md            ← This file
├── research.md        ← Phase 0 output
├── data-model.md      ← Phase 1 output
├── contracts/
│   └── api.md         ← Phase 1 output
└── tasks.md           ← Phase 2 output (speckit.tasks)
```

### Source Code (affected files)

```text
src/
├── app.py                    # +GET /api/leagues endpoint
│                             # +extend CalculationRequest (league, weight_mode)
│                             # +extend POST /api/pagerank response (meta, weight_label)
└── core/
    └── processing.py         # +get_available_leagues()
                              # +weight_mode param in _load_data() / get_top_graph()
                              # +league filter param in _load_data() / get_top_graph()

src/static/js/
└── graph.js                  # +league dropdown population on load
                              # +weight mode toggle control
                              # +debounced auto-run on control change
                              # +loading overlay on viz area
                              # +empty-state rendering
                              # +weight_label display in edges / tooltips

tests/unit/
└── test_pyspark.py            # +tests for count weight mode
                              # +tests for league filtering (intra-league predicate)
                              # +tests for get_available_leagues()

tests/integration/
└── test_api.py                # +tests for GET /api/leagues
                              # +tests for POST /api/pagerank with league + weight_mode params
                              # +tests for empty-state response (meta.empty == true)
```

## Phase 0: Research ✅ Complete

See [research.md](./research.md).

All technical unknowns resolved:
- Dataset column mapping confirmed (League_from = col 4, League_to = col 6)
- 124 distinct leagues identified — dynamic derivation required
- Intra-league filter predicate defined: both `League_from` and `League_to` must match
- Count mode: constant `1` per row, same `reduceByKey(add)` pipeline
- API extension: backward-compatible via Pydantic defaults
- Debounce strategy: 300 ms `setTimeout`/`clearTimeout` on control `change` events
- Loading overlay: localized to viz area (not full-screen), reuses CSS pattern

## Phase 1: Design & Contracts ✅ Complete

See [data-model.md](./data-model.md) and [contracts/api.md](./contracts/api.md).

### Backend Design

**`src/core/processing.py` changes:**

1. **`get_available_leagues(sc, file_path)`** — new top-level function:
   - Reads raw lines, skips header, maps `x[4].strip()` and `x[6].strip()`, computes `.distinct()`, `.collect()`, sorts.
   - Returns `list[str]`.

2. **`TransferAnalyzer._load_data(league=None, weight_mode="fee")`** changes:
   - After parsing CSV columns, if `league` is set (not `"all"`/`None`), apply `.filter(lambda x: x[4].strip() == league and x[6].strip() == league)`.
   - Weight map: if `weight_mode == "count"` → `lambda x: ((x[3].strip(), x[5].strip()), 1)` else existing `parse_fee(x[9])` path.
   - `_load_data` is called at `__init__` time — constructor now accepts `league` and `weight_mode` and passes them through.

3. **`get_top_graph()`** — adds `weight_label` to each edge dict:
   - `"€{weight/1_000_000:.0f}M"` for fee mode.
   - `"{weight} deals"` for count mode.
   - Returns `meta` dict: `{league, weight_mode, total_records, empty}`.

**`src/app.py` changes:**

1. **`GET /api/leagues`** — new endpoint:
   - Calls `get_available_leagues(spark.sparkContext, "transfers.csv")`.
   - Returns `{"leagues": [...]}`.

2. **`CalculationRequest`** — extend Pydantic model:
   ```python
   league: str = Field("all")
   weight_mode: str = Field("fee", pattern="^(fee|count)$")
   ```

3. **`POST /api/pagerank`** — pass `league` and `weight_mode` to `TransferAnalyzer`; add `meta` and `weight_label` to response.

### Frontend Design

**`src/static/js/graph.js` changes:**

1. **On `DOMContentLoaded`**: call `GET /api/leagues`, populate `<select id="league">` with "All Leagues" + sorted options.

2. **Weight mode toggle**: add event listener on `<select id="weight-mode">` (or toggle buttons). On change, trigger debounced submit.

3. **Debounced auto-run**: replace manual `form.addEventListener('submit', ...)` trigger with a shared `triggerAnalysis()` function called both by:
   - The existing "Run" button (immediate).
   - `league` and `weight-mode` control `change` events (after 300 ms debounce).

4. **Loading overlay on viz area**: a new `<div id="viz-loading">` overlays `#cy-container` / `#chart-container` when loading; hidden when result arrives.

5. **Empty-state**: if `meta.empty == true`, hide viz area and show `<div id="empty-state">` with message "No data available for the selected league."

6. **Weight label in edges / tooltips**: use `edge.data.weight_label` in Cytoscape edge tooltip; use `weight_label` in Chart.js tooltip body.

### HTML Template Changes *(if applicable)*

The `<form>` in `src/templates/index.html` needs two new controls:
- `<select id="league">` — league filter (populated dynamically).
- `<select id="weight-mode">` or toggle buttons — "Transfer Fee" / "Transfer Count".
- `<div id="viz-loading">` — overlay element for computation in-progress state.
- `<div id="empty-state">` — hidden by default, shown when `meta.empty == true`.

## Implementation Sequence

Tasks are broken into user-story-aligned increments, each independently testable:

1. **Backend foundation** — `get_available_leagues()` + `GET /api/leagues` + tests
2. **Backend league filter** — `_load_data()` filter predicate + tests
3. **Backend weight mode** — count mode map + `weight_label` in response + `meta` block + tests
4. **Frontend league dropdown** — populate from `/api/leagues` on load
5. **Frontend weight mode toggle** — control + wiring
6. **Frontend debounced auto-run** — replaces manual submit; triggers on either control
7. **Frontend loading overlay** — viz-area overlay while computing
8. **Frontend empty-state** — render empty-state when `meta.empty == true`
9. **Integration tests** — end-to-end happy path + empty-state + edge cases

*(Full task breakdown generated by `/speckit.tasks`)*
