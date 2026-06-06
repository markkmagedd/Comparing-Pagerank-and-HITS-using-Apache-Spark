---
description: "Task list for Transfer Details Pop-up feature implementation"
---

# Tasks: Transfer Details Pop-up

**Input**: Design documents from `/specs/006-transfer-details-popup/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/api.md

**Tests**: Tests are excluded as they were not explicitly requested. Focus is on direct implementation via PySpark and FastAPI.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify Spark environment and FastAPI routing initialization inside `src/app.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Add hidden pop-up container and styling properties to `src/static/css/style.css`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Club Transfer Details in Network Graph (Priority: P1) 🎯 MVP

**Goal**: As a user exploring the network graph visualization for any algorithm, I want to click on a club node so that I can see the specific transfer details for that club in a pop-up without losing my context in the main visualization.

**Independent Test**: Can be tested by loading any algorithm's network graph, clicking a node, and verifying a pop-up appears in the corner with the club's transfer data via PySpark processing.

### Implementation for User Story 1

- [x] T003 [P] [US1] Implement `get_top_transfers` method leveraging PySpark MapReduce filtering inside `src/core/processing.py`
- [x] T004 [US1] Implement `GET /api/transfers/{club_name}` endpoint in `src/app.py` (depends on T003)
- [x] T005 [P] [US1] Create the HTML pop-up skeletal structure with loading state inside `src/templates/index.html`
- [x] T006 [US1] Add Network Graph (Cytoscape) node click event listeners and fetch logic in `src/static/js/graph.js`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Club Transfer Details in Bar Graph (Priority: P2)

**Goal**: As a user viewing the bar graph visualization for any algorithm, I want to click on a bar so that I can see the specific transfer details for that club in a corner pop-up.

**Independent Test**: Can be tested by loading any algorithm's bar graph, clicking a bar, and verifying the same pop-up behavior as the network graph.

### Implementation for User Story 2

- [x] T007 [US2] Add Bar Graph (Chart.js) element click event listeners and shared fetch wiring in `src/static/js/graph.js`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T008 [P] Code cleanup and refactoring across `app.py` and `graph.js`
- [x] T009 Refine UI layout and add micro-animations to CSS popup window in `src/static/css/style.css`

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends strictly on the backend API created in US1 but should be independently testable via the Bar Chart UI

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- Foundational tasks can be run asynchronously to existing setup
- T003 (Backend `processing.py`) and T005 (Frontend HTML) can be run strictly in parallel by distinct team members.

---

## Parallel Example: User Story 1

```bash
# Launch generic PySpark method and HTML DOM modifications simultaneously safely targeting different domains:
Task: "Implement `get_top_transfers` method leveraging PySpark MapReduce filtering inside src/core/processing.py"
Task: "Create the HTML pop-up skeletal structure with loading state inside src/templates/index.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently via Network Nodes.
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Network Graph) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Bar Graph) → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories
