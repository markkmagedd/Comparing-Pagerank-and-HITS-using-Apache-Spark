# Data Model: Data-Driven Customization

**Branch**: `002-data-driven-customization`  
**Date**: 2026-03-19  
**Phase**: 1 — Design & Contracts

---

## Entities

### TransferRecord *(source: `transfers.csv` row)*

Represents a single inbound transfer deal row in the dataset.

| Field         | Type    | Source Column | Notes |
|---------------|---------|---------------|-------|
| `team_from`   | `str`   | index 3       | Originating club; stripped of whitespace |
| `league_from` | `str`   | index 4       | League of originating club; stripped |
| `team_to`     | `str`   | index 5       | Destination club; stripped |
| `league_to`   | `str`   | index 6       | League of destination club; stripped |
| `fee`         | `float` | index 9       | Parsed by `parse_fee()`; defaults to `100_000.0` if invalid |

**Count contribution**: Each row contributes exactly `1` to the "Transfer Count" weight mode regardless of fee value or players involved (per Q2 clarification).

**Validation rules**:
- `team_from` and `team_to` MUST be non-empty after stripping; rows with empty clubs are skipped.
- `fee` is parsed defensively via `parse_fee()`. Invalid/missing fees yield `100_000.0` in "fee" mode; fee value is irrelevant in "count" mode.

---

### LeagueFilter *(runtime parameter)*

The active filter applied before RDD aggregation.

| Field    | Type           | Valid Values                             | Default |
|----------|----------------|------------------------------------------|---------|
| `league` | `str \| None`  | Any `League_from`/`League_to` value, or `"all"` | `"all"` |

**Filter predicate** (applied as RDD `.filter()`):
- When `league == "all"` or `None`: no filter applied — all rows pass through.
- When `league` is a specific string: only rows where **both** `league_from == league` and `league_to == league` are retained (intra-league transfers only).
- League comparison is case-sensitive (values as they appear in the dataset).

**State transitions**:
```
"all" (default) → <specific league> → "all" (reset)
```
Single-select only; multi-league selection is out of scope.

---

### WeightMode *(runtime parameter)*

The active weight derivation strategy for edge weights.

| Value     | Edge Weight Formula                     | Unit Displayed  | Default |
|-----------|-----------------------------------------|-----------------|---------|
| `"fee"`   | `sum(parse_fee(row[9]))` per club pair  | `"€{value}"`    | ✅ Yes  |
| `"count"` | `count(rows)` per club pair             | `"{value} deals"`| No     |

Both modes use `reduceByKey(add)` on the RDD; the only difference is the mapped value before aggregation.

---

### AnalysisResult *(API response shape)*

The output of one computation run, parameterised by `LeagueFilter` + `WeightMode`.

```json
{
  "nodes": [
    { "data": { "id": "Real Madrid", "label": "Real Madrid", "rank": 0.2341 } }
  ],
  "edges": [
    { "data": { "source": "FC Barcelona", "target": "Real Madrid", "weight": 120000000, "weight_label": "€120M" } }
  ],
  "meta": {
    "league": "LaLiga",
    "weight_mode": "fee",
    "total_records": 312,
    "empty": false
  }
}
```

| Field              | Type      | Notes |
|--------------------|-----------|-------|
| `nodes[].data.id`  | `str`     | Club name |
| `nodes[].data.label` | `str`   | Same as `id` (display name) |
| `nodes[].data.rank` | `float`  | PageRank score, 4 decimal places |
| `edges[].data.weight` | `float` | Raw aggregated weight value |
| `edges[].data.weight_label` | `str` | Human-readable: `"€120M"` or `"12 deals"` depending on mode |
| `meta.league`      | `str`     | Active filter value (`"all"` or league name) |
| `meta.weight_mode` | `str`     | `"fee"` or `"count"` |
| `meta.total_records` | `int`  | Number of transfer records used after filtering |
| `meta.empty`       | `bool`    | `true` when no records match — frontend shows empty-state message |

---

### LeagueListResponse *(GET /api/leagues response)*

```json
{
  "leagues": ["1.Bundesliga", "Bundesliga", "LaLiga", "Ligue 1", "Premier League", "Serie A", "..."]
}
```

| Field     | Type       | Notes |
|-----------|------------|-------|
| `leagues` | `list[str]`| Sorted alphabetically; derived from distinct `League_from` ∪ `League_to` values in dataset |

---

## State Transitions

```
Page Load
  └─ GET /api/leagues → populate dropdown (one-time)
  └─ Controls: league="all", weight_mode="fee"

User changes league or weight_mode
  └─ Debounce 300ms
  └─ Show loading overlay on viz area
  └─ POST /api/pagerank { ..., league, weight_mode }
       ├─ meta.empty == true  → show empty-state message
       └─ meta.empty == false → render chart/graph, hide overlay

Page Reload
  └─ Controls reset to league="all", weight_mode="fee" (no persistence)
```
