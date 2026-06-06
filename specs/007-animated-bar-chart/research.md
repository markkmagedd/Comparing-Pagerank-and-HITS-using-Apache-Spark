# Research & Technical Decisions: Animated Bar Chart

## 1. D3.js Animated Bar Chart Race Implementation

- **Decision**: Implement the animated bar chart using standard D3.js `d3.transition()` chained sequences.
- **Rationale**: D3.js provides fine-grained control over element transitions, making it straightforward to swap Y coordinates for bars smoothly as data changes between years. This easily fulfills the requirement for smooth animations (FR-004, SC-001) and allows pausing/resuming controls via `d3.interrupt()` or managing transition timing.
- **Alternatives considered**: Using a higher-level library like Chart.js or Recharts. Rejected because they offer less control over the exact interpolation and SVG manipulation needed for a high-quality "race" animation, and D3.js is already documented as an active technology in the project stack.

## 2. API Payload Structure for Temporal Data

- **Decision**: The backend will expose a single JSON payload structured as an array of YearlyRankings: `[{ year: 2010, rankings: [{ club: "A", val: 100 }, ...] }, ...]`.
- **Rationale**: This fulfills FR-008 perfectly, giving the frontend a single block of data to iterate over seamlessly. It removes network latency from the animation playback equation (SC-001).
- **Alternatives considered**: Streaming each year via WebSockets. Rejected as overkill for this dataset size and unnecessarily complex compared to a single bulk fetch.

## 3. PySpark Yearly Aggregation Method

- **Decision**: The backend will process the dataset sequentially by year to generate graph topologies, run the PageRank/HITS algorithm for each year, and append the top 10 results to a final list. 
- **Rationale**: Ensures deterministic and scalable PySpark execution, aligning with Constitution Principle I.
- **Alternatives considered**: Attempting to implement a custom temporal-enabled PageRank in a single MapReduce pass. Rejected due to extreme cognitive and architectural complexity. Sequentially running standard PageRank filtered by year is simpler and mathematically sound for isolated yearly rankings.
