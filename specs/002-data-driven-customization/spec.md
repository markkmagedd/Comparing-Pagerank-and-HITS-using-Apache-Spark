# Feature Specification: Data-Driven Customization

**Feature Branch**: `002-data-driven-customization`  
**Created**: 2026-03-19  
**Status**: Draft  
**Input**: User description: "Data-Driven Customization: League Filtering — Let the user filter the source data to specific leagues (e.g., only 'Premier League' vs. 'La Liga'). This would show the internal hierarchy of a single league. Custom Weighting Selector — Currently, you use 'Transfer Fee' as the weight. Allow the user to toggle to 'Transfer Count' (number of deals) to see if volume or value matters more for club influence."

## Clarifications

### Session 2026-03-19

- Q: Should changing a control (league filter or weight mode) automatically trigger a new analysis run, or should the user press an explicit "Apply" / "Run" button? → A: Auto-run — analysis reruns automatically after a short debounce delay whenever either control changes.
- Q: When computing the "Transfer Count" weight between two clubs, should each row/record in the dataset count as 1, or should count reflect the number of distinct players transferred? → A: Record count — each row/deal entry in the dataset counts as 1 toward the edge weight between a club pair, regardless of how many players are involved in that deal.
- Q: Should the league filter support selecting multiple leagues simultaneously, or only one at a time? → A: Single-select — only one league can be active at a time, alongside the "All Leagues" baseline option. Multi-league selection is out of scope.
- Q: What should the visualization area show while a new computation is in progress after a control change? → A: Loading overlay — the existing visualization dims and a loading spinner appears over it until the new result is ready.
- Q: Should the active league filter and weight mode selections persist across page loads or browser sessions? → A: No persistence — controls always reset to "All Leagues" + "Transfer Fee" on every page load. URL-based and session-storage persistence are out of scope.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter Analysis to a Specific League (Priority: P1)

A researcher studying club influence within a single football competition wants to focus the graph analysis exclusively on transfer activity within, for example, the Premier League. By selecting "Premier League" from a league filter, only the clubs and transfers belonging to that league appear in the PageRank / HITS computation and visualization. The resulting ranking reflects the internal power hierarchy of that league alone, untainted by inter-league transfers.

**Why this priority**: The ability to isolate a single league is the primary value proposition of this feature. Without it, all subsequent customization (weighting) operates on mixed-league data that may mask meaningful intra-league patterns. This is the foundational filter.

**Independent Test**: Select a single league from the filter, trigger analysis, and verify that every club node shown in the visualization belongs to that league and that clubs from other leagues are absent.

**Acceptance Scenarios**:

1. **Given** the visualization page is loaded with multi-league data available, **When** the user selects "Premier League" from the league filter control, **Then** a loading overlay with a spinner appears over the visualization immediately, followed by the analysis completing using only Premier League transfer records and the graph displaying only Premier League clubs.
2. **Given** a computation is in progress (loading overlay active), **When** the new result arrives, **Then** the loading overlay disappears and the updated visualization is shown immediately.
2. **Given** a league filter is active, **When** no transfers exist for the selected league in the dataset, **Then** the system displays a clear "No data available for the selected league" message and the graph area shows an empty state.
3. **Given** a league filter is active, **When** the user clears the filter (selects "All Leagues"), **Then** the analysis reverts to using the full multi-league dataset and all clubs reappear in the visualization.
4. **Given** the page loads for the first time, **When** no explicit filter choice has been made, **Then** the system defaults to "All Leagues" and shows the full dataset.

---

### User Story 2 - Switch Between Transfer Fee and Transfer Count Weighting (Priority: P2)

A researcher wants to understand whether a club's influence in the transfer market is better explained by the *total monetary value* of its transfers or by the *sheer volume* of deals it participates in. They can toggle a "Weight By" control between **Transfer Fee** (monetary value) and **Transfer Count** (number of deals) to rerun the PageRank / HITS algorithm with the chosen weight and compare the resulting club rankings.

**Why this priority**: This is the second core customisation axis. It delivers research value by letting analysts test whether high-value clubs and high-volume clubs cluster differently in influence rankings. It requires league filtering to already exist (or at least the data pipeline to be in place), so it is P2.

**Independent Test**: With default settings, note the top-5 clubs by rank. Toggle the weight selector to "Transfer Count", trigger analysis, and confirm the ranking list changes to reflect count-based weighting; then toggle back to "Transfer Fee" and confirm the original ranking is restored.

**Acceptance Scenarios**:

1. **Given** the default "Transfer Fee" weight is active, **When** the user switches to "Transfer Count", **Then** the analysis reruns using deal count as the edge weight and the displayed rankings update accordingly.
2. **Given** "Transfer Count" is selected, **When** the user switches back to "Transfer Fee", **Then** the rankings revert to fee-weighted results.
3. **Given** either weight mode is active, **When** the user hovers over or inspects a graph edge or bar-chart element, **Then** the shown weight value reflects the currently selected mode (e.g., "€45M" for fee, "12 deals" for count).
4. **Given** a league filter and a weight mode are both active, **When** the user changes either control, **Then** the analysis re-executes respecting both the active league filter and the active weight mode simultaneously.

---

### User Story 3 - Combine League Filter and Weight Mode for Targeted Analysis (Priority: P3)

A researcher wants to ask a compound question: "Among Premier League clubs, do high-volume dealers rank differently than high-spend clubs?" They apply both the league filter and the weight mode toggle together to answer this question without needing separate sessions.

**Why this priority**: This story tests the orthogonality of the two controls and validates their combined use. It is P3 because it is implicitly covered when P1 and P2 work correctly together, but it deserves an explicit scenario to ensure no interaction bugs exist.

