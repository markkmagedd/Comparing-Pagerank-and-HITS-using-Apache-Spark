# Tasks: Data-Driven Customization

**Branch**: `002-data-driven-customization`  
**Input**: Design documents from `/specs/002-data-driven-customization/`  
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/api.md ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths are included in every description

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project wiring and confirm the existing stack is ready for extension.

- [x] T001 Confirm `transfers.csv` is present at repo root and verify column indices (Name=0, Team_from=3, League_from=4, Team_to=5, League_to=6, Transfer_fee=9) by running `head -3 transfers.csv`
- [x] T002 Confirm existing tests pass with `pytest tests/` — establishes baseline before any changes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared backend infrastructure that ALL user stories depend on — must be complete before Phase 3+.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Add `get_available_leagues(sc, file_path)` top-level function to `src/core/processing.py` — reads raw lines, skips header, unions `League_from` (col 4) and `League_to` (col 6) values, calls `.distinct().collect()`, returns `sorted(list[str])`
- [x] T004 Add `GET /api/leagues` endpoint to `src/app.py` — calls `get_available_leagues(spark.sparkContext, "transfers.csv")` and returns `{"leagues": [...]}`
- [x] T005 Extend `CalculationRequest` Pydantic model in `src/app.py` with two new optional fields: `league: str = Field("all")` and `weight_mode: str = Field("fee", pattern="^(fee|count)$")` — defaults preserve backward compatibility
- [x] T006 Refactor `TransferAnalyzer._load_data()` in `src/core/processing.py` to accept `league: str = "all"` and `weight_mode: str = "fee"` parameters; update `__init__` signature to pass them through
- [x] T007 Implement league filter predicate in `TransferAnalyzer._load_data()` in `src/core/processing.py`: when `league != "all"`, apply `.filter(lambda x: x[4].strip() == league and x[6].strip() == league)` on the raw data RDD before the weight aggregation map step
- [x] T008 Implement weight mode branch in `TransferAnalyzer._load_data()` in `src/core/processing.py`: when `weight_mode == "count"`, map each row to `((x[3].strip(), x[5].strip()), 1)` instead of `((x[3].strip(), x[5].strip()), parse_fee(x[9]))`; keep existing fee path unchanged
- [x] T009 Add `weight_label` field to each edge dict in `TransferAnalyzer.get_top_graph()` in `src/core/processing.py`: `f"€{weight/1_000_000:.0f}M"` for fee mode, `f"{int(weight)} deals"` for count mode
- [x] T010 Add `meta` dict to `TransferAnalyzer.get_top_graph()` return value in `src/core/processing.py`: `{"league": league, "weight_mode": weight_mode, "total_records": <count of filtered transfers>, "empty": <bool>}`
- [x] T011 Update `POST /api/pagerank` handler in `src/app.py` to pass `req.league` and `req.weight_mode` to the `TransferAnalyzer` constructor, and include `weight_label` on each edge and `meta` in the response body

**Checkpoint**: Backend fully extended — `GET /api/leagues` returns leagues, `POST /api/pagerank` accepts and applies `league` + `weight_mode`, response includes `meta` and `weight_label`. Run `pytest tests/` to confirm no regressions.

---

## Phase 3: User Story 1 — Filter Analysis to a Specific League (Priority: P1) 🎯 MVP

**Goal**: The user selects a single league from a dropdown; the analysis reruns (auto-debounced) using only intra-league transfer records and the graph/chart updates to show only clubs from that league. Selecting "All Leagues" restores the full dataset.

**Independent Test**: Open the UI, select "Premier League" from the league dropdown, wait for auto-run, verify that all visible club nodes/bars belong to Premier League clubs. Then select "All Leagues" and confirm the full multi-league result returns. Verify the loading overlay appears and disappears correctly.

### Implementation for User Story 1

