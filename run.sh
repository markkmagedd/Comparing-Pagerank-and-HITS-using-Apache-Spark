#!/bin/bash
cd "$(dirname "$0")"
PYTHONPATH=. PYSPARK_PYTHON=/Users/mark/miniconda3/bin/python PYSPARK_DRIVER_PYTHON=/Users/mark/miniconda3/bin/python \
  /Users/mark/miniconda3/bin/python -m uvicorn src.app:app --host 0.0.0.0 --port 8000
