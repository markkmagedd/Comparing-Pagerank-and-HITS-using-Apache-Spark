<!--
Sync Impact Report:

Version change: [CONSTITUTION_VERSION] → 1.0.0

List of modified principles:
- [PRINCIPLE_1_NAME] → I. PySpark Scalability First
- [PRINCIPLE_2_NAME] → II. Function Modularity and Single Responsibility
- [PRINCIPLE_3_NAME] → III. Safe App Initialization
- [PRINCIPLE_4_NAME] → IV. Robust Data Parsing
- [PRINCIPLE_5_NAME] → V. Deterministic Output Artifacts

Added sections:
- Architecture Constraints (Replacing [SECTION_2_NAME])
- Development Workflow (Replacing [SECTION_3_NAME])

Removed sections:
- None

Templates requiring updates:
- ✅ `.specify/templates/plan-template.md` (verified, generic checks align with principles)
- ✅ `.specify/templates/spec-template.md` (verified, no specific hardcoded rules needed)
- ✅ `.specify/templates/tasks-template.md` (verified, generic structure alignments match)
- ✅ `.agent/commands/*.md` (verified, no outdated agent-specific names remain)

Follow-up TODOs:
- Create a `README.md` and link this constitution.
-->
# Comparing-Pagerank-and-HITS-using-Apache-Spark Constitution

## Core Principles

### I. PySpark Scalability First
Use Apache Spark (via PySpark) for scalable preprocessing and graph algorithm computations on large datasets. All intensive computations MUST leverage RDDs/DataFrames to ensure horizontal scalability instead of running purely in-memory on a single node.

### II. Function Modularity and Single Responsibility
Scripts MUST be divided into logical, single-purpose functions (e.g., `plot_top_ranks`, `compute_contributions`, `run_pagerank`). Avoid massive monolithic execution blocks. Functions should include docstrings where complexity warrants.

### III. Safe App Initialization
Spark applications MUST initialize the `SparkSession` safely within the `if __name__ == "__main__":` block to prevent unintended executions and cluster connections when imported as a module for testing.

### IV. Robust Data Parsing
Data parsing MUST gracefully handle missing or unexpected values instead of crashing (e.g., applying nominal weights when valid floats cannot be parsed). CSV or data extraction should use robust module methods like `csv.reader` to correctly process lines including escaped characters.

### V. Deterministic Output Artifacts
Data visualization outputs MUST be saved deterministically into defined artifact files (e.g., `top_attractors.png`, `top_suppliers.png`) ensuring automated reproducibility. Scripts should not block execution waiting for user interaction on plots.

## Architecture Constraints

The project primarily relies on PySpark and Python 3.12 for graph algorithms and MapReduce architecture. No external heavy libraries beyond Pandas, Matplotlib, and CSV for localized output formatting and charting. The `transfers.csv` pipeline is the source of truth for graph topologies, and all algorithm implementations must support MapReduce schemas.

## Development Workflow

Feature proposals MUST clarify how they leverage the Spark distributed architecture. Testing should involve localized standalone tests with truncated datasets or small RDD examples before full Spark job execution. Output artifacts (like processed images) should be reproducible and not checked into version control without justification.

## Governance

All code changes must be reviewed and tested locally on a minimal dataset via PySpark submission. Changes to PageRank iterations, damping metrics, or HITS methodologies MUST include validation showing algorithmic convergence. Architectural complexity in the graph modeling must be explicitly justified against processing requirements.

**Version**: 1.0.0 | **Ratified**: 2026-03-19 | **Last Amended**: 2026-03-19
