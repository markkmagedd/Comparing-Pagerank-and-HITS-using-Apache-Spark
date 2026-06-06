# Data Model: PageRank Web Visualization

## Computation Request (API Context)
- `filter_type` (Enum): 'buyers' | 'sellers'
- `iterations` (Int): Default 10. Max bounding ~ 50.
- `damping_factor` (Float): Default 0.85. Bounds 0.0 - 1.0.
- `top_n` (Int): Default 10. Max bounding ~ 50. Limits graph clutter.

## Visualization Result (Graph Topology API Context)
- `nodes`: Array of node records
  - `id`: Unique identifier (e.g. Club Name)
  - `label`: Display text
  - `rank`: PageRank score (used for node sizing visually)
- `edges`: Array of connection records
  - `source`: Club Name ID
  - `target`: Club Name ID
  - `weight`: Absolute transfer fee aggregate between these clubs.
