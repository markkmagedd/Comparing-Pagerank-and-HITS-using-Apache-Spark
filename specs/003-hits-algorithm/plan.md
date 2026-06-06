# Implementation Plan: HITS Algorithm Integration

**Branch**: `003-hits-algorithm` | **Date**: 2026-03-31 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/003-hits-algorithm/spec.md`

## Summary

Add HITS (Hyperlink-Induced Topic Search) algorithm computation alongside the existing PageRank implementation, and provide a UI algorithm selector allowing users to switch between PageRank and HITS analysis. HITS computes mutual-reinforcement Hub and Authority scores on the same weighted transfer graph. The existing data pipeline (CSV loading, league filtering, weight modes) is reused without modification. The front-end gains an algorithm selector dropdown with auto-run-on-change behavior, dynamic direction labels (Authority/Hub vs Attractors/Suppliers), and conditional disabling of the Damping Factor control when HITS is active.

## Technical Context

**Language/Version**: Python 3.12 (backend), Vanilla JS (frontend)  
**Primary Dependencies**: FastAPI, PySpark (local mode, `local[1]`), Pydantic v2, Cytoscape.js, Chart.js + DataLabels plugin  
**Storage**: N/A — stateless; `transfers.csv` (532 KB) is the sole data source  
**Testing**: pytest (unit + integration); existing fixtures in `tests/unit/test_pyspark.py` and `tests/integration/test_api.py`  
**Target Platform**: Local development server (uvicorn) + any modern browser  
**Project Type**: Web service (FastAPI backend + single-page Jinja2/JS frontend)  
**Performance Goals**: HITS computation completes in comparable time to PageRank for the same iteration count (SC-001)  
**Constraints**: No new external dependencies; HITS must use PySpark RDDs for all intensive computation (Constitution Principle I)  
**Scale/Scope**: Same dataset; single-user local tool

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Pre-Design | Post-Design | Notes |
|-----------|-----------|-------------|-------|
| I. PySpark Scalability First | ✅ | ✅ | `run_hits()` uses RDD `.join()`, `.flatMap()`, `.reduceByKey()` — fully distributed, mirrors `run_pagerank()` pattern |
| II. Function Modularity & SRP | ✅ | ✅ | New `run_hits()` standalone function; `TransferAnalyzer.get_rankings()` extended with algorithm dispatch; each concern isolated |
| III. Safe App Initialization | ✅ | ✅ | No changes to SparkSession lifespan block |
| IV. Robust Data Parsing | ✅ | ✅ | No changes to data parsing; HITS receives the same preprocessed edges RDD |
| V. Deterministic Output Artifacts | ✅ | ✅ | No new file outputs; visualization remains in-browser |

**No violations — Complexity Justification table not required.**

## Project Structure

### Documentation (this feature)

```text
specs/003-hits-algorithm/
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
├── app.py                    # +new POST /api/hits endpoint (or unified /api/analyze)
│                             # +extend CalculationRequest with algorithm field
└── core/
    └── processing.py         # +run_hits() standalone function
                              # +TransferAnalyzer.get_rankings() algorithm dispatch
                              # +TransferAnalyzer.get_top_graph() returns algorithm + score_type in meta

src/static/js/
└── graph.js                  # +algorithm selector auto-run listener
                              # +dynamic direction label updates
                              # +damping factor conditional disable
                              # +algorithm-aware score labels in bar chart + network graph
                              # +algorithm parameter in API payload

src/static/css/
└── controls.css              # +disabled state styling for damping factor
                              # +algorithm selector styling

src/templates/
└── index.html                # +algorithm selector dropdown
                              # +tooltip on damping factor

tests/unit/
└── test_pyspark.py           # +test_run_hits_basic
                              # +test_hits_authority_vs_hub
                              # +test_hits_vs_pagerank_differ
                              # +test_hits_with_league_filter
                              # +test_hits_with_count_weight

tests/integration/
└── test_api.py               # +test_hits_endpoint
                              # +test_hits_authority_ranking
                              # +test_hits_empty_state
                              # +test_algorithm_selector_default
