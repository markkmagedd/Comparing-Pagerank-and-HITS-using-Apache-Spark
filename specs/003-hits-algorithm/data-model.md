# Data Model: HITS Algorithm Integration

**Feature**: 003-hits-algorithm  
**Date**: 2026-03-31

## Entities

### Algorithm Type (new)

An enumerated value controlling which link-analysis algorithm to execute.

| Field    | Type   | Values                  | Default      |
|----------|--------|-------------------------|--------------|
| `algorithm` | `str` | `"pagerank"`, `"hits"` | `"pagerank"` |

**Validation**: Must match pattern `^(pagerank|hits)$`.

### Score Type (new, derived)

A read-only label derived from the combination of algorithm and direction. Not user-editable; computed by the backend.

| Algorithm  | Direction  | Score Type   | Display Label      |
|------------|------------|-------------|-------------------|
| `pagerank` | `buyers`   | `"pagerank"` | "PageRank Score"  |
| `pagerank` | `sellers`  | `"pagerank"` | "PageRank Score"  |
| `hits`     | `buyers`   | `"authority"` | "Authority Score" |
| `hits`     | `sellers`  | `"hub"`       | "Hub Score"       |

### Hub Score (new, computed)

A floating-point value computed by the HITS algorithm for each node, representing how well the node distributes influence (sells to highly authoritative clubs).

| Field    | Type    | Range       | Notes                          |
|----------|---------|-------------|--------------------------------|
| `hub`    | `float` | `[0.0, 1.0]` | L2-normalized per iteration  |

### Authority Score (new, computed)

A floating-point value computed by the HITS algorithm for each node, representing how well the node attracts influence (buys from high-hub clubs).

| Field       | Type    | Range       | Notes                          |
|-------------|---------|-------------|--------------------------------|
| `authority` | `float` | `[0.0, 1.0]` | L2-normalized per iteration  |

### Calculation Request (extended)

Extends the existing `CalculationRequest` Pydantic model with the algorithm field.

| Field            | Type    | Default     | Validation                    | Changed? |
|------------------|---------|-------------|-------------------------------|----------|
| `direction`      | `str`   | `"buyers"`  | `^(buyers\|sellers)$`         | No       |
| `iterations`     | `int`   | `10`        | `1 ≤ x ≤ 50`                 | No       |
| `damping_factor` | `float` | `0.85`      | `0.0 ≤ x ≤ 1.0`              | No (ignored for HITS) |
| `top_n`          | `int`   | `10`        | `1 ≤ x ≤ 50`                 | No       |
| `league`         | `str`   | `"all"`     | Free text                     | No       |
| `weight_mode`    | `str`   | `"fee"`     | `^(fee\|count)$`              | No       |
| **`algorithm`**  | **`str`** | **`"pagerank"`** | **`^(pagerank\|hits)$`** | **New**  |

### Analysis Result Meta (extended)

Extends the existing `meta` dictionary returned in the API response.

| Field            | Type   | Values                              | Changed? |
|------------------|--------|-------------------------------------|----------|
| `league`         | `str`  | League name or `"all"`              | No       |
| `weight_mode`    | `str`  | `"fee"` or `"count"`               | No       |
| `total_records`  | `int`  | Edge count                          | No       |
| `empty`          | `bool` | `true` if no results                | No       |
| **`algorithm`**  | **`str`** | **`"pagerank"` or `"hits"`**    | **New**  |
| **`score_type`** | **`str`** | **`"pagerank"`, `"authority"`, or `"hub"`** | **New** |

## Relationships

```
CalculationRequest.algorithm → determines → Algorithm Type
Algorithm Type + Direction → derives → Score Type
Score Type → determines → display label in visualization
```

## State Transitions

The algorithm selector is stateless (no persistence). On page load it resets to `"pagerank"`. The state machine for the damping factor control:

```
[PageRank selected] → damping enabled (interactive)
[HITS selected]     → damping disabled (greyed out, tooltip visible)
[PageRank re-selected] → damping re-enabled
```

Direction labels follow a parallel transition:

```
[PageRank selected] → "Attractors (Buyers)" / "Suppliers (Sellers)"
[HITS selected]     → "Authority (Buyers)" / "Hub (Sellers)"
```
