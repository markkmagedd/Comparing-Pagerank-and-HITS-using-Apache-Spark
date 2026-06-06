# Research: HITS Algorithm Integration

**Feature**: 003-hits-algorithm  
**Date**: 2026-03-31

## R1: HITS Algorithm Formulation for Weighted Directed Graphs

**Decision**: Implement weighted HITS using the standard mutual-reinforcement update with edge weights as multiplicative factors during Hub/Authority propagation.

**Rationale**: The standard HITS algorithm computes two scores per node — Authority (how good a node is as a destination) and Hub (how good a node is as a source/distributor). In a weighted graph, the edge weight naturally scales the contribution: a transfer worth €50M contributes more to a club's Authority score than a €1M transfer. This mirrors how `run_pagerank()` already uses weights proportionally.

**Algorithm pseudocode (per iteration)**:
```
For each node u:
  authority(u) = Σ hub(v) × weight(v → u)   for all v that point to u
  hub(u)       = Σ authority(v) × weight(u → v)  for all v that u points to

Normalize:
  authority_norm = √(Σ authority(u)²)
  hub_norm       = √(Σ hub(u)²)
  authority(u) = authority(u) / authority_norm
  hub(u)       = hub(u) / hub_norm
```

**Alternatives considered**:
- Unweighted HITS (ignore edge weights): Rejected — loses the weight mode feature (fee vs count) and reduces analytical value.
- HITS with damping (Bharat & Henzinger variant): Rejected — adds unnecessary complexity and the standard HITS already converges well on transfer networks of this size.

## R2: Hub/Authority ↔ Direction Mapping

**Decision**: Map "Buyers" (Attractors) direction → Authority scores; "Sellers" (Suppliers) direction → Hub scores.

**Rationale**: 
- In the transfer graph, edges go from selling club to buying club (Seller → Buyer).
- **Authority** measures how much a node is pointed to → Buyers receive edges → Buyers have Authority.
- **Hub** measures how well a node points to important nodes → Sellers distribute edges → Sellers have Hub.
- This alignment matches the semantic meaning of the existing PageRank directions: "Attractors" (PageRank on buyer edges) ≈ "Authority" (HITS on same graph).

**Alternatives considered**:
- Reverse mapping (Buyers → Hub, Sellers → Authority): Rejected — contradicts the definition of Hub/Authority in the HITS literature.

## R3: RDD Implementation Strategy

**Decision**: Implement `run_hits()` using the same RDD join-flatMap-reduceByKey pattern as `run_pagerank()`, operating on the same `(source, (destination, weight))` edge RDD.

**Rationale**: Constitution Principle I mandates PySpark for all intensive computation. The existing `run_pagerank()` demonstrates the pattern. HITS requires two passes per iteration (Authority update, then Hub update), but each pass uses the same RDD operations. Both Hub and Authority RDDs can be maintained in parallel.

**Implementation detail**:
- HITS needs edges in both directions (forward for Hub update, reverse for Authority update)
- Construct both `forward_links` and `reverse_links` from the same input RDD: `forward_links = edges_rdd.groupByKey()`, `reverse_links = edges_rdd.map(swap).groupByKey()`
- Cache both link RDDs for reuse across iterations
- After all iterations, return `(authority_rdd, hub_rdd)`

**Alternatives considered**:
- GraphX/GraphFrames: Rejected — would add a heavy dependency and the dataset size doesn't warrant it.
- Pandas-based computation: Rejected — violates Constitution Principle I (PySpark Scalability First).

## R4: Normalization Strategy

**Decision**: Use L2 (Euclidean) normalization after each iteration for both Hub and Authority vectors.

**Rationale**: Standard HITS uses L2 normalization to prevent score explosion. After computing raw Authority and Hub sums, divide each score by the L2 norm of the entire vector: `norm = sqrt(sum(score_i^2))`. This ensures convergence and produces scores in a comparable range.

**Implementation**: After `reduceByKey(add)`, compute the L2 norm via an additional `.map().reduce()` pass, then `.mapValues(lambda x: x / norm)`.

**Alternatives considered**:
- L1 normalization (sum to 1): Viable but less standard for HITS; L2 is canonical.
- No normalization: Rejected — scores diverge exponentially.

## R5: API Design — Single Endpoint vs New Endpoint

**Decision**: Extend the existing `POST /api/pagerank` endpoint with an `algorithm` field rather than creating a separate `POST /api/hits` endpoint.

**Rationale**: 
- Both algorithms accept the same inputs (direction, iterations, top_n, league, weight_mode) and return the same output shape (nodes, edges, meta).
- A single endpoint simplifies frontend logic — only the payload field changes.
- The `meta` response already includes contextual information; adding `algorithm` and `score_type` fields extends this naturally.
- Backward compatibility: `algorithm` defaults to `"pagerank"`, so existing clients work unchanged.

**Alternatives considered**:
- Separate `POST /api/hits` endpoint: Rejected — duplicates routing logic and request/response models for functionally identical shapes.
- Renaming endpoint to `/api/analyze`: Considered but deferred — avoiding a breaking change to existing endpoint URL.

## R6: Damping Factor Handling

**Decision**: The `damping_factor` field is still accepted in the API request when HITS is selected, but ignored by the backend. The frontend disables the control (greyed out + tooltip).

**Rationale**: 
- Keeping the field in the Pydantic model avoids conditional validation logic.
- The backend simply doesn't pass `damping` to `run_hits()` — it only has `iterations`.
- The frontend provides the user feedback by disabling the control.

**Alternatives considered**:
- Remove damping from the request when HITS is selected (frontend): More complex JS logic for marginal benefit.
- Reject requests with damping when algorithm is HITS: Overly strict; doesn't improve UX.
