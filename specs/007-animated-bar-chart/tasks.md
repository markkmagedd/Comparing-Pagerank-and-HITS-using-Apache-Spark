# Tasks: Animated Bar Chart

**Input**: Design documents from `/specs/007-animated-bar-chart/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are omitted as they were not requested in the specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create missing UI static and template files: `src/static/js/historical_bar_chart.js` and `src/templates/analysis.html`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Implement routing for the new `analysis.html` template in the FastAPI application setup (e.g., in `src/app.py` or main entry point)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Historical Animation (Priority: P1) 🎯 MVP

**Goal**: Watch an animated bar chart that progresses year-by-year, showing the top 10 clubs ascending and descending in ranks, with loading indication and interactive details popup on click.

**Independent Test**: Can be fully tested by pressing "Start" on the new analysis screen, seeing the loading spinner, then confirming the chart visually transitions through each year sequentially while updating ranks and allows opening details upon clicking a bar.

### Implementation for User Story 1

- [X] T003 [P] [US1] Implement PySpark temporal iterators for year-by-year sequence processing in `src/core/processing.py`
- [X] T004 [US1] Create FastAPI endpoint `GET /api/rankings/historical` returning `YearlyRankings` JSON in the api routing layer (e.g., `src/app.py` based on existing structure) - depends on T003
- [X] T005 [P] [US1] Build the HTML layout with "Start" button, active year display, and loading spinner in `src/templates/analysis.html`
- [X] T006 [US1] Implement D3.js chart initialization and base SVG setup in `src/static/js/historical_bar_chart.js`
- [X] T007 [US1] Implement API fetch logic, spinner handling, and year-by-year sequential D3 `transition()` execution in `src/static/js/historical_bar_chart.js`
- [X] T008 [US1] Integrate clickable bar functionality to trigger the Transfer Details popup across all rendered bars in `src/static/js/historical_bar_chart.js`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Animation Controls (Priority: P2)

**Goal**: Be able to pause/resume playback and adjust the animation speed (e.g., 0.5x, 1x, 2x) to closely inspect historical epochs.

**Independent Test**: Can be independently tested by starting the continuous animation, pressing pause/resume to verify chart holding state, and toggling speed setting observed through transition completion times.

### Implementation for User Story 2

- [X] T009 [P] [US2] Enhance UI layout to include Play/Pause toggle and Speed selection dropdown in `src/templates/analysis.html`
- [X] T010 [US2] Implement state management properties to track active play/pause state and current speed setting in `src/static/js/historical_bar_chart.js`
- [X] T011 [US2] Wire Play/Pause button to `d3.interrupt()` or coordinate resuming from current year state in `src/static/js/historical_bar_chart.js`
- [X] T012 [US2] Link speed toggle UI inputs to dynamically scale the D3 `.duration()` scaling in `src/static/js/historical_bar_chart.js`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T013 [P] Apply custom styling and bar chart CSS refinements in `src/static/css/style.css`
- [X] T014 Run validation referencing `quickstart.md` to ensure all functionality runs exactly as prescribed.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed sequentially in priority order (P1 → P2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after User Story 1 (Phase 3) - Integrates into US1 UI and core script

### Within Each User Story

- Core PySpark calculations before API endpoints
- REST logic before frontend data binding
- UI controls built before JS event listener binding

### Parallel Opportunities

- Foundational endpoint scaffolding (US1: T003/T004) can be worked on concurrently with generic HTML/CSS layout (US1: T005).

---

## Parallel Example: User Story 1

```bash
# Launch backend algorithm and endpoint alongside frontend markup initialization
Task: "Implement PySpark temporal iterators for year-by-year sequence processing in src/core/processing.py"
Task: "Build the HTML layout with "Start" button, active year display, and loading spinner in src/templates/analysis.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done: Developer A begins Spark backend (T003), Developer B begins D3 frontend setup (T005/T006).

---

## Notes

- [P] tasks = different files, no dependencies
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
