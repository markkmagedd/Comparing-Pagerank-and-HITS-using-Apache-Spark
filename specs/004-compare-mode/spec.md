# Feature Specification: Side-by-Side Algorithm Comparison Mode

**Feature Branch**: `004-compare-mode`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "Add a Compare mode to the web interface. When activated, the visualization area splits into two panels showing PageRank results on the left and HITS results on the right, both computed from the same filters. Both panels update simultaneously when any control changes. Each panel shows its own bar chart or network graph. Nodes that appear in both algorithm's top-N results should be visually highlighted. A summary line between the panels shows overlap count. The user can exit compare mode to return to the single-algorithm view."

## Clarifications

### Session 2026-03-31

- Q: Where should the Compare mode toggle be placed in the UI? → A: As a third button in the existing visualization toggle row (Bar Chart / Network Graph / Compare).
- Q: Should Compare mode respect the current viz toggle or always use bar charts? → A: Always use bar charts in Compare mode (most readable for side-by-side ranking comparison).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Algorithms Side-by-Side (Priority: P1)

As a researcher studying transfer network dynamics, I want to see PageRank and HITS results displayed simultaneously so that I can visually compare which clubs each algorithm ranks highest and understand how the algorithms diverge on the same dataset.

**Why this priority**: This is the core value proposition of the feature — the ability to compare two algorithm outputs in a single view is the primary thesis comparison tool.

**Independent Test**: Open the application, activate Compare mode, and verify that two panels appear — left showing PageRank results and right showing HITS results — both using the current filters. The user can interpret differences at a glance.

**Acceptance Scenarios**:

1. **Given** the user is on the default single-algorithm view, **When** they activate Compare mode, **Then** the visualization area splits into two side-by-side panels: the left panel shows PageRank results and the right panel shows HITS results.
2. **Given** Compare mode is active, **When** both panels have loaded, **Then** each panel displays a heading indicating the algorithm name ("PageRank" / "HITS") and the appropriate score type label (e.g., "PageRank Score", "Authority Score").
3. **Given** Compare mode is active, **When** the user deactivates Compare mode, **Then** the view returns to the single-algorithm layout, showing whichever algorithm is currently selected in the algorithm dropdown.

---

### User Story 2 - Simultaneous Filter Updates (Priority: P2)

As a researcher, I want both comparison panels to update simultaneously when I change any filter (league, weight mode, direction, iterations, Top N) so that I'm always comparing apples-to-apples on the same data slice.

**Why this priority**: Without synchronized updates, the comparison would be meaningless — both panels must always reflect the same data parameters.

**Independent Test**: Activate Compare mode, change the league filter to "Premier League", and verify both panels reload with Premier League data. Change weight mode to "Transfer Count" and verify both panels update again.

**Acceptance Scenarios**:

1. **Given** Compare mode is active and both panels are showing results, **When** the user changes the league filter, **Then** both panels recompute and display updated results for the new league.
2. **Given** Compare mode is active, **When** the user changes the weight mode, direction, iterations, or Top N, **Then** both panels recompute simultaneously and reflect the new settings.
3. **Given** Compare mode is active, **When** the user clicks "Run Algorithm" or triggers an auto-run change, **Then** a loading indicator appears on both panels and they update together.

---

### User Story 3 - Overlap Highlighting and Summary (Priority: P3)

As a researcher, I want to see which clubs appear in both algorithm rankings and which are unique to each, so I can quantify how much the algorithms agree or disagree.

**Why this priority**: This adds analytical depth on top of the basic side-by-side view — it transforms visual comparison into a measurable insight.

**Independent Test**: Activate Compare mode, run a comparison, and verify that clubs present in both the PageRank top-N and HITS top-N are visually distinct (highlighted). Verify that a summary line between the panels states the overlap count (e.g., "7 of 10 clubs appear in both rankings").

**Acceptance Scenarios**:

