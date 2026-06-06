# Feature Specification: Season Range Filter

**Feature Branch**: `005-season-filter`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "Add a season range filter to the web interface. The user can select a start season and end season (data spans 2000-2001 through 2018-2019) to restrict the transfer network to only transfers that occurred within that range. The backend should filter transfers by the Season column before building the edge RDD. The filter should work with all existing controls (league, weight mode, algorithm, direction). Include an "All Seasons" default option. When a season range is active, display it in the results metadata. The season filter should auto-trigger analysis recomputation like the league and weight mode filters do. Seasons should be listed chronologically in the dropdowns."

## Clarifications
### Session 2026-03-31
- Q: What should be the specific UX behavior when a user selects an End Season that is chronologically before the Start Season? → A: Option B (Dynamic Disable: Prevent invalid selections entirely by disabling/graying out options in the End dropdown that precede the selected Start dropdown).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Restrict Data by Chronological Range (Priority: P1)

As a network researcher, I want to filter the transfer dataset to a specific range of seasons (e.g., from 2005-2006 to 2010-2011) so that I can observe network topologies and algorithm rankings during specific historical eras rather than across the entire 20-year span.

**Why this priority**: Core value of the feature is restricting the dataset to a target time continuum.

**Independent Test**: Load the application, change the season range to "2010-2011" through "2012-2013", and verify that the resulting calculation uses only data from those seasons before applying PageRank or HITS.

**Acceptance Scenarios**:

1. **Given** the user is viewing the visualization, **When** they select a start season and an end season and run the algorithm, **Then** the network graph and bar charts display only nodes/edges built from transfers in that range.
2. **Given** the user is selecting a season range, **When** they look at the dropdowns, **Then** the options span from '2000-2001' to '2018-2019' sorted chronologically.

---

### User Story 2 - Seamless UI Integration & Auto-trigger (Priority: P2)

As a user exploring data, I want the season filter to automatically update the visualization when changed, and smoothly integrate with existing controls like League and Weight Mode.

**Why this priority**: Maintains the immediate, responsive UX pattern established in Data-Driven Customization.

**Independent Test**: Change the Start Season dropdown and observe that the loader appears and the visualization automatically recomputes without needing to press the "Run Algorithm" button manually.

**Acceptance Scenarios**:

1. **Given** the visualization is rendered, **When** the user changes either the start or end season, **Then** an analysis computation is automatically triggered.
2. **Given** the user sets a season range, **When** they also change the League or Weight Mode, **Then** the simultaneous combination of all active filters correctly isolates the data slice.

---

### User Story 3 - Visualizing Metadata Context (Priority: P3)

As a researcher exporting results, I need the active season range visually displayed on the results so that I always know what time period I am looking at.

**Why this priority**: Essential for reporting and tracking context, especially in Compare Mode or static screenshots.

**Independent Test**: Run a filtered query and verify that a UI label or graphical overlay explicitly states the utilized season boundaries (e.g., "Season: 2010-2011 to 2015-2016").

**Acceptance Scenarios**:

1. **Given** the results are rendered, **When** the default "All Seasons" option is active, **Then** the metadata implicitly reads "All Seasons" (or full range).
2. **Given** the results are rendered, **When** a restricted range is active, **Then** the metadata explicitly states the subset range.

---

### Edge Cases

- What happens if a very restrictive season + league combination yields no transfers? The system should natively reuse the existing empty-state indicator.
- How does the "All Seasons" option function in the UI? It will be implemented as an "All Seasons" option at the very top of both the Start Season and End Season dropdowns. Selecting "All Seasons" in either dropdown implicitly resets the filter to show the entire dataset.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide UI elements allowing users to select a starting season and an ending season.
- **FR-002**: The season options MUST span from "2000-2001" to "2018-2019" and MUST be listed chronologically.
- **FR-003**: System MUST provide an "All Seasons" selection option, acting as the default state upon initial load or control reset.
- **FR-004**: System MUST filter the dataset sequentially before graph algorithm calculation, exclusively allowing transfers within the inclusive season boundaries.
- **FR-005**: Changing the selected season(s) MUST automatically trigger calculation re-runs, adhering to the application's existing debounce behavior.
- **FR-006**: The backend MUST correctly orchestrate the combination of season boundaries, league filters, and algorithm selections robustly.
- **FR-007**: System MUST validate frontend input by dynamically disabling (graying out) invalid target options in the 'End Season' dropdown that occur chronologically before the selected 'Start Season' (and vice-versa for the Start dropdown relative to the End limit).
- **FR-008**: The currently active time boundary MUST be represented in the metadata payload and displayed cleanly in the UI accompanying the visualization.

### Key Entities

- **Time Series Filter Object**: Defines the chronological boundary (inclusive start string, inclusive end string, or "ALL").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can construct and run a subset historical time analysis with zero programmatic errors.
- **SC-002**: Auto-recomputation responds dynamically within standard debounced latencies upon any season drop-down adjustments.
- **SC-003**: The combined filter query returns correct datasets verified against raw CSV ranges.

## Assumptions

- The backend parsing logic will extract the 'Season' directly from the `transfers.csv` format "2000-2001". No complex date parsing is necessary beyond simple array indexing of the known season strings.
- "All Seasons" assumes looking at the complete historical continuum.
- If Start/End seasons are identical, it is treated as a single-season filter.
