# Feature Specification: HITS Algorithm Integration

**Feature Branch**: `003-hits-algorithm`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "implement the HITS algorithm for the same data model and add in the web interface the ability for the user to choose whether to show the HITS results or the PageRank results"

## Clarifications

### Session 2026-03-31
- Q: Should the algorithm selector (PageRank ↔ HITS) trigger an automatic rerun when changed, or require the user to click "Run"? → A: Auto-run on change (same debounce as league/weight controls).
- Q: What should the UI do with the "Damping Factor" control when HITS is selected (since HITS doesn't use damping)? → A: Disable (grey out) the control with a tooltip explaining it's not applicable to HITS.
- Q: Should the direction selector labels update to reflect HITS terminology (Authority/Hub) when HITS is selected, or stay as "Attractors (Buyers)" / "Suppliers (Sellers)"? → A: Dynamically update labels to "Authority (Buyers)" / "Hub (Sellers)" when HITS is active.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run HITS Algorithm and View Results (Priority: P1)

A researcher wants to analyze the football transfer network using the HITS (Hyperlink-Induced Topic Search) algorithm. They access the web interface and select "HITS" as the algorithm type. The system computes Hub and Authority scores for clubs based on transfer data. Clubs that attract many transfers from important sellers receive high Authority scores (strong attractors), while clubs that sell to many influential buyers receive high Hub scores (strong suppliers). The researcher views these scores in the existing visualization (bar chart or network graph) to understand club influence from a link-analysis perspective complementary to PageRank.

**Why this priority**: Running the HITS algorithm is the foundational capability without which no comparison to PageRank is possible. This story delivers the core computational and display functionality.

**Independent Test**: Select "HITS" as the algorithm, choose "Authority" ranking, hit Run, and verify that ranked club data appears in the visualization with Authority scores — confirming the algorithm ran successfully on the transfer dataset.

**Acceptance Scenarios**:

1. **Given** the web interface is loaded, **When** the user selects "HITS" as the algorithm and clicks "Run", **Then** the system computes HITS Hub and Authority scores and displays them in the currently active visualization type (bar chart or network graph).
2. **Given** HITS is selected, **When** the user chooses "Authority" as the ranking type, **Then** the visualization shows clubs ranked by their Authority score, with the highest-authority club at the top.
3. **Given** HITS is selected, **When** the user chooses "Hub" as the ranking type, **Then** the visualization shows clubs ranked by their Hub score, with the highest-hub club at the top.
4. **Given** a HITS computation completes, **When** the result is displayed, **Then** each node/bar shows the relevant HITS score (Hub or Authority) in the same format used for PageRank scores.

---

### User Story 2 - Switch Between PageRank and HITS (Priority: P2)

A researcher wants to compare how clubs rank under two different link-analysis algorithms: PageRank and HITS. They use an algorithm selector control on the web interface to toggle between "PageRank" and "HITS". Switching the selection and running the analysis displays the results of the chosen algorithm, allowing side-by-side conceptual comparison across runs.

**Why this priority**: Enabling the user to choose between algorithms is the second core value proposition — it lets the researcher answer whether PageRank and HITS agree or diverge on club influence. This depends on HITS being functional (P1).

**Independent Test**: Run PageRank and note the top-5 ranked clubs. Switch to HITS (Authority), run again, and confirm the ranking may differ — validating that a distinct algorithm is being executed, not just relabelled PageRank results.

**Acceptance Scenarios**:

1. **Given** the visualization shows PageRank results, **When** the user switches the algorithm selector to "HITS", **Then** the system automatically reruns the analysis after a short debounce delay and the visualization updates with HITS-based rankings.
2. **Given** HITS results are displayed, **When** the user switches back to "PageRank", **Then** the system automatically reruns the analysis and the visualization updates with PageRank-based rankings.
3. **Given** the algorithm selector is set to a value, **When** the user changes any other control (league filter, weight mode, direction), **Then** the selected algorithm is preserved and applied in the next computation.
4. **Given** the page loads for the first time, **Then** the algorithm selector defaults to "PageRank" to preserve backward compatibility with the existing experience.

---

### User Story 3 - HITS Works with Existing Filters (Priority: P3)

A researcher wants to analyze HITS rankings for a specific league and weight mode combination. The HITS algorithm respects the same controls already available for PageRank — league filter, weight mode (Transfer Fee vs Transfer Count), direction (Buyers / Sellers), iterations, and Top N — ensuring feature parity and composability.

**Why this priority**: This story validates that HITS integrates seamlessly with all existing UI controls and data pipeline filters. It is P3 because it tests integration completeness rather than adding new standalone value.

**Independent Test**: Set league to "Premier League", weight mode to "Transfer Count", algorithm to "HITS", direction to "Authority", and run. Verify that only Premier League clubs appear and that scores reflect count-based weighting.

**Acceptance Scenarios**:

1. **Given** HITS is selected and a specific league filter is active, **When** the user runs the analysis, **Then** only clubs from the selected league appear in the result.
2. **Given** HITS is selected and weight mode is "Transfer Count", **When** the user runs the analysis, **Then** the HITS computation uses deal count as the edge weight and results differ from fee-weighted HITS.
3. **Given** HITS is selected, **When** the user changes the "Top N" slider, **Then** the visualization shows the adjusted number of top-ranked clubs.

---

### Edge Cases

- What happens when the HITS algorithm does not converge within the specified number of iterations for a sparse or disconnected graph?
- How does the system handle a dataset where all edge weights are identical (e.g., all Transfer Count = 1)?
- What happens when the user selects HITS with a league filter that yields a very small graph (e.g., only 2 clubs)?
- What if the selected number of iterations is very high (e.g., 50) — does the system remain responsive?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST implement the HITS algorithm to compute both Hub and Authority scores for each club in the transfer network.
- **FR-002**: The system MUST provide an algorithm selector control in the web interface allowing the user to choose between "PageRank" and "HITS" before running a computation.
- **FR-003**: When "HITS" is selected, the system MUST compute and display either Hub or Authority scores based on the user's chosen direction/ranking type.
- **FR-004**: When the analysis direction is set to "Buyers" (Attractors) and HITS is selected, the system MUST display Authority scores (clubs that attract transfers). When set to "Sellers" (Suppliers), the system MUST display Hub scores (clubs that distribute transfers).
- **FR-005**: The algorithm selector MUST default to "PageRank" on initial page load to maintain backward compatibility.
- **FR-006**: The HITS algorithm MUST use the same input data pipeline as PageRank, respecting the active league filter, weight mode, and other parameters.
- **FR-007**: HITS results MUST be displayed using the same visualization components (bar chart and network graph) already used for PageRank, with score labels reflecting the HITS metric (Hub or Authority score).
- **FR-008**: The algorithm selector MUST NOT reset when other controls (league filter, weight mode, direction, iterations, Top N) are changed.
- **FR-013**: When the algorithm selector value is changed, the system MUST automatically rerun the analysis after the same short debounce delay used for league filter and weight mode changes, without requiring the user to click "Run".
- **FR-009**: The HITS algorithm MUST accept the same "iterations" parameter as PageRank to control convergence depth.
- **FR-010**: The system MUST display a loading indicator while the HITS computation is running, identical to the existing PageRank loading behavior.
- **FR-011**: If the HITS computation produces an empty result (due to filtering), the system MUST show the same informative empty-state message used for PageRank.
- **FR-012**: The visualization labels MUST clearly indicate which algorithm produced the displayed results (e.g., "PageRank Score", "Authority Score", or "Hub Score").
- **FR-014**: When HITS is the selected algorithm, the "Damping Factor" input control MUST be visually disabled (greyed out) and MUST display a tooltip or explanatory text stating that damping factor is not applicable to the HITS algorithm. When PageRank is re-selected, the control MUST re-enable.
- **FR-015**: When HITS is the selected algorithm, the direction selector labels MUST dynamically update to "Authority (Buyers)" and "Hub (Sellers)". When PageRank is re-selected, the labels MUST revert to "Attractors (Buyers)" and "Suppliers (Sellers)".

### Key Entities

- **Algorithm Type**: An enumerated selection representing the link-analysis algorithm to run — either "PageRank" or "HITS". Determines the computation method applied to the transfer network.
- **Hub Score**: A HITS-derived metric representing how well a club serves as a distributor/supplier in the transfer network. Clubs that sell players to many highly authoritative buyers receive high Hub scores.
- **Authority Score**: A HITS-derived metric representing how well a club serves as a destination/attractor in the transfer network. Clubs that attract transfers from many high-hub sellers receive high Authority scores.
- **Ranking Direction**: Maps the existing "Buyers/Sellers" direction control to the appropriate HITS score: Buyers → Authority scores, Sellers → Hub scores.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select "HITS" from the algorithm selector and view Hub or Authority rankings within the same interaction session, with results appearing within the same time frame as an equivalent PageRank computation.
- **SC-002**: When running HITS and PageRank on the same dataset with identical parameters, the resulting club rankings are visibly different in at least some cases, confirming distinct algorithms are executed.
- **SC-003**: 100% of existing controls (league filter, weight mode, direction, iterations, Top N, visualization toggle) function identically whether PageRank or HITS is the active algorithm.
- **SC-004**: The page loads with "PageRank" pre-selected and behaves identically to the pre-feature state, ensuring zero regression in existing behavior.
- **SC-005**: A user can complete a full comparison workflow — running PageRank, reviewing results, switching to HITS, running again, and comparing — entirely within the web interface without any command-line interaction.

## Assumptions

- The HITS algorithm will use the same iterative convergence approach as PageRank, where the "iterations" parameter controls the number of Hub/Authority score update cycles.
- Hub and Authority scores will be normalized after each iteration to prevent numerical overflow, following the standard HITS algorithm formulation.
- The existing direction control ("Buyers" / "Sellers") naturally maps to Authority and Hub scores respectively: buying clubs are ranked by Authority, selling clubs by Hub.
- The HITS damping factor parameter is not applicable to the standard HITS algorithm; the existing "Damping Factor" UI control will be greyed out (disabled) with a tooltip when HITS is selected, and re-enabled when PageRank is selected.
- The existing data pipeline (CSV loading, league filtering, weight mode) is algorithm-agnostic and will be reused without modification for HITS input preparation.
- Performance of HITS computation will be comparable to PageRank for the same number of iterations, since both algorithms perform iterative updates over the same graph structure.
