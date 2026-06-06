# Bachelors Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-31

## Active Technologies
- Python 3.12 (backend), Vanilla JS (frontend) + FastAPI, PySpark (local mode, `local[1]`), Pydantic v2, Cytoscape.js, Chart.js + DataLabels plugin (002-data-driven-customization)
- N/A — stateless; `transfers.csv` (532 KB) is the sole data source, read at startup (002-data-driven-customization)
- Python 3.12 (backend), Vanilla JS (frontend) + FastAPI, PySpark (local mode, `local[1]`), Pydantic v2, Cytoscape.js, Chart.js + DataLabels plugin (003-hits-algorithm)
- Python 3.12, Vanilla JavaScript (ES6+) + PySpark 4.1, FastAPI, Chart.js, Cytoscape.js (existing) (004-compare-mode)
- N/A (stateless, CSV file as source) (004-compare-mode)
- Python 3.12 (Backend), Vanilla JavaScript/HTML/CSS (Frontend) + PySpark, FastAPI, Chart.js (004-compare-mode)
- Python 3.12 (Backend), Javascript (Frontend) + FastAPI (Routing), PySpark (DataFrame filtering), Chart.js (Visualization) (005-season-filter)
- N/A (Relies on data/transfers.csv) (005-season-filter)

- Python 3.12 (Backend via FastAPI), HTML/JS (Frontend via Cytoscape) + FastAPI, Uvicorn, PySpark, Cytoscape.js (001-pagerank-web-visualization)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12 (Backend via FastAPI), HTML/JS (Frontend via Cytoscape): Follow standard conventions

## Recent Changes
- 005-season-filter: Added Python 3.12 (Backend), Javascript (Frontend) + FastAPI (Routing), PySpark (DataFrame filtering), Chart.js (Visualization)
- 004-compare-mode: Added Python 3.12 (Backend), Vanilla JavaScript/HTML/CSS (Frontend) + PySpark, FastAPI, Chart.js
- 004-compare-mode: Added Python 3.12, Vanilla JavaScript (ES6+) + PySpark 4.1, FastAPI, Chart.js, Cytoscape.js (existing)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
