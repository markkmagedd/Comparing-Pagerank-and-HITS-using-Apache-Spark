---
description: "Task list for Side-by-Side Algorithm Comparison Mode implementation"
---

# Tasks: Side-by-Side Algorithm Comparison Mode

**Input**: Design documents from `/specs/004-compare-mode/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [X] T001 [P] Review `src/templates/index.html` to understand the current visualization toggle structure and target div for the new chart container.
- [X] T002 [P] Review `src/static/js/graph.js` to identify the `triggerAnalysis` fetch wrapper and `renderBarChart` dependencies.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

- [X] T003 Update `renderBarChart` function signature in `src/static/js/graph.js` to accept `canvasCtx` (or `canvasId`) as a parameter to support rendering to arbitrary targets, rather than relying on a hardcoded canvas ID. Keep backward compatibility with existing usages.

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - View Algorithms Side-by-Side (Priority: P1) 🎯 MVP

**Goal**: Display PageRank and HITS results simultaneously so users can visually compare which clubs each algorithm ranks highest.

**Independent Test**: Open the application, activate Compare mode, and verify that two panels appear — left showing PageRank results and right showing HITS results — both using the current filters. Deactivate Compare mode to return to single-algorithm view.

### Implementation for User Story 1

- [X] T004 [US1] Add "Compare" button to the visualization toggle row in `src/templates/index.html` alongside "Bar Chart" and "Network Graph". 
- [X] T005 [US1] Add DOM structure for the second visualization panel in `src/templates/index.html` (e.g., `<div id="chart-container-right" class="hidden">` with its own `<canvas id="rankChartRight">`), and heading labels for "PageRank" and "HITS".
- [X] T006 [P] [US1] Add CSS layout rules in `src/static/css/style.css` to handle side-by-side flexbox rendering when a `.compare-mode-active` class is applied to the main visualization area.
- [X] T007 [US1] Implement Compare mode toggle state logic in `src/static/js/graph.js`. Clicking the "Compare" button sets `isCompareModeActive = true`, applies the `.compare-mode-active` class to the layout, hides the network graph canvas, and disables the algorithm dropdown. Re-clicking disables Compare mode and reverts the UI.
- [X] T008 [US1] Modify `triggerAnalysis()` in `src/static/js/graph.js` to branch logic based on `isCompareModeActive`. When true, dispatch two concurrent API requests using `Promise.all` (one with `algorithm: 'pagerank'` and one with `algorithm: 'hits'`), wait for both, then call `renderBarChart` twice on the respective left and right canvases.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Simultaneous Filter Updates (Priority: P2)

**Goal**: Both comparison panels update simultaneously when changing any filter (league, weight mode, direction, iterations, Top N).

**Independent Test**: Activate Compare mode, change the league filter to "Premier League", and verify both panels reload with Premier League data and the loader covers both panels during recomputation.

### Implementation for User Story 2

- [X] T009 [US2] Ensure all existing filter `change` event listeners in `src/static/js/graph.js` (league, weight mode, direction, iterations) seamlessly trigger the dual-dispatch `debounceAnalysis()` logic when `isCompareModeActive` is true. No extra wiring should be strictly necessary if T008 is robust, but review and adjust damping factor behavior (must remain editable and applies to PageRank).
- [X] T010 [US2] Update loading global overlay in `src/static/js/graph.js` and `src/static/css/style.css` to ensure the `#viz-loading` spinner cleanly blankets the entire two-panel visualization row rather than just the left canvas while the `Promise.all` is awaiting.
- [X] T011 [US2] Verify that error handling gracefully displays "Error running algorithms" and restores UI interaction if either of the `Promise.all` calls fail.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Overlap Highlighting and Summary (Priority: P3)

**Goal**: See which clubs appear in both algorithm rankings and which are unique to each, to quantify algorithm agreement.

**Independent Test**: Activate Compare mode, run a comparison, and verify clubs present in both algorithm top-Ns are visually distinct (e.g., gold borders). Verify the summary line states the overlap count between the panels.

### Implementation for User Story 3

- [X] T012 [P] [US3] Add a placeholder `<div id="overlap-summary" class="hidden"></div>` in `src/templates/index.html`, positioned centrally between or above the two compare panels. Add basic centered typography styles in `src/static/css/style.css`.
- [X] T013 [US3] Implement `calculateOverlap(prData, hitsData)` helper function in `src/static/js/graph.js` that extracts the node IDs from each result, computes the intersection `Set`, and returns `{ overlapSet, overlapCount, totalN }`.
- [X] T014 [US3] Modify the bar chart rendering loop inside `renderBarChart` in `src/static/js/graph.js` to optionally accept `overlapSet`. For each node/label being processed, if the node ID exists in `overlapSet`, assign a distinct `backgroundColor` (e.g., gold/yellow) and `borderColor` instead of the default blue.
- [X] T015 [US3] Update the Compare mode success callback in `triggerAnalysis()` within `src/static/js/graph.js` to call `calculateOverlap()`, display the resulting string "X of N clubs appear in both rankings" in the `#overlap-summary` div, and pass the `overlapSet` to both `renderBarChart` calls. Handle cases where API returns 0 nodes correctly by showing "0 of 0".

**Checkpoint**: All user stories should now be independently functional. Compare mode should highlight overlaps and display dynamic counts automatically upon running.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T016 Verify empty-state handling natively hides Chart targets and the `#overlap-summary` container in Compare mode, restoring the `#empty-state` placeholder correctly.
- [X] T017 Remove any debug console logs in `src/static/js/graph.js` related to `Promise.all` execution and ensure variable cleanup.
- [X] T018 Code cleanup and verify that `renderNetwork()` disables or gracefully hides itself without throwing errors when switching into compares.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories should proceed sequentially in priority order (US1 → US2 → US3) due to progressive DOM structure additions.
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Configures the fundamental dispatch modifications.
- **User Story 2 (P2)**: Integrates seamlessly on top of Phase 1 to fix loading overlays and input bindings during dual-fetches.
- **User Story 3 (P3)**: Depends on User Story 1 (requires `Promise.all` results) to compute intersection logic before rendering.

### Parallel Opportunities

- Setup tasks [P] can run in parallel
- T006 and T012 CSS/HTML scaffolding can run in parallel with core JS logic in T007.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Modify the `triggerAnalysis` in JavaScript to do concurrent fetches.
2. Render dual DOM canvases.
3. Test dual side-by-side PageRank / HITS displays.

### Incremental Delivery

1. Integrate Compare toggle & Basic Dual Canvas rendering (MVP).
2. Wire global loading indicators appropriately.
3. Add intersection computation (`calculateOverlap`) and inject conditional Gold rendering options into Chart.js to clearly highlight overlapping nodes.
