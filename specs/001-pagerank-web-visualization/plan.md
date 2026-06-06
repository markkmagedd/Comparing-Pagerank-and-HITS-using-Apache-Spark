# Implementation Plan: PageRank Web Visualization

**Branch**: `001-pagerank-web-visualization` | **Date**: 2026-03-19 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-pagerank-web-visualization/spec.md`

## Summary

Build an interactive FastAPI + PySpark web application that accepts user-controlled algorithm parameters (direction, iterations, damping factor, top N), runs PageRank against a football transfer dataset (`transfers.csv`), and renders the resulting topology as either an interactive node-link network graph (via **Cytoscape.js**) or an interactive bar chart. Both views must support clicking an element to display a detailed overlay panel. The network graph must display each node's computed rank directly beneath its team name. Nodes must be rendered at a deliberately large base size for legibility. The bar chart is the default view on page load or after re-running a computation.

---

## Technical Context

**Language/Version**: Python 3.12 (backend), Vanilla HTML/CSS/JS (frontend)  
**Primary Dependencies**: FastAPI, Uvicorn, PySpark 3.x, Jinja2, Cytoscape.js 3.26.x, Chart.js 4.x (bar chart)  
**Storage**: No persistent database — stateless computation against a local `transfers.csv` at runtime  
**Testing**: pytest (unit + integration), httpx (async API tests)  
**Target Platform**: Local server (macOS/Linux). Browser client (Chrome/Firefox/Safari modern)  
**Project Type**: Single-project web service (Python backend + embedded HTML/JS frontend)  
**Performance Goals**: UI interaction latency < 100ms. Algorithm computation time is strictly Spark-bound; no artificial UI delays.  
**Constraints**: Spark JVM must be started exactly once via ASGI lifespan. Top-N capping ensures graph payloads remain < 50 nodes to prevent browser jank.  
**Scale/Scope**: Single-user local analytics tool. PySpark runs in `local[1]` or `local[*]` mode — no cluster needed.

---

## Constitution Check

*GATE: Must pass before implementation.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Safe App Initialization | ✅ PASS | SparkSession is created in ASGI `lifespan`, not at module import time. `processing.py` has no top-level side effects. |
| Separation of Concerns | ✅ PASS | `processing.py` owns all PySpark logic; `app.py` owns routing/request lifecycle; frontend JS owns rendering exclusively. |
| Lean Architecture | ✅ PASS | No ORM, no message broker, no separate frontend build step. Vanilla JS + CDN-loaded libraries only. |
| Testability | ✅ PASS | PySpark logic is independently testable via unit tests using a local SparkSession fixture. API is testable via HTTPX AsyncClient. |
| FR Coverage | ⚠️ PARTIAL | FR-008 (rank beneath node label), FR-009 (bar chart toggle + default), FR-010 (large base node size) are **not yet implemented**. `tasks.md` must be updated to track these. |

**Gate Decision**: Proceed. No violations. Phase 3 tasks must now cover FR-008, FR-009, and FR-010 as a follow-on.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-pagerank-web-visualization/
├── spec.md              # Feature specification (source of truth)
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: API entity shapes
├── quickstart.md        # Phase 1: Developer onboarding guide
├── contracts/
│   └── graph_api.yaml   # Phase 1: OpenAPI 3.0 contract
├── checklists/
│   └── requirements.md  # Spec quality validation checklist
└── tasks.md             # Phase 2 output (speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── app.py                  # FastAPI app, lifespan, routes, Pydantic schemas
├── core/
│   ├── __init__.py
│   └── processing.py       # TransferAnalyzer + run_pagerank (PySpark RDD logic)
├── static/
│   ├── css/
│   │   └── style.css       # Base dark-mode stylesheet
│   └── js/
│       └── graph.js        # API client + Cytoscape.js + Chart.js rendering logic
└── templates/
    └── index.html          # Jinja2 HTML shell: sidebar form + main canvas area

tests/
├── unit/
│   └── test_pyspark.py     # Unit tests for processing.py (SparkContext-level)
└── integration/
    └── test_api.py         # Integration tests for FastAPI endpoints via HTTPX
```

**Structure Decision**: Single-project web service. Python backend serves both the HTML template and the `/api/pagerank` REST endpoint. Frontend is embedded HTML/JS (no bundler). This matches the research decision to avoid Node.js compilation overhead for a Bachelors-scale project.

---

## Phase 0: Research (Complete ✅)

All NEEDS CLARIFICATIONs resolved. See [research.md](./research.md).

| Topic | Decision |
|-------|----------|
| Web Framework | FastAPI — native async, lightweight, easy Pydantic validation |
| Graph Renderer | Cytoscape.js — built for node-link graphs, physics layout, tap events |
| Bar Chart Renderer | **Chart.js** — lightweight, well-documented, supports canvas-based click events consistent with the overlay interaction pattern already established for Cytoscape nodes |
| PySpark Integration | Long-lived `SparkSession` shared across requests via ASGI lifespan hook |
| Data Scoping | Top-N capping done in PySpark `takeOrdered()` stage before serialization |

