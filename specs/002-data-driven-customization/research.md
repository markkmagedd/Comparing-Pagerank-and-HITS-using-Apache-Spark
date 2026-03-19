# Research: Data-Driven Customization

**Branch**: `002-data-driven-customization`  
**Date**: 2026-03-19  
**Phase**: 0 — Outline & Research

---

## 1. Dataset Structure

**Decision**: The existing `transfers.csv` has `League_from` (col index 4) and `League_to` (col index 5) fields per row alongside `Transfer_fee` (col index 9).

**Rationale**: Inspection of the live dataset confirms 124 distinct league strings. League filtering can be applied at the RDD parsing step (column 4 and/or 5) before any aggregation, requiring no schema changes.

**Key finding — column indices (0-based)**:

| Index | Field           | Example                |
|-------|-----------------|------------------------|
| 0     | Name            | "Luís Figo"            |
| 1     | Position        | "Right Winger"         |
| 2     | Age             | 27                     |
| 3     | Team_from       | "FC Barcelona"         |
| 4     | League_from     | "LaLiga"               |
| 5     | Team_to         | "Real Madrid"          |
| 6     | League_to       | "LaLiga"               |
| 7     | Season          | "2000-2001"            |
| 8     | Market_value    | NA                     |
| 9     | Transfer_fee    | 60000000               |

**Alternatives considered**: Filtering by `League_from` only vs. `League_to` only vs. both. Chosen approach: filter records where **both** `League_from` and `League_to` match the selected league, ensuring only intra-league transfers are included in the computation. Cross-league transfers are excluded when a filter is active.

---

## 2. League Filter — Data Delivery

**Decision**: The backend derives available leagues dynamically on each `/api/pagerank` request (or a dedicated `/api/leagues` endpoint) by scanning the RDD.

**Rationale**: With 124 leagues, hardcoding is not viable. The dataset fits in memory (532 KB); computing distinct leagues from the already-cached `transfers` RDD is cheap.

**Implementation pattern**: Add a `GET /api/leagues` endpoint that returns `{"leagues": ["LaLiga", "Premier League", ...]}` sorted alphabetically. The frontend calls this once on page load to populate the league filter `<select>` dropdown.

**Alternatives considered**:
- Embedding leagues in the pagerank response: rejected — leagues don't change per computation.
- Hardcoding the top-N leagues: rejected — would fail the FR-001 requirement that the list reflects actual dataset contents.

---

## 3. Weight Mode — Backend Filter Strategy

**Decision**: Extend `TransferAnalyzer._load_data()` and `get_top_graph()` to accept `weight_mode: str` (`"fee"` | `"count"`) and `league: str | None` parameters.

**Rationale**: The current pipeline maps `((Team_from, Team_to), fee)` and does `reduceByKey(add)`. For "count" mode, replace the fee with a constant `1` per row before `reduceByKey(add)`, giving the total deal count per club pair — exactly aligned with the Q2 clarification (each CSV row = 1 count, regardless of players).

**Fee mode** (existing behaviour preserved):
```
((Team_from, Team_to), parse_fee(x[9]))  →  reduceByKey(add)  →  aggregated fee
```

**Count mode** (new):
```
((Team_from, Team_to), 1)  →  reduceByKey(add)  →  deal count
```

**Alternatives considered**:
- Two separate `_load_data` calls: rejected — the RDD can share file I/O; branching happens only at the map step.
- Computing both modes simultaneously: rejected — adds unnecessary complexity; modes are mutually exclusive per request.

---

## 4. League Filter — Backend Filter Strategy

**Decision**: Apply the league filter as a `.filter()` on the raw data RDD **before** the weight aggregation map, preserving the existing PySpark pipeline shape.

**Filter predicate (intra-league)**:
```python
lambda x: x[4].strip() == league and x[6].strip() == league
```
where `x[4]` = `League_from`, `x[6]` = `League_to`.

**"All Leagues" default**: When `league` is `None` or `"all"`, the filter step is skipped entirely — zero code change to the existing path.

**Alternatives considered**: Filtering on `League_from` only (shows clubs that sold from a league), or `League_to` only (clubs that bought into a league). Intra-league (both match) is chosen to faithfully represent the "internal hierarchy of a single league" as stated in the feature description.

---

## 5. API Contract Extension

**Decision**: Extend the existing `POST /api/pagerank` request body with two optional fields (`league`, `weight_mode`) using Pydantic defaults that match pre-feature behaviour.

**Existing `CalculationRequest`** is extended to:
```python
league: str = Field("all", description="League name or 'all'")
weight_mode: str = Field("fee", pattern="^(fee|count)$")
```

**Rationale**: Backward-compatible — existing callers sending no new fields continue to work with `"all"` leagues and `"fee"` weight mode. No breaking change.

**Alternatives considered**: New dedicated endpoint (`POST /api/pagerank/filtered`): rejected — duplicates logic and breaks existing frontend integration without benefit.

---

## 6. Frontend — League Dropdown Population

**Decision**: On page load, call `GET /api/leagues` once. Populate a `<select id="league">` element with an "All Leagues" first option (`value="all"`) followed by the sorted league list. Attach a `change` event listener that debounces (300 ms) and re-submits the form.

**Debounce strategy**: Use a `setTimeout`/`clearTimeout` pattern on control `change` events. 300 ms idle window is appropriate — fast enough to feel responsive, long enough to avoid double-fire on keyboard navigation through `<select>` options.

**Alternatives considered**: Search/autocomplete input for 124 leagues: deferred — dropdown is simpler and sufficient for this research tool.

---

## 7. Frontend — Weight Mode Toggle

**Decision**: Replace or extend the existing controls area with a two-button toggle (radio-style) or a `<select>` for weight mode, with values `"fee"` and `"count"`. The same debounced submit listener applies.

**Edge weight display**: When rendering edges in the network graph or tooltips in the bar chart, append the unit dynamically: `"€{weight}M"` for fee mode, `"{weight} deals"` for count mode.

**Alternatives considered**: Checkbox: rejected — binary toggle is confusing as a checkbox. Radio buttons: viable alternative but the existing "viz toggle" button pattern (`.viz-toggle-btn`) is already established in `graph.js` and can be reused for the weight mode toggle for visual consistency.

---

## 8. Loading Overlay Implementation

**Decision**: Reuse or extend the existing `loader` element (`#loader`) for the full-page loading state triggered by the existing form submit. For the new auto-run debounce path, apply a dedicated `#viz-loading-overlay` CSS class that dims only the visualization area (not the control panel), matching acceptance scenario Q4-A.

**Rationale**: The existing `#loader` is a full-screen spinner tied to the `<form>` submit. For auto-run (no button press), a localized overlay on top of the chart/graph area is the correct UX — the user can still see that controls remain active.

---

## 9. Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. PySpark Scalability First | ✅ Pass | League filter and weight mode applied as RDD `.filter()` and `.map()` — fully distributed |
| II. Function Modularity | ✅ Pass | New `league` and `weight_mode` params added to existing functions; `GET /api/leagues` is a single-purpose function |
| III. Safe App Initialization | ✅ Pass | No changes to SparkSession initialization path |
| IV. Robust Data Parsing | ✅ Pass | Missing fee defaults to 100k (existing `parse_fee`); for "count" mode, no fee parsing needed at all |
| V. Deterministic Output Artifacts | ✅ Pass | No new output files; visualization remains in-browser |

No violations. Complexity justification table not required.
