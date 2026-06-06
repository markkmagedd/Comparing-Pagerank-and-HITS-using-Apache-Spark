# Tasks: League Flow Sankey Visualization

- [ ] T021 Update `TransferAnalyzer` in `src/core/processing.py` to store the filtered RDD of columns for multi-purpose analysis.
- [ ] T022 Implement `get_league_flow()` in `TransferAnalyzer` to aggregate transfers by league.
- [ ] T023 Add `/api/league-flow` endpoint to `src/app.py`.
- [ ] T024 Add `chartjs-chart-sankey` script to `src/templates/index.html`.
- [ ] T025 Add "League Flow" button to the visualization toggle in `src/templates/index.html`.
- [ ] T026 Implement `renderSankey()` in `src/static/js/graph.js` and update `switchVisualization` and `triggerAnalysis` logic to handle the new view.
- [ ] T027 Add CSS styling for the Sankey container (large height, flex layout).
- [ ] T028 Final verification of league flows (e.g., Eredivisie to Premier League).
