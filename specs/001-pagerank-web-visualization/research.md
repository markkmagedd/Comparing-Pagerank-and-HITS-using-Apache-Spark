# Research & Technical Decisions: PageRank Web Visualization

## Clarified Technical Context

Based on the feature context and the core PySpark pipeline:
- **Backend Framework**: Python (FastAPI). Decision: FastAPI provides an extremely fast, lightweight way to serve REST API endpoints to a client, which is ideal for a single-page visualization architecture.
- **Frontend Framework**: Vanilla HTML/JS with **Cytoscape.js** for network rendering. Decision: Cytoscape.js is explicitly optimized for rendering and interacting with graph (node-link) networks, and performs much better than generic libraries (like Chart.js) or highly complex manual DOM manipulation (like D3.js) for quick node/edge visualizations.
- **PySpark Integration**: The web backend will initialize a `SparkSession` globally upon app startup, minimizing the overhead of starting the Spark JVM context for every user request.
- **Data Bounds**: The graph limit (Top N) will be handled in the PySpark map/reduce step. The backend will package the top nodes and the directed edges directly connecting them, sending a JSON payload to the frontend.

## Decisions

### 1. Web Framework
**Decision**: FastAPI (Python)
**Rationale**: Python is strictly required because the existing data pipeline `pagerank.py` is written in PySpark. FastAPI is simple, modern, allows background tasks, and natively supports providing JSON APIs to frontends.
**Alternatives considered**: Flask (older, lacks native ASGI/async out of the box), Django (overkill for a single analysis web page).

### 2. Frontend Web Graph Logic
**Decision**: Pure HTML/CSS/JS + Cytoscape.js
**Rationale**: Keeps the architecture simple (no Node.js/React compilation overhead required) fitting the "Bachelors Project" constraints defined implicitly by context. Cytoscape.js handles network physics, dragging, zooming, and node mapping natively.
**Alternatives considered**: D3.js (complex learning curve), React + ReactFlow (requires heavy build tools), Sigma.js (good but more complex to integrate than Cytoscape).

### 3. PySpark Execution Interface
**Decision**: Import modularized `run_pagerank` and share a long-lived `SparkSession`.
**Rationale**: The constitution principle "Safe App Initialization" enforces module safety. Rather than executing `.py` as a subprocess, FastAPI will import the functions and share a single `SparkSession` created at ASGI app startup.
**Alternatives considered**: Spawning a subprocess via `os.system()` (high latency and resource overhead due to JVM startup on every click).

### 4. Bar Chart Rendering Library (FR-009)
**Decision**: Chart.js 4.x (CDN-loaded, Vanilla JS)
**Rationale**: FR-009 requires an interactive bar chart where clicking a bar fires the same data overlay as a node tap in the network graph. Chart.js exposes a direct `onClick` event callback that receives the bar's dataset index, enabling instant look-up of the node payload already cached in memory from the last API response — no re-fetch required. Loaded from CDN (same delivery pattern as Cytoscape.js), zero build tooling, renders onto `<canvas>` consistent with the existing Cytoscape canvas approach.
**Alternatives considered**: Plotly.js (larger bundle size, primarily Python-first API design), D3.js (requires extensive custom layout code for a straightforward bar chart), raw SVG (too low-level and verbose for time-constrained project scope).
