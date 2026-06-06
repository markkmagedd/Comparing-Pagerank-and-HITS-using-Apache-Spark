# Feature Specification: Transfer Details Pop-up

**Feature Branch**: `006-transfer-details-popup`  
**Created**: 2026-04-06  
**Status**: Draft  
**Input**: User description: "I want to add a feature where in the bar graph or the network in any algorithm when a bar or node is selected the details of the transfers of the club shows in a small pop up in the corner of the screen"

## Clarifications

### Session 2026-04-06
- Q: A club might have hundreds of transfers. How should we constrain the data displayed in the pop-up to maintain usability? → A: Limit to top N most expensive transfers (e.g., Top 10)
- Q: How will the transfer details data be retrieved when a club node/bar is selected? → A: Fetched dynamically via a new backend API endpoint on selection
- Q: What exact fields must be displayed for each individual transfer in the pop-up? → A: Player Name, Transfer Fee, and Associated Club (Bought From / Sold To)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Club Transfer Details in Network Graph (Priority: P1)

As a user exploring the network graph visualization for any algorithm, I want to click on a club node so that I can see the specific transfer details for that club in a pop-up without losing my context in the main visualization.

**Why this priority**: Displaying detailed data for nodes directly impacts the analytical value of the network graphs, making it the most critical part of the feature.

**Independent Test**: Can be tested by loading any algorithm's network graph, clicking a node, and verifying a pop-up appears in the corner with the club's transfer data.

**Acceptance Scenarios**:

1. **Given** the user is viewing a network graph for an algorithm, **When** they select a club node, **Then** a small pop-up appears in the corner of the screen containing the transfer details for that club.
2. **Given** the pop-up is visible, **When** the user clicks on a different club node, **Then** the pop-up updates to show the transfer details of the newly selected club.
3. **Given** the pop-up is visible, **When** the user clicks outside of any node or on a close button, **Then** the pop-up disappears.

---

### User Story 2 - View Club Transfer Details in Bar Graph (Priority: P2)

As a user viewing the bar graph visualization for any algorithm, I want to click on a bar so that I can see the specific transfer details for that club in a corner pop-up.

**Why this priority**: Similar value to the network graph, but often bar graphs already convey rankings clearly. Adding drill-down details provides deep dive capabilities. It's a parallel implementation to the network graph pop-up.

**Independent Test**: Can be tested by loading any algorithm's bar graph, clicking a bar, and verifying the same pop-up behavior as the network graph.

**Acceptance Scenarios**:

1. **Given** the user is viewing a bar graph for an algorithm, **When** they select a bar representing a club, **Then** the transfer details pop-up appears in the corner.
2. **Given** the pop-up is visible from selecting a bar, **When** the user clicks another bar, **Then** the pop-up updates with the new club's details.

### Edge Cases

- What happens when a selected club has zero transfers recorded?
- How does the system handle very long lists of transfers that might exceed the pop-up's natural height?
- What happens if the user reshapes/resizes their screen—does the pop-up remain visible in the corner?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a pop-up container anchored to a corner of the screen when a valid visual element (node or bar) is selected.
- **FR-002**: System MUST render the specific transfer details (limited to the top N most expensive transfers, e.g., Top 10) for the currently selected club within the pop-up, including players bought/sold, transfer fees, and relevant clubs.
- **FR-003**: System MUST update the contents of an already open pop-up when a new valid visual element is selected.
- **FR-004**: System MUST allow the user to dismiss the pop-up (e.g., via clicking outside, or a dedicated close button).
- **FR-005**: System MUST handle cases where a club has no transfers by displaying an empty state message within the pop-up.
- **FR-006**: System MUST ensure the pop-up content is scrollable if the transfer details exceed the maximum height of the pop-up.
- **FR-007**: System MUST support this interaction across all implemented algorithm visualizations (e.g., PageRank, HITS, etc.) that utilize network or bar graphs.
- **FR-008**: System MUST display a loading state (e.g., skeleton loader or spinner) while fetching data from the backend API.

### Integration & Dependencies

- **Backend API**: The pop-up requires a new backend endpoint to dynamically fetch the required transfer details (limited to top N) for the selected club upon interaction, rather than embedding all data in the initial graph payload.

### Key Entities *(include if feature involves data)*

- **Club Node/Bar**: Represents a football club in the visualization. Requires an identifier to fetch corresponding transfer data.
- **Transfer Details**: The overarching data payload containing all inbound and outbound transfers associated with a specific club. For each transfer, it strictly includes: Player Name, Transfer Fee, and Associated Club (Bought From or Sold To).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view the transfer details of any club within 1 click from either the network or bar graph visualizations.
- **SC-002**: The pop-up consistently appears within 500ms of selecting a valid node or bar.
- **SC-003**: The pop-up correctly updates its data 100% of the time when a new club is selected without requiring a page refresh.
- **SC-004**: Users on standard resolution screens can see the relevant transfer detail text clearly formatted without the pop-up obscuring the visual representation of the selected element itself.