### New Research: Bar Chart Toggle (FR-009)

**Decision**: Chart.js 4.x  
**Rationale**: FR-009 requires an interactive bar chart where clicking a bar fires the same overlay as a node click. Chart.js exposes an `onClick` callback receiving the bar's data index, enabling direct look-up of the node payload already held in memory from the last API response. This avoids re-fetching. Chart.js is loaded via CDN (same pattern as Cytoscape.js), requires zero build tooling, and renders on a `<canvas>` element — consistent with the `<canvas>`-based Cytoscape renderer.  
**Alternatives considered**: Plotly.js (larger bundle, more complex python-first API), D3.js (requires significant custom layout work for basic bar charts), pure SVG (too low-level for a time-constrained project).

---

## Phase 1: Design & Contracts (Complete ✅)

### Data Model

See [data-model.md](./data-model.md). No changes required — existing entities cover the bar chart view since both views consume the same API response payload (`nodes[]`, `edges[]`).

### API Contract

See [contracts/graph_api.yaml](./contracts/graph_api.yaml). The existing contract remains valid. No new endpoints are needed; FR-009 (bar chart) is a pure frontend concern using the same API response.

### Frontend Architecture (Updated for FR-008, FR-009, FR-010)

The frontend now has a **dual-renderer** architecture controlled by a toggle in the sidebar. A single shared `lastResult` variable holds the last successful API response. Both renderers read from this cache, enabling instant switching without re-running the algorithm.

```
graph.js responsibilities:
 ├── API fetch + error handling
 ├── renderNetwork(data)   → Cytoscape.js (FR-008, FR-010 affected)
 │     ├── label = "data(id)" + "\n" + "data(rank)" (rank beneath name)
 │     ├── base node size: minSize = 80px (larger floor)
 │     └── tap(node) → showOverlay(node.data)
 ├── renderBarChart(data)  → Chart.js (FR-009)
 │     ├── x-axis = node IDs, y-axis = rank scores
 │     ├── onClick(bar)    → showOverlay(node at index)
 │     └── destroyed on toggle away
 ├── showOverlay(nodeData) → shared overlay panel
 └── vizToggle (Network ↔ Bar Chart) → default: Bar Chart
```

### Quickstart

See [quickstart.md](./quickstart.md). Updated to include `chart.js` CDN note and the viz toggle behavior.

---

## Implementation Phases (Forward-Looking)

### Phase 3 Addendum: Visual Enhancements (FR-008, FR-009, FR-010)

These tasks are not yet complete and are the **primary output** to be tracked in `tasks.md`.

| Task ID | Description | Files Affected |
|---------|-------------|----------------|
| T020 | Add Chart.js CDN script tag to `index.html` | `src/templates/index.html` |
| T021 | Add Visualization Type toggle control (Network / Bar Chart) to sidebar, defaulting to Bar Chart | `src/templates/index.html` |
| T022 | Implement `renderBarChart(data)` in `graph.js` using Chart.js. Bars = top-N nodes by rank. `onClick` fires `showOverlay()`. | `src/static/js/graph.js` |
| T023 | Implement `renderNetwork(data)` updated function: rank label beneath node name (FR-008), base node `minSize = 80` (FR-010) | `src/static/js/graph.js` |
| T024 | Wire toggle control event: switching to Bar Chart destroys Cytoscape instance; switching to Network destroys Chart.js instance. Re-render from `lastResult`. | `src/static/js/graph.js` |
| T025 | Set Bar Chart as default view on initial page load (FR-009 requirement) | `src/static/js/graph.js` |
| T026 | Add `label` field to API node response in `app.py` (currently only `id` and `rank` in `cy_nodes`) | `src/app.py` |
| T027 | Integration test: verify `/api/pagerank` response nodes include `label` field | `tests/integration/test_api.py` |
| T028 | Update `tasks.md` to include T020–T027 and mark previous tasks as complete | `specs/001-pagerank-web-visualization/tasks.md` |

---

## Complexity Tracking

No constitution violations. Architecture remains a single-project web service. The bar chart uses the **existing API response** without any new backend endpoints, preserving the lean architecture principle.

---

## Artifact Summary

| Artifact | Status | Path |
|----------|--------|------|
| `spec.md` | ✅ Final (updated 2026-03-19) | specs/001-pagerank-web-visualization/spec.md |
| `research.md` | ✅ Complete (Bar Chart decision added in plan) | specs/001-pagerank-web-visualization/research.md |
| `data-model.md` | ✅ No changes needed | specs/001-pagerank-web-visualization/data-model.md |
| `contracts/graph_api.yaml` | ✅ No changes needed | specs/001-pagerank-web-visualization/contracts/graph_api.yaml |
| `quickstart.md` | ✅ Valid | specs/001-pagerank-web-visualization/quickstart.md |
| `plan.md` | ✅ **This file** | specs/001-pagerank-web-visualization/plan.md |
| `tasks.md` | ⚠️ Needs T020–T028 appended | specs/001-pagerank-web-visualization/tasks.md |
