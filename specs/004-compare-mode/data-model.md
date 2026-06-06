# Data Model & Entites

## Overview

The "Compare Mode" feature primarily affects the frontend visualization and orchestration layer. It utilizes the existing PySpark output structures to define new UI-level components. No new backend persistence or PySpark RDD models are required.

## Key UI Entities

### Comparison Result

A paired set of algorithm outputs derived from concurrent API requests to the existing `/api/pagerank` endpoint.

**Structure**:
```typescript
interface ComparisonResult {
  pagerank_data: GraphResult; // Expected to contain PageRank scores
  hits_data: GraphResult;     // Expected to contain HITS scores (Authority or Hub)
  overlap_metadata: OverlapMetadata;
}
```

### Overlap Metadata

The calculated intersection between the top-N nodes returned by both algorithms.

**Structure**:
```typescript
interface OverlapMetadata {
  overlap_set: Set<string>; // Set of club IDs present in both algorithms' results
  overlap_count: number;    // Size of the overlap set
  total_n: number;          // Total number of unique clubs requested (e.g., top-n, but bounded by max available)
}
```

### State Management
The UI state will track:
- `isCompareModeActive` (boolean)
- `currentFilters` (the shared payload for both algorithms)
- Both result sets locally to power re-rendering without re-fetching if only visualization types toggle (though FR-005 mandates only bar charts).