- [x] T012 [US1] Add `<select id="league">` HTML control to the controls panel in `src/templates/index.html` — include a placeholder "Loading leagues…" `<option>` and an "All Leagues" `<option value="all">` as first item; add `<div id="viz-loading" class="hidden">` overlay element inside the visualization area wrapper; add `<div id="empty-state" class="hidden">` message element inside the visualization area wrapper
- [x] T013 [US1] Add CSS rules for `#viz-loading` (semi-transparent overlay with centered spinner over the viz area), `#empty-state` (centered message text), and the `hidden` utility class to `src/static/css/` (create new file `src/static/css/controls.css` or extend existing stylesheet)
- [x] T014 [US1] Implement `loadLeagues()` async function in `src/static/js/graph.js`: calls `GET /api/leagues`, populates `<select id="league">` with "All Leagues" as first option followed by sorted league names, handles fetch error gracefully (logs warning, leaves dropdown with "All Leagues" only)
- [x] T015 [US1] Call `loadLeagues()` on `DOMContentLoaded` in `src/static/js/graph.js` (add after existing control setup code)
- [x] T016 [US1] Extract existing form-submit logic into a reusable `triggerAnalysis()` async function in `src/static/js/graph.js`; include showing `#viz-loading` overlay at start and hiding it on completion/error; include hiding `#empty-state` at start
- [x] T017 [US1] Add debounced auto-run: in `src/static/js/graph.js`, declare `let debounceTimer = null`; attach `change` event listener to `<select id="league">` that calls `clearTimeout(debounceTimer); debounceTimer = setTimeout(triggerAnalysis, 300)`
- [x] T018 [US1] Update `triggerAnalysis()` in `src/static/js/graph.js` to include `league: document.getElementById('league').value` in the `POST /api/pagerank` request payload
- [x] T019 [US1] Add empty-state rendering to `triggerAnalysis()` in `src/static/js/graph.js`: when `response.meta.empty === true`, hide viz containers (`#cy-container`, `#chart-container`) and show `#empty-state` with message "No data available for the selected league."; when `meta.empty === false`, hide `#empty-state` and show active viz container
- [x] T020 [US1] Write unit test for `get_available_leagues()` in `tests/unit/test_pyspark.py`: assert it returns a non-empty sorted list of strings, assert "LaLiga" and "Premier League" are in the result
- [x] T021 [US1] Write unit test for league filter in `tests/unit/test_pyspark.py`: instantiate `TransferAnalyzer(spark, "transfers.csv", league="LaLiga")`, call `get_top_graph(top_n=5)`, assert `meta["league"] == "LaLiga"`, assert `meta["empty"] == False`, assert `meta["total_records"] > 0`
- [x] T022 [US1] Write integration test for `GET /api/leagues` in `tests/integration/test_api.py`: assert `200`, `"leagues"` key in response, list is non-empty and sorted
- [x] T023 [US1] Write integration test for league filter via `POST /api/pagerank` in `tests/integration/test_api.py`: send `{"league": "Premier League", "weight_mode": "fee", "direction": "buyers", "iterations": 1, "top_n": 5}`, assert `200`, assert `meta.league == "Premier League"`, assert `meta.empty == False`
- [x] T024 [US1] Write integration test for empty-state response in `tests/integration/test_api.py`: send a league known to yield no intra-league transfers (e.g. a country-level label), assert `200`, assert `meta.empty == True`, assert `nodes == []` and `edges == []`

**Checkpoint**: League filter is fully functional end-to-end. Run `pytest tests/` — all tests pass. Demo: select "Premier League" → auto-run fires → loading overlay shown → results render → only PL clubs visible. Select "All Leagues" → full result returns.

---

## Phase 4: User Story 2 — Switch Between Transfer Fee and Transfer Count Weighting (Priority: P2)

**Goal**: The user toggles a weight mode selector between "Transfer Fee" and "Transfer Count"; the analysis reruns automatically; displayed rankings and edge/tooltip labels update to reflect the chosen weight mode.

**Independent Test**: With default settings, note the top-5 clubs. Switch weight mode to "Transfer Count" via the UI control, observe auto-run fires, confirm the ranking changes and edge labels now show deal counts (e.g., "12 deals"). Switch back to "Transfer Fee"; confirm original ranking and fee labels restore.

### Implementation for User Story 2

