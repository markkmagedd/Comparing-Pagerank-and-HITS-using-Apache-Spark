# Quickstart: Transfer Details Pop-up

1. Backend: Implement the `get_top_transfers()` method inside `src/core/processing.py` to filter the PySpark RDD.
2. Backend: Add the `/api/transfers/{club_name}` REST endpoint in `src/app.py`.
3. Frontend UI: Create the HTML structure for the popup in `src/templates/index.html` (starts with `display: none;`).
4. Frontend Logic: In `src/static/js/graph.js`, bind a `click` event listener to nodes/bars.
5. Integration: On click, set UI to loading state, query the new endpoint, map the JSON array to HTML list items, and show the pop-up container.
