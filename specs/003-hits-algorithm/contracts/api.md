# API Contract: HITS Algorithm Integration

**Feature**: 003-hits-algorithm  
**Date**: 2026-03-31

## Modified Endpoints

### POST `/api/pagerank`

**Change**: Extended request body with `algorithm` field; extended response `meta` with `algorithm` and `score_type`.

#### Request Body (JSON)

```json
{
  "direction": "buyers",
  "iterations": 10,
  "damping_factor": 0.85,
  "top_n": 10,
  "league": "all",
  "weight_mode": "fee",
  "algorithm": "pagerank"
}
```

| Field            | Type    | Required | Default      | Validation               | Notes |
|------------------|---------|----------|--------------|--------------------------|-------|
| `direction`      | string  | No       | `"buyers"`   | `buyers` or `sellers`    | Unchanged |
| `iterations`     | integer | No       | `10`         | 1–50                     | Unchanged; applies to both algorithms |
| `damping_factor` | float   | No       | `0.85`       | 0.0–1.0                  | **Ignored when `algorithm` is `"hits"`** |
| `top_n`          | integer | No       | `10`         | 1–50                     | Unchanged |
| `league`         | string  | No       | `"all"`      | Any string               | Unchanged |
| `weight_mode`    | string  | No       | `"fee"`      | `fee` or `count`         | Unchanged |
| **`algorithm`**  | **string** | **No** | **`"pagerank"`** | **`pagerank` or `hits`** | **New** |

#### Response Body (JSON) — Success (200)

```json
{
  "nodes": [
    {
      "data": {
        "id": "FC Barcelona",
        "label": "FC Barcelona",
        "rank": 2.3456
      }
    }
  ],
  "edges": [
    {
      "data": {
        "source": "Real Madrid",
        "target": "FC Barcelona",
        "weight": 45000000,
        "weight_label": "€45M"
      }
    }
  ],
  "meta": {
    "league": "all",
    "weight_mode": "fee",
    "total_records": 1234,
    "empty": false,
    "algorithm": "hits",
    "score_type": "authority"
  }
}
```

**New `meta` fields:**

| Field        | Type   | Values                                      | Description |
|--------------|--------|---------------------------------------------|-------------|
| `algorithm`  | string | `"pagerank"` or `"hits"`                    | Which algorithm produced the result |
| `score_type` | string | `"pagerank"`, `"authority"`, or `"hub"`     | Which score is shown in `rank` field |

**Node `rank` field semantics**:
- When `algorithm` is `"pagerank"`: `rank` contains the PageRank score (same as before)
- When `algorithm` is `"hits"` and `direction` is `"buyers"`: `rank` contains the Authority score
- When `algorithm` is `"hits"` and `direction` is `"sellers"`: `rank` contains the Hub score

#### Response — Error (500)

```json
{
  "detail": "Error message string"
}
```

No change to error response format.

## Backward Compatibility

- The `algorithm` field defaults to `"pagerank"`, so existing clients that omit it receive identical behavior.
- The `meta` object gains two new fields (`algorithm`, `score_type`), which are additive — existing clients that don't read them are unaffected.
- The node `rank` field continues to hold a numeric score regardless of algorithm.
- No existing endpoints are removed or renamed.

## Unchanged Endpoints

- `GET /` — Serves `index.html` (unchanged)
- `GET /health` — Health check (unchanged)
- `GET /api/leagues` — Returns available leagues (unchanged)
