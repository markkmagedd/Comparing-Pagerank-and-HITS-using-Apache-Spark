# Tasks: HITS Algorithm Integration

**Input**: Design documents from `/specs/003-hits-algorithm/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new project setup needed — this feature extends the existing codebase. This phase covers the foundational algorithm code that all user stories depend on.

*(No setup tasks required — project structure, dependencies, and tooling are already in place.)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement the core HITS algorithm function and extend the backend to dispatch between algorithms. These tasks MUST be complete before any user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T001 Implement `run_hits(edges_rdd, iterations)` standalone function in src/core/processing.py — accepts the same `(source, (destination, weight))` edge RDD as `run_pagerank()`. Build forward and reverse link RDDs, iterate Hub/Authority mutual-reinforcement updates with L2 normalization per iteration, return `(authority_ranks_rdd, hub_ranks_rdd)` tuple. Follow the existing `run_pagerank()` pattern using `.groupByKey()`, `.join()`, `.flatMap()`, `.reduceByKey(add)`, `.mapValues()`. Cache both link RDDs.
- [x] T002 Add unit test `test_run_hits_basic` in tests/unit/test_pyspark.py — create a small hand-crafted edge RDD (3-4 nodes), call `run_hits()`, verify it returns a tuple of two RDDs (authority, hub), each containing scores for all nodes, and scores are positive floats summing to approximately 1.0 (L2-normalized).
- [x] T003 Extend `TransferAnalyzer.get_rankings()` in src/core/processing.py — add `algorithm="pagerank"` parameter (default preserves backward compat). If `algorithm == "hits"`, call `run_hits()` and return Authority scores for `direction == "buyers"` or Hub scores for `direction == "sellers"`. If `algorithm == "pagerank"`, call existing `run_pagerank()` unchanged.
- [x] T004 Extend `TransferAnalyzer.get_top_graph()` in src/core/processing.py — add `algorithm="pagerank"` parameter, pass to `get_rankings()`. Add `algorithm` (string) and `score_type` (one of `"pagerank"`, `"authority"`, `"hub"`) to the returned `meta` dictionary.
- [x] T005 Extend `CalculationRequest` Pydantic model in src/app.py — add `algorithm: str = Field("pagerank", pattern="^(pagerank|hits)$")`.
- [x] T006 Update `POST /api/pagerank` handler in src/app.py — pass `req.algorithm` to `analyzer.get_top_graph()`. The response already includes `meta`; the new `algorithm` and `score_type` keys are automatically included from the updated `get_top_graph()`.

**Checkpoint**: Backend can now compute HITS when `algorithm=hits` is sent in the API request, and returns results with correct `meta.algorithm` and `meta.score_type`. All existing PageRank functionality works identically with default `algorithm=pagerank`.

---

## Phase 3: User Story 1 — Run HITS Algorithm and View Results (Priority: P1) 🎯 MVP

**Goal**: User can select "HITS" in the UI, trigger a computation, and view Authority or Hub rankings in the existing bar chart or network graph visualizations.

**Independent Test**: Open the web interface, select "HITS" from the algorithm dropdown, click "Run", and verify that ranked club data appears in the bar chart with "Authority Score" or "Hub Score" labels.

### Implementation for User Story 1

- [x] T007 [US1] Add algorithm selector dropdown to src/templates/index.html — insert a `<select id="algorithm">` control in the sidebar form with options `<option value="pagerank" selected>PageRank</option>` and `<option value="hits">HITS</option>`. Place it as the first control in the form (above "Analysis Target").
- [x] T008 [US1] Update subtitle text in src/templates/index.html — change the static subtitle from "PySpark PageRank Visualization" to a generic "PySpark Graph Algorithm Visualization" (or make it dynamic via JS in T012).
- [x] T009 [US1] Add algorithm selector reference and auto-run listener in src/static/js/graph.js — reference `document.getElementById('algorithm')`, add a `change` event listener calling `debounceAnalysis()` (same 300ms debounce as league/weight controls). Add the algorithm selector to the list of controls disabled during computation and re-enabled after.
- [x] T010 [US1] Include `algorithm` field in API payload in src/static/js/graph.js — in the `triggerAnalysis()` function, add `algorithm: document.getElementById('algorithm').value` to the payload object sent to `POST /api/pagerank`.
- [x] T011 [US1] Update bar chart score label in src/static/js/graph.js — in `renderBarChart()`, replace the hardcoded `"PageRank Score (${weightDesc})"` dataset label with a dynamic label derived from `meta.score_type`: map `"pagerank"` → `"PageRank Score"`, `"authority"` → `"Authority Score"`, `"hub"` → `"Hub Score"`, appending `(${weightDesc})`.
- [x] T012 [US1] Update network graph node label in src/static/js/graph.js — in `renderNetwork()`, update the node label function to use the score type from `lastResult.meta.score_type`: display `"Rank:"` for pagerank, `"Auth:"` for authority, `"Hub:"` for hub, before the score value.
- [x] T013 [US1] Update error alert text in src/static/js/graph.js — change the hardcoded `"Error running PageRank algorithm"` message to `"Error running algorithm"` (algorithm-agnostic).
- [x] T014 [US1] Add unit test `test_hits_authority_vs_hub` in tests/unit/test_pyspark.py — create a `TransferAnalyzer` with the real dataset, call `get_top_graph(direction='buyers', algorithm='hits', iterations=1, top_n=5)` and verify `meta.score_type == "authority"`. Then call with `direction='sellers'` and verify `meta.score_type == "hub"`. Verify nodes are non-empty in both cases.
- [x] T015 [US1] Add integration test `test_hits_endpoint` in tests/integration/test_api.py — POST to `/api/pagerank` with `algorithm: "hits"`, `direction: "buyers"`, `iterations: 1`, `top_n: 5`. Assert status 200, `meta.algorithm == "hits"`, `meta.score_type == "authority"`, nodes list is non-empty.

**Checkpoint**: At this point, User Story 1 should be fully functional — user can select HITS, run analysis, and see Authority/Hub results with correct labels in the visualization.

---

## Phase 4: User Story 2 — Switch Between PageRank and HITS (Priority: P2)

**Goal**: User can seamlessly toggle between PageRank and HITS, with the algorithm selector triggering auto-run, damping factor disabling for HITS, and direction labels updating dynamically.

**Independent Test**: Run PageRank, note top-5 clubs. Switch to HITS (auto-runs). Verify results differ. Verify damping factor is greyed out. Verify direction labels show "Authority (Buyers)" / "Hub (Sellers)". Switch back to PageRank. Verify damping re-enables, direction labels revert.

### Implementation for User Story 2

- [x] T016 [US2] Implement damping factor conditional disable in src/static/js/graph.js — add a function `updateAlgorithmUI()` called on algorithm selector change: when `algorithm == "hits"`, set `damping.disabled = true`, add a `title` attribute "Not applicable to HITS algorithm" to the damping input, add class `disabled` to its parent `.form-group`. When `algorithm == "pagerank"`, reverse all changes.
- [x] T017 [US2] Add disabled state CSS styling in src/static/css/controls.css — add styles for `.form-group.disabled` that visually grey out the label, input, and small text (e.g., `opacity: 0.4`, `pointer-events: none` on the input, subtle "not-allowed" cursor on the group).
- [x] T018 [US2] Implement dynamic direction labels in src/static/js/graph.js — in the `updateAlgorithmUI()` function, update the `<option>` text content of the direction `<select>`: if `algorithm == "hits"`, set options to `"Authority (Buyers)"` / `"Hub (Sellers)"`; if `"pagerank"`, revert to `"Attractors (Buyers)"` / `"Suppliers (Sellers)"`. Preserve the selected `value` attribute (`"buyers"` / `"sellers"`) unchanged.
- [x] T019 [US2] Wire `updateAlgorithmUI()` to algorithm selector change event in src/static/js/graph.js — ensure `updateAlgorithmUI()` is called both on algorithm selector `change` events and on page load (to set initial state for default "pagerank").
- [x] T020 [US2] Add reset behavior for algorithm selector in src/static/js/graph.js — in the `resetBtn` click handler, add `algorithmSelect.value = 'pagerank'` and call `updateAlgorithmUI()` to re-enable damping and revert direction labels.
- [x] T021 [US2] Add unit test `test_hits_vs_pagerank_differ` in tests/unit/test_pyspark.py — run `get_top_graph(top_n=10, algorithm='pagerank')` and `get_top_graph(top_n=10, algorithm='hits')` on the same dataset. Assert that the node ID lists are not identical (rankings should differ for at least some positions), confirming distinct algorithms.
- [x] T022 [US2] Add integration test `test_algorithm_default` in tests/integration/test_api.py — POST to `/api/pagerank` WITHOUT the `algorithm` field. Assert `meta.algorithm == "pagerank"` and `meta.score_type == "pagerank"`, verifying backward compatibility.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work — user can switch algorithms freely, UI adapts dynamically, and defaults preserve backward compatibility.

---

## Phase 5: User Story 3 — HITS Works with Existing Filters (Priority: P3)

**Goal**: HITS integrates seamlessly with all existing controls: league filter, weight mode, direction, iterations, and Top N — ensuring feature parity with PageRank.

**Independent Test**: Set league to "Premier League", weight mode to "Transfer Count", algorithm to "HITS", run. Verify only Premier League clubs appear with count-based weighting. Change Top N and verify result count changes.

### Implementation for User Story 3

- [x] T023 [US3] Add unit test `test_hits_with_league_filter` in tests/unit/test_pyspark.py — create `TransferAnalyzer(spark, "transfers.csv", league="Premier League")`, call `get_top_graph(algorithm='hits', direction='buyers', iterations=1, top_n=5)`. Assert `meta.league == "Premier League"`, `meta.algorithm == "hits"`, non-empty nodes.
- [x] T024 [US3] Add unit test `test_hits_with_count_weight` in tests/unit/test_pyspark.py — create `TransferAnalyzer(spark, "transfers.csv", weight_mode="count")`, call `get_top_graph(algorithm='hits', direction='buyers', iterations=1, top_n=5)`. Assert `meta.weight_mode == "count"`, all edges have `"deals"` in `weight_label`.
- [x] T025 [US3] Add integration test `test_hits_empty_state` in tests/integration/test_api.py — POST to `/api/pagerank` with `algorithm: "hits"`, `league: "NON_EXISTENT_LEAGUE"`. Assert `meta.empty == True`, empty nodes list. Verifies empty-state handling works identically for HITS.
- [x] T026 [US3] Add integration test `test_hits_with_filters_integration` in tests/integration/test_api.py — POST with `algorithm: "hits"`, `league: "Premier League"`, `weight_mode: "count"`, `direction: "sellers"`, `iterations: 2`, `top_n: 5`. Assert `meta.algorithm == "hits"`, `meta.score_type == "hub"`, `meta.league == "Premier League"`, `meta.weight_mode == "count"`. Validates all controls compose correctly with HITS.

**Checkpoint**: All user stories should now be independently functional — HITS works with every existing filter combination.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple user stories

- [x] T027 [P] Add algorithm selector styling in src/static/css/controls.css — style the algorithm `<select>` to match existing controls. Optionally add a visual separator or heading distinguishing the algorithm selector from other parameter controls.
- [x] T028 Update the page `<title>` in src/templates/index.html — change from "PageRank Transfer Visualizer" to "Transfer Network Analyzer" (or similar algorithm-agnostic title) to reflect the dual-algorithm capability.
- [x] T029 Run full test suite and verify all existing tests pass — execute `pytest tests/` and confirm zero regressions in existing PageRank tests (test_pagerank_endpoint_calculation, test_pagerank_league_filter_integration, test_pagerank_weight_mode_integration, test_pagerank_empty_state_integration).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — extends existing codebase directly. BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion — delivers core HITS in UI.
- **User Story 2 (Phase 4)**: Depends on Phase 2 + Phase 3 (US1 must exist before switching between algorithms is meaningful).
- **User Story 3 (Phase 5)**: Depends on Phase 2 only — filter integration is independent of UI switching logic. Can run in parallel with US2.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2 → Can start immediately after foundational tasks
- **User Story 2 (P2)**: Depends on Phase 2 + US1 (needs algorithm selector from T007 and score labels from T011-T012)
- **User Story 3 (P3)**: Depends on Phase 2 → Can run in parallel with US2 (tests only, no new implementation needed)

### Within Each Phase

- T001 → T002 (implement then test)
- T003, T004 depend on T001 (need `run_hits()` to exist)
- T005, T006 depend on T003, T004 (API layer wraps processing layer)
- T007, T008 are parallelizable (different HTML sections)
- T009, T010, T011, T012 are sequential (all modify graph.js)
- T016, T017, T018 are partially parallel (T16/T18 in JS, T17 in CSS)

### Parallel Opportunities

```
Phase 2:  T001 → T002 → T003 → T004 → T005 + T006 (parallel, different files)
Phase 3:  T007 + T008 (parallel, same file but different sections)
          T009 → T010 → T011 → T012 → T013 (sequential, same file)
          T014 + T015 (parallel, different test files)
Phase 4:  T016 + T017 (parallel, JS + CSS)
          T018 → T019 → T020 (sequential, same file)
          T021 + T022 (parallel, different test files)
Phase 5:  T023 + T024 + T025 + T026 (all parallel, different test functions)
Phase 6:  T027 + T028 (parallel, different files)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001–T006)
2. Complete Phase 3: User Story 1 (T007–T015)
3. **STOP and VALIDATE**: Select HITS, run, verify Authority/Hub scores appear
4. Deploy/demo if ready — core HITS functionality is working

### Incremental Delivery

1. Phase 2 → Foundation ready (HITS computable via API)
2. Add User Story 1 → HITS visible in UI → Test → Demo (MVP!)
3. Add User Story 2 → Algorithm switching + UI adaptations → Test → Demo
4. Add User Story 3 → Filter integration validated → Test → Demo
5. Polish → Final cleanup and regression testing

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The HITS algorithm implementation (T001) is the single most critical task — everything else depends on it
- All existing PageRank tests must continue to pass throughout (backward compatibility)
