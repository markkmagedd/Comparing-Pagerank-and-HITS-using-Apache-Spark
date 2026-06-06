# Research: Compare Mode Implementation

## 1. API Strategy for Compare Mode

**Decision**: The frontend will make two concurrent API calls to the existing `POST /api/pagerank` endpoint rather than creating a new combined endpoint.

**Rationale**: 
- **Simplicity**: No backend changes are required. The existing endpoint already supports the `algorithm` parameter (added in feature 003).
- **Concurrency**: By using `Promise.all()` in JavaScript, both requests execute concurrently, allowing FastAPI to schedule both PySpark jobs (PageRank and HITS) simultaneously.
- **Modularity**: Keeps the backend API focused and simple rather than introducing complex multi-purpose "compare" payloads.

**Alternatives considered**: 
- *New `/api/compare` backend endpoint*: This would require modifying FastAPI and `TransferAnalyzer` to compute and return a combined JSON object. It adds unnecessary complexity to the backend when the frontend is fully capable of orchestrating two fetches.

## 2. Frontend Layout & Visualization Setup

**Decision**: The frontend will dynamically append a second container (e.g. `chart-container-right`) alongside the existing one when Compare mode is active, splitting the available width using flexbox/grid.

**Rationale**: 
- **Isolation**: Modifying Chart.js instances can be finicky. Having two separate canvas elements ensures there's no state contamination.
- **Maintainability**: The existing rendering functions `renderBarChart` can be reused by simply passing the target canvas context as an argument.

**Alternatives considered**: 
- *A single grouped bar chart*: Chart.js supports grouped bars, but this violates FR-002 ("visualization area MUST split into two side-by-side panels"). Side-by-side panels are much clearer for dense network lists.
