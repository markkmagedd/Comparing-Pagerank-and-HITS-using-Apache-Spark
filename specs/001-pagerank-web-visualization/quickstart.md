# Quickstart: PageRank Visualizer

## Prerequisites
1. Ensure Python 3.12+ is installed globally or in your current environment.
2. Java 8 or 11+ must be installed locally since PySpark requires it to compile scala code and run the JVM backend.

## Installation
First, prepare a clean Python environment for the standalone application:
```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pyspark jinja2
```

## Running the Web Visualization
Since PySpark has JVM startup overhead, the service launches the Spark session once globally when Uvicorn starts the FastAPI backend.
```bash
uvicorn src.app:app --reload
```

Then, navigate to the web application index manually:
`http://127.0.0.1:8000`

Use the web control panel to query new graph visualizations. It processes the dataset natively in the backend and serves JSON payload responses readable globally by the Cytoscape JS framework running seamlessly in your browser.