```

**Structure Decision**: Follows the existing single-project layout. The HITS function is added to `processing.py` alongside `run_pagerank()` since both are graph algorithms operating on the same RDD inputs. A single new API endpoint (or extension of the existing one) routes to the correct algorithm.

## Phase 0: Research ✅ Complete

See [research.md](./research.md).

All technical unknowns resolved:
- HITS algorithm formulation: standard iterative Hub/Authority mutual reinforcement with L2 normalization
- Hub/Authority direction mapping: Buyers → Authority (attract incoming edges), Sellers → Hub (distribute outgoing edges)
- Weighted HITS: edge weights incorporated during Authority/Hub update steps as multiplicative factors
- Normalization: L2 norm applied after each iteration to both Hub and Authority vectors
- Convergence: fixed iteration count (same parameter as PageRank), no early-stop needed
- API design: extend existing `/api/pagerank` endpoint with `algorithm` field vs. new endpoint → chosen to keep single endpoint for simplicity
- Damping factor: not sent to backend when HITS is selected; backend ignores it for HITS

## Phase 1: Design & Contracts ✅ Complete

See [data-model.md](./data-model.md) and [contracts/api.md](./contracts/api.md).

### Backend Design

**`src/core/processing.py` changes:**

1. **`run_hits(edges_rdd, iterations=10)`** — new top-level function:
   - Initializes hub and authority scores to 1.0 for each node
   - Each iteration:
     - **Authority update**: For each node, sum the hub scores of nodes pointing to it (weighted by edge weight)
     - **Hub update**: For each node, sum the authority scores of nodes it points to (weighted by edge weight)
     - **Normalize**: L2-normalize both hub and authority score vectors
   - Returns a tuple: `(authority_ranks_rdd, hub_ranks_rdd)` — each is an RDD of `(node_id, score)`
   - Uses same RDD operations as `run_pagerank()`: `.join()`, `.flatMap()`, `.reduceByKey(add)`, `.mapValues()`

2. **`TransferAnalyzer.get_rankings(direction, iterations, damping, algorithm="pagerank")`** changes:
   - New `algorithm` parameter (default `"pagerank"` for backward compatibility)
   - If `algorithm == "pagerank"`: existing behavior (calls `run_pagerank()`)
   - If `algorithm == "hits"`: calls `run_hits()`, returns Authority scores for `direction == "buyers"`, Hub scores for `direction == "sellers"`

3. **`TransferAnalyzer.get_top_graph()`** changes:
   - Accepts new `algorithm` parameter, passes to `get_rankings()`
   - Adds to `meta` dict: `algorithm` (string), `score_type` (one of `"pagerank"`, `"authority"`, `"hub"`)

**`src/app.py` changes:**

1. **`CalculationRequest`** — extend Pydantic model:
   ```python
   algorithm: str = Field("pagerank", pattern="^(pagerank|hits)$")
   ```

2. **`POST /api/pagerank`** — pass `algorithm` to `TransferAnalyzer.get_top_graph()` and include `algorithm` + `score_type` in response `meta`.

### Frontend Design

**`src/static/js/graph.js` changes:**

1. **Algorithm selector**: Reference new `<select id="algorithm">` element. Add `change` event listener with same debounce pattern as league/weight controls.

2. **Direction label update**: When algorithm selector changes:
   - If `"hits"`: update direction `<option>` text to `"Authority (Buyers)"` / `"Hub (Sellers)"`
   - If `"pagerank"`: revert to `"Attractors (Buyers)"` / `"Suppliers (Sellers)"`

3. **Damping factor toggle**: When algorithm changes:
   - If `"hits"`: set `damping.disabled = true`, add tooltip text, add `.disabled` CSS class to parent
   - If `"pagerank"`: re-enable, remove tooltip, remove CSS class

4. **Score labels in visualization**:
   - Bar chart dataset label: use `meta.score_type` → `"PageRank Score"`, `"Authority Score"`, or `"Hub Score"`
   - Network graph node label: use `"Rank:"` for PageRank, `"Auth:"` or `"Hub:"` for HITS

5. **API payload**: Include `algorithm` field from selector value in POST body.

### HTML Template Changes

The `<form>` in `src/templates/index.html` needs:
- `<select id="algorithm">` — algorithm selector with options "PageRank" and "HITS"
- `title` attribute or `<small>` element on dampening factor for tooltip when disabled

## Implementation Sequence

Tasks are broken into user-story-aligned increments, each independently testable:

1. **Backend HITS core** — `run_hits()` function + unit tests
2. **Backend algorithm dispatch** — `TransferAnalyzer.get_rankings()` + `get_top_graph()` algorithm parameter + unit tests
3. **Backend API extension** — `CalculationRequest.algorithm` field + response meta + integration tests
4. **Frontend algorithm selector** — HTML control + auto-run listener + API payload
5. **Frontend damping factor toggle** — conditional disable/enable + tooltip + CSS
6. **Frontend direction labels** — dynamic text update on algorithm change
7. **Frontend score labels** — algorithm-aware labels in bar chart + network graph
8. **Integration tests** — end-to-end HITS happy path + algorithm comparison + edge cases

*(Full task breakdown generated by `/speckit.tasks`)*
