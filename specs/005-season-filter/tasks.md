---
description: "Task list for Season Range Filter implementation"
---

# Tasks: Season Range Filter

**Input**: Design documents from `/specs/005-season-filter/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project evaluation and targeting.

- [X] T001 [P] Review `src/templates/index.html` structure to identify where to inject the Season dropdown controls.
- [X] T002 [P] Review `src/core/processing.py` (referenced as `graph_jobs.py` in plan) to pinpoint where `transfers_df` is instantiated/cached before algorithm mapping.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

- [X] T003 Update the backend Pydantic API payload representations in `src/app.py` to accept parallel logical optional fields `start_season: str` and `end_season: str`.

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Restrict Data by Chronological Range (Priority: P1) 🎯 MVP

**Goal**: Filter the transfer dataset to a specific range of seasons before algorithm execution.

**Independent Test**: Manually select a start/end season in the UI, hit "Run Algorithm", and verify the resulting graph operates on a constrained history without crashing.

### Implementation for User Story 1

- [X] T004 [US1] Add DOM structure for the `start-season` and `end-season` dropdowns within the form in `src/templates/index.html`. Populate chronological `<option>` tags from "2000-2001" to "2018-2019", prefixing both with an explicit `<option value="all">All Seasons</option>`.
- [X] T005 [US1] Update data-fetching orchestration in `src/static/js/graph.js` (`triggerAnalysis`) to extract values from the season selectors and attach them to the `/api/pagerank` JSON `POST` payload.
- [X] T006 [US1] Update `src/app.py` endpoint routes to collect `start_season` and `end_season` inputs and pass them downstream as explicit arguments into the `TransferAnalyzer` constructor.
- [X] T007 [US1] Implement DataFrame `.filter()` or `.where()` subsetting in `src/core/processing.py` to isolate rows strictly inside the chronological bounds. Bypass the `.filter()` if season inputs are omitted or marked "all".

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently via the Run button.

---

## Phase 4: User Story 2 - Seamless UI Integration & Auto-trigger (Priority: P2)

**Goal**: The filter dynamically auto-recalculates when changed and prevents the user from selecting impossible date ranges.

**Independent Test**: Change the start season drop-down. Verify that 1) invalid end-season options before the start limit are instantly disabled/grayed out, and 2) the recalculation visually starts without pressing "Run".

### Implementation for User Story 2

- [X] T008 [US2] In `src/static/js/graph.js`, add `change` event listeners to both the `start-season` and `end-season` DOM elements to explicitly trigger `debounceAnalysis()`.
- [X] T009 [US2] Implement a helper function `validateSeasonRange()` in `src/static/js/graph.js` that triggers on selection change. The logic must iterate over the `<option>` lists and dynamically inject the HTML `disabled` attribute to targets that violate the chronological hierarchy (e.g. End dates preceding the chosen Start date).

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. The UI is protected from bad bounds.

---

## Phase 5: User Story 3 - Visualizing Metadata Context (Priority: P3)

**Goal**: The backend explicitly reports the active bounds out to the frontend, rendering a concise descriptive badge.

**Independent Test**: Apply a filtered date constraint and verify that a UI string explicitly states "Season: [Start] to [End]" prominently around the visualization layer.

### Implementation for User Story 3

- [X] T010 [US3] Modify `src/core/processing.py` algorithm outputs to encode the effectively applied time constraint inside the standard `meta` dictionary block alongside the results. (e.g., `meta['season_range'] = "2010-2011 to 2012-2013"`).
- [X] T011 [US3] In `src/static/js/graph.js`, expand the UI processing blocks inside the exact success callback of `triggerAnalysis()` to extract `lastResult.meta.season_range`.
- [X] T012 [US3] Establish a persistent container inside `src/templates/index.html` (e.g., `<div id="season-range-meta"></div>` above the `#chart-container`) to render this timestamp explicitly. Add related CSS to `src/static/css/style.css`.

**Checkpoint**: All user stories should now be independently functional. Subsets are explicitly stated and protected.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T013 Verify that the PySpark DataFrame `.filter()` appropriately propagates total zero-row collections seamlessly into the existing empty-state indicator.
- [X] T014 Ensure the 'disabled' tag visual coloring inside the HTML select menus properly adopts the site's dark mode visual contrast. Apply quick fixes in `src/static/css/style.css`.
- [X] T015 Verify the newly introduced `season_range` label plays correctly with the Compare mode UI grid without obstructing the dual-bar charts.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 completion.
- **User Stories (Phase 3-5)**: Must trigger chronologically due to strict API dependency (US1 → US2 → US3).
- **Polish (Final Phase)**: Final assurance testing.

### Parallel Opportunities

- Client-side DOM setup (T004) can parallelize alongside Backend validation logic upgrades (T006).

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Introduce backend `filter()` logic and test it manually via CURL.
2. Hook up HTML dropdowns.
3. Validate deterministic PySpark operation on constrained histories.

### Incremental Delivery

1. Integrate filter bounds into DataFrame map steps (US1 MVP).
2. Wire up protective DOM scripting to lock impossible combinations (US2 frontend).
3. Push bounds explicitly back up to presentation layer (US3 Metadata context).