1. **Given** Compare mode is active and both panels have results, **When** results are rendered, **Then** nodes/bars representing clubs that appear in both algorithm's top-N are visually highlighted (e.g., with a gold accent, border, or badge).
2. **Given** Compare mode is active and both panels have results, **When** results are rendered, **Then** a summary line displayed between the two panels shows the overlap count in the format "X of N clubs appear in both rankings".
3. **Given** Compare mode is active, **When** the Top N value changes and the overlap shifts, **Then** the highlights and summary line update to reflect the new overlap.

---

### Edge Cases

- What happens when one algorithm returns fewer nodes than top-N (e.g., a small league with only 4 clubs)? Both panels should display whatever nodes are available, and the overlap summary should use the actual count rather than the requested top-N.
- What happens when the selected filters produce no data (empty state)? Both panels should show the existing empty-state message. The overlap summary should show "0 of 0 clubs appear in both rankings".
- What happens when Compare mode is activated before any analysis has been run? The system should automatically trigger a dual-algorithm computation.
- How does Compare mode interact with the algorithm selector dropdown? The algorithm dropdown should be disabled (greyed out) while Compare mode is active, since both algorithms are shown simultaneously.
- How does Compare mode interact with the damping factor control? The damping factor should remain editable in Compare mode because it affects the PageRank panel's results.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a "Compare" button as the third option in the existing visualization toggle row (alongside "Bar Chart" and "Network Graph"), clearly indicating the current mode state.
- **FR-002**: When Compare mode is active, the visualization area MUST split into two side-by-side panels of equal width.
- **FR-003**: The left panel MUST always display PageRank results and the right panel MUST always display HITS results.
- **FR-004**: Each panel MUST display a clear heading identifying which algorithm it shows.
- **FR-005**: Compare mode MUST always render both panels as bar charts, regardless of the previously selected visualization type. The viz toggle row highlights "Compare" as the active option, replacing the Bar Chart / Network Graph selection.
- **FR-006**: When any filter changes in Compare mode, the system MUST compute both algorithms and update both panels simultaneously.
- **FR-007**: The system MUST display a loading indicator across both panels during computation.
- **FR-008**: Clubs appearing in both algorithm's top-N results MUST be visually highlighted in both panels with a distinct visual treatment.
- **FR-009**: The system MUST display an overlap summary between the two panels in the format "X of N clubs appear in both rankings".
- **FR-010**: When Compare mode is exited, the system MUST return to the single-algorithm view showing the previously selected algorithm.
- **FR-011**: The algorithm selector dropdown MUST be disabled while Compare mode is active.
- **FR-012**: The damping factor control MUST remain editable in Compare mode (it only affects the PageRank panel).
- **FR-013**: HITS-specific score type labels MUST show correctly in the right panel (e.g., "Authority Score" for buyers direction, "Hub Score" for sellers direction).
- **FR-014**: When Compare mode is activated before any analysis has been run, the system MUST automatically trigger a dual computation.
- **FR-015**: When both panels encounter an empty data state, both panels MUST show the empty state indicator and the overlap summary MUST show "0 of 0".

### Key Entities

- **Comparison Result**: A paired set of algorithm outputs (PageRank result + HITS result) computed from the same filters, including overlap metadata.
- **Overlap Set**: The set of club identifiers that appear in both algorithm's top-N results, used to drive highlighting and the summary count.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can activate and deactivate Compare mode in a single click, with the layout transition completing within 1 second.
- **SC-002**: Both comparison panels update within the same computation cycle — the user never sees one panel with stale data while the other has new data.
- **SC-003**: The overlap summary accurately reflects the intersection of the two result sets for all filter combinations.
- **SC-004**: Users can identify overlapping clubs in under 3 seconds thanks to clear visual highlighting.
- **SC-005**: All existing single-algorithm functionality continues to work identically when Compare mode is not active.

## Assumptions

- Compare mode requires two API calls (one per algorithm) or a single new endpoint that returns both. The implementation detail is left to the planning phase.
- The compare toggle is placed in the sidebar near the existing visualization toggle, as it controls how results are displayed.
- The overlap highlighting style (gold border, badge, etc.) will be determined during implementation to fit the existing design language.
- Mobile/responsive layout is not a concern — the existing application targets desktop usage.
- Compare mode state is not persisted; returning to the page resets to single-algorithm view (consistent with existing behavior for the algorithm selector).