- [x] T025 [US2] Add `<select id="weight-mode">` HTML control to the controls panel in `src/templates/index.html` with two options: `<option value="fee">Transfer Fee</option>` and `<option value="count">Transfer Count</option>`; default selected = "fee"
- [x] T026 [US2] Attach `change` event listener on `<select id="weight-mode">` in `src/static/js/graph.js` using the same debounce pattern as the league control: `clearTimeout(debounceTimer); debounceTimer = setTimeout(triggerAnalysis, 300)`
- [x] T027 [US2] Update `triggerAnalysis()` in `src/static/js/graph.js` to include `weight_mode: document.getElementById('weight-mode').value` in the `POST /api/pagerank` request payload
- [x] T028 [US2] Update `renderBarChart()` in `src/static/js/graph.js` to use `n.data.weight_label` (from `meta.weight_mode`) as the Chart.js dataset label string: `"PageRank Score (${meta.weight_mode === 'count' ? 'Transfer Count' : 'Transfer Fee'})"` and pass `meta` into the function
- [x] T029 [US2] Update Cytoscape edge tooltip / `showOverlay()` in `src/static/js/graph.js` to display `edge.data.weight_label` (e.g., "€45M" or "12 deals") when a node is selected and its edges are inspected; update `showOverlay` to accept and display the active weight label context
- [x] T030 [US2] Write unit test for count weight mode in `tests/unit/test_pyspark.py`: instantiate `TransferAnalyzer(spark, "transfers.csv", weight_mode="count")`, call `get_top_graph(top_n=5)`, assert `meta["weight_mode"] == "count"`, assert each edge has a `weight_label` ending in `"deals"`, assert all edge `weight` values are positive integers
- [x] T031 [US2] Write unit test asserting fee and count modes produce different rankings in `tests/unit/test_pyspark.py`: run `get_top_graph` with `weight_mode="fee"` and `weight_mode="count"`, collect top-1 club from each, assert they are not always identical (or that edge weights differ)
- [x] T032 [US2] Write integration test for weight mode toggle via `POST /api/pagerank` in `tests/integration/test_api.py`: send two requests — one with `weight_mode="fee"`, one with `weight_mode="count"` — assert both return `200`, assert `meta.weight_mode` echoes the requested mode, assert `edges[0].data.weight_label` ends with "M" for fee and "deals" for count

**Checkpoint**: Weight mode toggle is fully functional. Run `pytest tests/`. Demo: toggle "Transfer Count" → auto-run fires → rankings update → edge labels show "X deals". Toggle back to "Transfer Fee" → fee labels restore. League filter remains unaffected throughout.

---

## Phase 5: User Story 3 — Combine League Filter and Weight Mode (Priority: P3)

**Goal**: Both controls work orthogonally — changing one does not reset the other. The analysis correctly applies both the active league filter and the active weight mode simultaneously on every run.

**Independent Test**: Set league = "La Liga", weight = "Transfer Count", run analysis. Change weight to "Transfer Fee" without touching the league control — confirm league stays "La Liga" and only the weight label/ranking changes. Reset both controls to defaults — confirm "All Leagues" + "Transfer Fee" baseline is restored.

### Implementation for User Story 3

- [x] T033 [US3] Verify in `triggerAnalysis()` in `src/static/js/graph.js` that both `league` and `weight_mode` are read from their respective controls on every call — confirm neither control resets the other's DOM value when a result arrives (read state, do not write it back)
- [x] T034 [US3] Add a "Reset to Defaults" button `<button id="reset-controls">Reset</button>` to the controls panel in `src/templates/index.html`; attach click handler in `src/static/js/graph.js` that sets `document.getElementById('league').value = 'all'` and `document.getElementById('weight-mode').value = 'fee'`, then calls `triggerAnalysis()` immediately (no debounce)
- [x] T035 [US3] Write integration test for combined controls in `tests/integration/test_api.py`: send `POST /api/pagerank` with `{"league": "LaLiga", "weight_mode": "count", ...}`, assert `meta.league == "LaLiga"` and `meta.weight_mode == "count"` simultaneously; send second request with `{"league": "LaLiga", "weight_mode": "fee", ...}`, assert `meta.league` is still `"LaLiga"` and `meta.weight_mode == "fee"`

**Checkpoint**: All three user stories functional. Run full `pytest tests/`. Demo combined scenario: set La Liga + Transfer Count → analysis runs; change to Transfer Fee → La Liga stays, rankings update; reset → All Leagues + Transfer Fee restored.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: UX refinements, robustness, and test cleanup across all stories.

