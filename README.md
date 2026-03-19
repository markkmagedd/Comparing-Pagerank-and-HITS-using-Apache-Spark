# PageRank Transfer Visualizer

An interactive web-based dashboard to visualize PageRank rankings of transfer data (buyers vs. sellers) using FastAPI and Apache Spark.

## Features
- **Dynamic Calculation**: Run PageRank with custom iterations and damping factors.
- **Top N Filtering**: Visualize only the most significant nodes and their internal relationships.
- **Buyer/Seller Views**: Switch logic to see which clubs are the most dominant attractors (buyers) or suppliers (sellers).
- **Interactive Graph**: Powered by Cytoscape.js with node/edge details on interaction.
- **Spark Integration**: Utilizes PySpark for the heavy lifting of rank computation.

## Prerequisites
- **Python 3.12+**
- **Java 17+** (Designed for Java 25 compatibility using JVM flag workarounds)
- **Apache Spark** (pyspark 4.1.1+)

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Dataset**:
   Place `transfers.csv` in the root directory.

## Running the Application

Start the FastAPI server using Uvicorn:
```bash
PYTHONPATH=. /Users/mark/miniconda3/bin/python -m uvicorn src.app:app --host 0.0.0.0 --port 8000
```

Access the dashboard at `http://localhost:8000`.

## Testing

Run the test suite:
```bash
PYTHONPATH=. pytest tests/
```

## Troubleshooting (Java 25+)
If you encounter `UnsupportedOperationException: getSubject is not supported` on newer JVMs (like Java 25), this application includes:
1. `SparkSession` configuration using `--add-opens` for critical `java.base` and `javax.security.auth` packages.
2. A Python-based CSV loader bypass in `TransferAnalyzer` to avoid Hadoop's internal `FileSystem` initialization that triggers the bug on small datasets.
