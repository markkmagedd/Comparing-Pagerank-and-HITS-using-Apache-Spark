# Tasks: PageRank Web Visualization

**Input**: Design documents from `/specs/001-pagerank-web-visualization/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure (`src/core`, `src/static/css`, `src/static/js`, `src/templates`, `tests/unit`, `tests/integration`)
- [X] T002 Initialize Python virtual environment and install dependencies (fastapi, uvicorn, pyspark, jinja2) in `requirements.txt`
- [X] T003 [P] Configure basic linting rules in `.flake8` and gitignore configurations

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented
**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Build the `TransferAnalyzer` core module in `src/core/processing.py` to safely import PageRank logic without triggering top-level execution
- [X] T005 Initialize the FastAPI application and global PySpark `SparkSession` via ASGI lifespan in `src/app.py`
- [X] T006 Add CORS middleware and `/static` file mounting config in `src/app.py`
- [X] T007 Setup testing framework stubs in `tests/integration/test_api.py` and `tests/unit/test_pyspark.py`

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — View Buyer/Seller PageRank (Priority: P1) 🎯 MVP

**Goal**: Access a web interface where users can trigger the PageRank algorithm with adjustable parameters and view the resulting interactive visualization.

**Independent Test**: Launch the web page, configure parameters, click Run, and verify the buyers/sellers graph visualization renders in the browser.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Integration test for `/api/pagerank` POST endpoint response shape in `tests/integration/test_api.py`
- [X] T009 [P] [US1] Unit test ensuring `damping_factor`, `top_n`, and `iterations` parameters correctly modify output arrays in `tests/unit/test_pyspark.py`

### Implementation for User Story 1

- [X] T010 [P] [US1] Create the `CalculationRequest` Pydantic schema in `src/app.py` matching `data-model.md` and `contracts/graph_api.yaml`
- [X] T011 [US1] Implement `/api/pagerank` POST endpoint in `src/app.py` (depends on T004 & T010)
- [X] T012 [P] [US1] Create the HTML shell with sidebar parameter form (Direction, Iterations, Damping Factor, Top N, Run button) in `src/templates/index.html`
- [X] T013 [P] [US1] Create base dark-mode styling in `src/static/css/style.css`
- [X] T014 [US1] Implement API fetch and Cytoscape.js network graph rendering in `src/static/js/graph.js`
- [X] T015 [US1] Integrate loading spinner and status indicator while algorithm computes in `src/static/js/graph.js`

**Checkpoint**: User Story 1 fully functional and independently testable

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T016 Setup default page load via FastAPI Jinja2 template hook in `src/app.py` with `GET /` returning `index.html`
- [X] T017 Verify exception handling across PySpark dataset loading within the `/api/pagerank` route in `src/app.py`
- [X] T018 Code cleanup and reducer-speed optimization in `src/core/processing.py`
- [X] T019 Update `README.md` at project root wrapping notes from `quickstart.md`

---

## Phase 5: Visual Enhancements (FR-008, FR-009, FR-010) 🎯 Active

**Goal**: Display rank labels beneath node names in the network graph (FR-008), offer a Bar Chart visualization type that is the default view (FR-009), and render nodes at a larger legible base size (FR-010).

**Spec References**:
- **FR-008**: Node's computed rank MUST appear directly beneath the team name in the network graph
- **FR-009**: Visualization type toggle (Network Graph ↔ Bar Chart). Bar chart must fire the same overlay on click. Bar Chart is the default on load and after computation
- **FR-010**: Network graph nodes MUST use a deliberately larger base size for legibility

**Independent Test**: Load the page — Bar Chart must appear by default. Run algorithm — Bar Chart renders. Click a bar — overlay appears. Toggle to Network Graph — nodes are large, rank labels are visible beneath names. Click a node — same overlay appears.

### Implementation for Phase 5

- [X] T020 [P] [US1] Add Chart.js 4.x CDN `<script>` tag to `src/templates/index.html` (below the existing Cytoscape.js script)
- [X] T021 [P] [US1] Add Visualization Type toggle control (two-button pill: "Bar Chart" | "Network Graph") to the sidebar in `src/templates/index.html`; default selected state: Bar Chart
- [X] T022 [US1] Implement `renderBarChart(data)` in `src/static/js/graph.js` using Chart.js: horizontal bar chart, x-axis = rank score, y-axis = team names sorted by rank descending; `onClick` callback calls shared `showOverlay(nodeData)` function
- [X] T023 [US1] Update `renderNetwork(data)` in `src/static/js/graph.js`: set node label to display team name + `"\n"` + rank value beneath it using Cytoscape `text-wrap: 'wrap'` and a `label` data function; set minimum node `width`/`height` to `80px` (FR-010)
- [X] T024 [US1] Wire toggle control event listener in `src/static/js/graph.js`: switching to Bar Chart destroys the active Cytoscape instance and calls `renderBarChart(lastResult)`; switching to Network Graph destroys the Chart.js instance and calls `renderNetwork(lastResult)`
- [X] T025 [US1] Set Bar Chart as the default rendered view on form submit completion: after receiving a successful API response, call `renderBarChart(data)` first and activate the "Bar Chart" toggle button (FR-009)
- [X] T026 [P] [US1] Add `label` field to the API node response objects in `src/app.py` (currently `cy_nodes` only includes `id` and `rank`; add `"label": n["id"]` to each node's `data` dict)
- [X] T027 [P] [US1] Update integration test in `tests/integration/test_api.py` to assert that each node object in the response contains a `label` field
- [X] T028 [P] [US1] Add CSS styles for the visualization toggle pill (two-button switcher) and Chart.js canvas container to `src/static/css/style.css`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately ✅ Complete
- **Foundational (Phase 2)**: Depends on Phase 1 ✅ Complete
- **User Story MVP (Phase 3)**: Depends on Phase 2 ✅ Complete
- **Polish (Phase 4)**: Depends on Phase 3 ✅ Complete
- **Visual Enhancements (Phase 5)**: Depends on Phase 3 completion — **active now**

### Phase 5 Parallel Opportunities

- **T020, T021, T028** (HTML/CSS structure) can run in parallel with each other — different files, no shared state
- **T026, T027** (API label field + its test) can run in parallel — `app.py` and `test_api.py` are independent
- **T022, T023** (bar chart + network renderers) can be written in parallel as separate functions if `lastResult` and `showOverlay` stubs are defined first
- **T024, T025** depend on T022 and T023 being complete

### Suggested Execution Order for Phase 5

```
[Parallel batch 1]  T020, T021, T028, T026, T027
[Sequential]        T022 (bar chart renderer)
[Sequential]        T023 (network renderer update)
[Sequential]        T024 (toggle wiring)
[Sequential]        T025 (default to bar chart on submit)
```

---

## Implementation Strategy

### MVP Already Delivered (US1 core)

1. ✅ Phase 1: Setup
2. ✅ Phase 2: Foundational
3. ✅ Phase 3: User Story 1 (Cytoscape network graph)
4. ✅ Phase 4: Polish

### Current Sprint: Phase 5 Visual Enhancements

5. Complete T020–T028 in parallel batches above
6. **VALIDATE**: Manually run the server, load the browser, confirm Bar Chart is default, toggle works, overlay fires on bar click, rank labels appear under node names, nodes are visibly larger

### Task Counts

| Phase | Total | Completed | Remaining |
|-------|-------|-----------|-----------|
| Phase 1: Setup | 3 | 3 | 0 |
| Phase 2: Foundational | 4 | 4 | 0 |
| Phase 3: User Story 1 | 8 | 8 | 0 |
| Phase 4: Polish | 4 | 4 | 0 |
| Phase 5: Visual Enhancements | 9 | 0 | **9** |
| **Total** | **28** | **19** | **9** |
