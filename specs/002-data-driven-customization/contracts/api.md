# API Contracts: Data-Driven Customization

**Branch**: `002-data-driven-customization`  
**Date**: 2026-03-19

---

## GET /api/leagues

Returns the distinct league names present in the loaded dataset, sorted alphabetically. Called once on page load to populate the league filter dropdown.

### Request

No body. No query parameters.

### Response `200 OK`

```json
{
  "leagues": [
    "1.Bundesliga",
    "Bundesliga",
    "LaLiga",
    "Ligue 1",
    "Premier League",
    "Serie A"
  ]
}
```

| Field     | Type        | Description |
|-----------|-------------|-------------|
| `leagues` | `list[str]` | Distinct `League_from` ∪ `League_to` values, sorted A→Z |

### Error Cases

| Status | Condition |
|--------|-----------|
| `500`  | Spark context unavailable or dataset unreadable |

---

## POST /api/pagerank *(extended)*

Backward-compatible extension of the existing endpoint. Two new optional fields are added to the request body.

### Request Body

```json
{
  "direction": "buyers",
  "iterations": 10,
  "damping_factor": 0.85,
  "top_n": 10,
  "league": "Premier League",
  "weight_mode": "fee"
}
```

| Field           | Type    | Default    | Constraints | Description |
|-----------------|---------|------------|-------------|-------------|
| `direction`     | `str`   | `"buyers"` | `buyers\|sellers` | Existing field |
| `iterations`    | `int`   | `10`       | 1–50 | Existing field |
| `damping_factor`| `float` | `0.85`     | 0.0–1.0 | Existing field |
| `top_n`         | `int`   | `10`       | 1–50 | Existing field |
| `league`        | `str`   | `"all"`    | Any valid league name or `"all"` | **New** — `"all"` disables filtering |
| `weight_mode`   | `str`   | `"fee"`    | `fee\|count` | **New** — selects edge weight strategy |

### Response `200 OK`

```json
{
  "nodes": [
    {
      "data": {
        "id": "Manchester City",
        "label": "Manchester City",
        "rank": 0.2341
      }
    }
  ],
  "edges": [
    {
      "data": {
        "source": "Manchester City",
        "target": "Arsenal",
        "weight": 45000000,
        "weight_label": "€45M"
      }
    }
  ],
  "meta": {
    "league": "Premier League",
    "weight_mode": "fee",
    "total_records": 418,
    "empty": false
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `nodes[].data.id` | `str` | Club name (unique within response) |
| `nodes[].data.label` | `str` | Display name (same as `id`) |
| `nodes[].data.rank` | `float` | PageRank score (4 d.p.) |
| `edges[].data.source` | `str` | Originating club |
| `edges[].data.target` | `str` | Destination club |
| `edges[].data.weight` | `float` | Raw aggregated weight (fee in € or count) |
| `edges[].data.weight_label` | `str` | Human-readable: `"€45M"` (fee) or `"12 deals"` (count) |
| `meta.league` | `str` | Active league filter echoed back (`"all"` or name) |
| `meta.weight_mode` | `str` | Active weight mode echoed back (`"fee"` or `"count"`) |
| `meta.total_records` | `int` | Number of transfer records after league filtering |
| `meta.empty` | `bool` | `true` when filtering yields 0 records; nodes/edges will be empty arrays |

### Response `200 OK` — Empty State

When `meta.empty == true` (league filter matches no records):

```json
{
  "nodes": [],
  "edges": [],
  "meta": {
    "league": "Wales",
    "weight_mode": "count",
    "total_records": 0,
    "empty": true
  }
}
```

The frontend renders an empty-state message instead of an empty chart/graph.

### Error Cases

| Status | Condition |
|--------|-----------|
| `422`  | Invalid `weight_mode` value (not `fee` or `count`) |
| `422`  | `direction`, `iterations`, `top_n`, `damping_factor` out of valid range (existing) |
| `500`  | Spark computation failure |