**Independent Test**: Set league = "La Liga", weight = "Transfer Count", run analysis; then change weight to "Transfer Fee" without changing the league filter, run again, and confirm the league filter remains "La Liga" throughout both runs.

**Acceptance Scenarios**:

1. **Given** the league filter is set to "La Liga" and weight is "Transfer Count", **When** the user changes weight to "Transfer Fee", **Then** the league filter remains "La Liga" and only La Liga results update to reflect fee-based weighting.
2. **Given** both controls have non-default values, **When** the user resets both to defaults, **Then** the system returns to "All Leagues" and "Transfer Fee" simultaneously without error.

---

### Edge Cases

- What happens when the selected league has only one club in the dataset (no edges in the graph)?
- How does the system handle a league name that contains special characters or non-ASCII text?
- What if a transfer record is missing a fee value — is it excluded or treated as zero when "Transfer Fee" weight is selected?
- What if a transfer record has a fee of zero but a non-zero count — how is it handled in "Transfer Fee" mode?
- What if the user rapidly switches between weight modes or leagues before the previous computation completes?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a single-select league filter control that lists all distinct leagues present in the loaded dataset; only one league can be active at a time.
- **FR-002**: When a league is selected, the system MUST restrict transfer records used in the PageRank / HITS computation to only those belonging to that single chosen league.
- **FR-003**: The system MUST include an "All Leagues" option in the league filter that resets filtering and uses the complete dataset.
- **FR-004**: The system MUST provide a weight mode selector with at least two options: "Transfer Fee" (monetary value) and "Transfer Count" (number of deals).
- **FR-005**: When either control (league filter or weight mode) is changed, the system MUST automatically rerun the ranking algorithm after a short debounce delay (no manual "Apply" / "Run" button required) and update all visualizations with the new result.
- **FR-006**: The system MUST apply both the active league filter and the active weight mode simultaneously in each computation run.
- **FR-007**: Edge or bar-chart labels visible to the user MUST reflect the currently active weight mode in their displayed values and units.
- **FR-008**: Transfer records with a missing or zero fee MUST be handled gracefully in "Transfer Fee" mode — either excluded from the computation or treated as zero — and the applied behaviour MUST be consistent and documented in the UI (e.g., a tooltip or note).
- **FR-009**: Changing either control MUST NOT reset the other control's selection.
- **FR-010**: If the combination of filter and weight produces an empty result set, the system MUST display an informative empty-state message rather than a blank or broken visualization.
- **FR-011**: The default state on every page load MUST be "All Leagues" and "Transfer Fee". Control selections MUST NOT persist across page loads or browser sessions; no URL query parameters, cookies, or browser storage are used to retain filter state.
- **FR-012**: While a computation is in progress following a control change, the system MUST display a loading overlay with a spinner on top of the existing (now stale) visualization; the overlay MUST be dismissed automatically when the new result is rendered.

### Key Entities

- **League**: A named football competition (e.g., "Premier League", "La Liga"). Identified by a string label present in the transfer dataset. Serves as the grouping key for the league filter.
- **Transfer Record**: A single row in the dataset representing one transfer deal between an originating and a destination club, with attributes: monetary fee, league, and an implicit count contribution of 1 per row. A single record may involve one or more players but always contributes exactly 1 to the "Transfer Count" edge weight.
- **Weight Mode**: An enumerated selection representing how edge weight is derived — either aggregated monetary value ("Transfer Fee") or aggregated deal volume ("Transfer Count").
- **Analysis Result**: The output of a PageRank / HITS computation run, parameterised by the active League filter and Weight Mode at the time of execution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can narrow the visualization to a single league and see updated rankings within the same interaction session, in under 5 seconds from making their selection.
- **SC-002**: A user can switch weight mode between "Transfer Fee" and "Transfer Count" and observe a visibly different club ranking in the resulting visualization.
- **SC-003**: Both controls can be changed independently without affecting each other's selection state, verifiable by toggling each control multiple times in alternating order.
- **SC-004**: 100% of transfer records associated with the selected league are included in the computation (and 0% from other leagues) when a specific league filter is active.
- **SC-005**: An empty-state message is displayed in 100% of cases where the filter/weight combination yields no computable results, preventing any broken or blank visualization from being shown to the user.
- **SC-006**: On initial page load, the visualization behaves identically to the pre-feature baseline (all leagues, fee-weighted), ensuring no regression in existing functionality.

## Assumptions

- The existing dataset already contains a league identifier field per transfer record; no external league lookup service is required.
- "Transfer Count" is defined as the number of dataset rows (deal records) between a pair of clubs. Each row contributes exactly 1 to the count, regardless of the number of players involved in that deal. Player count is explicitly out of scope for this weight mode.
- Transfer records with a missing fee are excluded from "Transfer Fee" mode computations rather than defaulted to zero, to avoid artificially inflating or deflating rankings. The UI will note this behavior.
- The available league list is derived dynamically from the loaded dataset on each page load; it is not hardcoded.
- The two controls (league filter, weight mode) are UI-level filters applied before feeding data into the existing algorithm — the core algorithm itself is not modified.
- The league filter is single-select: the user can activate exactly one league at a time, or the "All Leagues" baseline. Selecting multiple leagues simultaneously is explicitly out of scope for this feature.
- Control selections do not persist across page loads or browser sessions. No URL params, session storage, or cookies are used. This is a stateless exploration tool.
- Simultaneous rapid control changes are debounced so that only the final stable state (after a brief idle pause) triggers a computation, preventing stale intermediate results from rendering. No explicit "Apply" / "Run" button exists; submission is automatic.
