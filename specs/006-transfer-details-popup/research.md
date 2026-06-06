# Phase 0: Research

## Unknowns Resolved

### 1. API Endpoint Architecture
- **Decision**: Add a new `GET /api/transfers/{club_name}` endpoint in `app.py`.
- **Rationale**: FastAPI simplifies creating dynamic parameterized routes effortlessly. Standard REST pattern for resource fetching.
- **Alternatives considered**: Passing back all transfer strings appended to the initial graph load in `/api/pagerank`. Rejected due to heavy payload sizes exceeding performance constraints.

### 2. PySpark Data Processing Path
- **Decision**: Introduce a highly targeted PySpark filter function in `TransferAnalyzer` named `get_top_transfers(club_name, top_n=10)`. The method will filter the parsed RDD where `club_name` is either the buyer or the seller, extract `Player Name`, `Fee`, and `Counterparty Club`, sort descending by fee, and return the top N.
- **Rationale**: Keeps data fetching bounded directly to the source of truth RDD without iterating arrays in the FastAPI layer, fully adhering to PySpark execution principles (Constitution Principle I & II).
- **Alternatives considered**: Using Pandas for individual club parsing out of a locally saved CSV chunk. Rejected because it violates the distributed MapReduce architecture outlined in the Constitution.
