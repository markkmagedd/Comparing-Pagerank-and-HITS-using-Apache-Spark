# Phase 0: Research & Architecture Decisions

## Decision 1: PySpark Season Filtering Mechanism

**Decision**: The `start_season` and `end_season` strings will be passed via the FastAPI JSON payload and utilized to filter the source `transfers_df` DataFrame *before* any RDD mapping or algorithmic computations occur.

**Rationale**: By filtering at the DataFrame level immediately after CSV loading/parsing (or within an initial `filter()` operation), we significantly reduce the size of the dataset pushed through the intensive Graph computation stages (PageRank/HITS). This strictly adheres to the "PySpark Scalability First" principle. When `start_season` or `end_season` is absent or "all", the filter operation will be bypassed.

**Alternatives Considered**:
- Post-filtering the nodes after PageRank calculation: Rejected. Highly inefficient because PySpark would compute ranks across the entire 20-year graph for nodes that may only exist in a tight 2-year window.
- Splitting the single `transfers.csv` into multiple season-specific CSVs on disk: Rejected. Unnecessary overhead and breaks current simplicity; PySpark's DataFrame `.filter()` or `.where()` is perfectly optimized for memory-fast columnar filtering.

## Decision 2: Frontend "All Seasons" & Invalid Range Handling UX

**Decision**: The dropdowns will span from "2000-2001" to "2018-2019" chronologically. An "All Seasons" option will be injected at the very top of both the Start Season and End Season `<select>` elements. The frontend JavaScript will enforce chronological validity by dynamically adding the `disabled` attribute to any `<option>` in the End Season dropdown that chronologically precedes the currently selected Start Season (and vice versa).

**Rationale**: This fulfills the prioritized UX integration requirement (US2) and explicitly satisfies the resolution of the clarification phase. By dynamically disabling options, users cannot construct an invalid time boundary, meaning the backend does not need complex return-error schemas for bad date ranges.

**Alternatives Considered**:
- Using an `<input type="date">` UI: Rejected. The data is grouped by distinct season tokens (e.g., "2000-2001"), not arbitrary days/months. Dropdowns mapping to explicit dataset tokens guarantee exact matches.
- Throwing a Javascript `alert()` upon invalid selection: Rejected (per clarification) because it allows the user to make a mistake first rather than guiding them inherently.

## Decision 3: Metadata Propagation

**Decision**: The backend API response `meta` block (already natively used for `empty`, `weight_mode`, `league`, `score_type`) will be expanded to echo back the utilized `season_range` string (e.g., `"2010-2011 to 2012-2013"` or `"All Seasons"`). The frontend will parse this and display it cleanly in the existing `#overlap-summary` container or a dedicated `#season-summary` badge directly above the chart panels.

**Rationale**: Meets User Story 3 efficiently without redefining the frontend state machine. It guarantees that the UI always displays the *actual* bounds used by the backend computation, aligning with "Deterministic Output Artifacts" principles.
