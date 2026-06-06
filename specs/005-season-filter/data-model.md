# Season Filter Data Model & Contracts

## Entities

### `AlgorithmPayload` (API Request)

The payload structure that the frontend sends to `/api/pagerank` (and equivalent Graph actions) must be updated to include the new chronological season filters.

**New Fields:**
- `start_season` (string): The inclusive start season (e.g., `"2005-2006"` or `"all"`).
- `end_season` (string): The inclusive end season (e.g., `"2010-2011"` or `"all"`).

*Note: Default is "all". If `"all"` is sent, or the fields are completely missing, the backend defaults to full historical analysis.*

### `AlgorithmResultMeta` (API Response)

The metadata block returned by the graph analysis endpoints must be updated to echo the effectively applied time constraint back to the frontend UI, ensuring deterministic visualization presentation.

**New Field:**
- `season_range` (string): Explains the bounds processed by PySpark. Examples: `"2005-2006 to 2010-2011"` or `"All Seasons"`.

## Validation Rules

1. **Chronological Integrity**
   - The sequence of seasons follows the static chronological list (e.g. `['2000-2001', '2001-2002', ..., '2018-2019']`).
   - `start_season` index must be <= `end_season` index.
2. **Missing/Implicit Contexts**
   - If `start_season` is "all" or missing, the constraint defaults to the earliest available date.
   - If `end_season` is "all" or missing, the constraint defaults to the latest available date.
   - For UI simplicity, both are treated jointly as the "All Seasons" state if either actively represents the total sequence natively. 