- [x] T036 [P] Add loading overlay CSS transition (fade-in/out) to `src/static/css/controls.css` so the overlay appearance is smooth rather than abrupt
- [x] T037 [P] Disable both `<select id="league">` and `<select id="weight-mode">` controls during active computation in `triggerAnalysis()` in `src/static/js/graph.js` and re-enable them on completion/error — prevents double-fire during debounce window
- [x] T038 [P] Add `aria-label` attributes to `<select id="league">` and `<select id="weight-mode">` in `src/templates/index.html` for accessibility
- [x] T039 Add a brief visible indicator (e.g., small badge or italicised text below the control) showing the active filter state (e.g., "Filtered: Premier League · Count") in `src/templates/index.html` and update it dynamically from `meta` in `src/static/js/graph.js`
- [x] T040 [P] Update `tests/unit/test_pyspark.py` fixture docstring and add a teardown `spark.stop()` safeguard — ensure Spark session is cleanly closed in all test failure paths
- [x] T041 Run `pytest tests/ -v` and confirm all tests pass with no warnings; document any known league names that yield empty intra-league graphs as a comment in `src/core/processing.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS all user stories**
- **Phase 3 (US1)**: Depends on Phase 2 — can start once foundational backend is complete
- **Phase 4 (US2)**: Depends on Phase 2 — can start in parallel with Phase 3 (different files: `weight_mode` param already wired in Phase 2)
- **Phase 5 (US3)**: Depends on Phases 3 and 4 completing — validates their orthogonality
- **Phase 6 (Polish)**: Depends on Phase 5

### User Story Dependencies

- **US1 (P1)**: Depends on foundational backend (T003–T011). Frontend-heavy.
- **US2 (P2)**: Depends on foundational backend (T003–T011). Can begin in parallel with US1 since it touches different HTML elements and `weight_mode` is already wired in the backend.
- **US3 (P3)**: Depends on US1 and US2 completing. Minimal new code — mostly validation + a reset button.

### Within Each User Story

- Backend changes (Phase 2) → HTML controls → JS wiring → tests
- Tests must fail before implementation of the feature they cover
- Do not reset control DOM values in JS on result render

### Parallel Opportunities

- T003 and T005 can be worked in parallel (different functions in different files)
- T006, T007, T008, T009, T010 are sequential within `processing.py` (same function chain)
- T012 and T013 (HTML + CSS) can run in parallel with T014–T016 (JS logic) since they touch different files
- T020–T024 (US1 tests) can all be written in parallel before implementation
- T025 (HTML) can be written in parallel with T026–T029 (JS) once Phase 2 is done
- T036, T037, T038, T040 (Phase 6) are all independent

---

## Parallel Example: Phase 2 Backend

```bash
# These can be started together (no file conflicts in Phase 2):
Task T003: get_available_leagues() in src/core/processing.py
Task T004: GET /api/leagues endpoint in src/app.py
Task T005: Extend CalculationRequest in src/app.py
# (T004 and T005 both touch app.py — coordinate or sequence them)

# Sequential chain after T003:
T006 → T007 → T008 → T009 → T010 → T011
```

## Parallel Example: User Story 1 Frontend

```bash
# Launch in parallel (different files):
Task T012: HTML controls + overlay elements in src/templates/index.html
Task T013: CSS overlay rules in src/static/css/controls.css

# After T012 + T013 complete:
Task T014: loadLeagues() in src/static/js/graph.js
Task T015: Call loadLeagues() on DOMContentLoaded in src/static/js/graph.js
# Then sequentially:
T016 → T017 → T018 → T019
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational backend (T003–T011) — **critical blocker**
3. Complete Phase 3: US1 League filter frontend (T012–T024)
4. **STOP and VALIDATE**: League dropdown populates, selecting "Premier League" auto-runs and shows only PL clubs, loading overlay appears and dismisses, empty state works
5. Demo / review before proceeding

### Incremental Delivery

1. Setup + Foundational (Phase 1+2) → backend API extended, all existing tests still pass
2. US1 complete (Phase 3) → League filter functional end-to-end (**MVP**)
3. US2 complete (Phase 4) → Weight mode toggle functional
4. US3 complete (Phase 5) → Combined controls validated, reset button added
5. Polish (Phase 6) → UX refinements and accessibility

---

## Notes

- `[P]` tasks operate on different files with no incomplete dependencies — safe to run concurrently
- `[Story]` label maps each task to a specific user story for traceability
- The debounce timer (`debounceTimer`) must be a single shared variable in `graph.js` — both `league` and `weight-mode` change listeners share it so rapid alternating changes still only fire one request
- `TransferAnalyzer` is instantiated per request in `app.py` — `league` and `weight_mode` are constructor params, not method params, to keep `_load_data()` self-contained
- League comparison is **case-sensitive** — values must match exactly as they appear in the CSV (e.g., `"LaLiga"` not `"La Liga"`)
- Commit after each phase checkpoint to keep history clean
