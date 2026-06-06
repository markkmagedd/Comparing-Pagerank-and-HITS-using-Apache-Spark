# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

The feature introduces a toggleable Compare mode to the web interface. This mode splits the visualization into two side-by-side bar charts displaying PageRank outputs on the left and HITS outputs on the right. Both visualizations are driven by the same data filters (season, league, weights, etc). This will be orchestrated on the frontend using simultaneous API calls using `Promise.all` to the robust existing PySpark backend. Node overlaps between algorithms' top-N results will be highlighted visually along with a dynamic summary label to help compare outputs deterministically.

## Technical Context

**Language/Version**: Python 3.12 (Backend), Vanilla JavaScript/HTML/CSS (Frontend)
**Primary Dependencies**: PySpark, FastAPI, Chart.js
**Testing**: pytest
**Target Platform**: Linux server/local development
**Project Type**: Web application
**Performance Goals**: Frontend rendering two synchronous bar charts without blocking main thread, leveraging simultaneous FastApi backings to cached PySpark RDDs.
**Scale/Scope**: ~5,000 transfers graph; Dual rendering for top-N analysis (default ≤ 20 bars each).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. PySpark Scalability First**: PASS - Compare mode utilizes the existing Spark-powered backend, reusing distributed graph logic without pulling processing into single-node bottlenecks.
- **II. Function Modularity**: PASS - Frontend orchestration will rely on decoupling rendering functions to support isolated canvas targets.
- **III. Safe App Initialization**: PASS - Doesn't affect existing backend init.
- **IV. Robust Data Parsing**: PASS - Doesn't affect existing edge RDD ingestion schema.
- **V. Deterministic Output**: PASS - Charts correctly decouple deterministic algorithm outputs in independent side-by-side elements, highlighted precisely.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
src/
├── static/
│   ├── css/
│   │   ├── style.css     # UI container, flex layouts for side-by-side panels
│   │   └── controls.css  # Button styling overrides for compare toggle
│   └── js/
│       └── graph.js      # Core logic extension: handling Promise.all calls and 2x canvas renders
├── templates/
│   └── index.html        # DOM changes for two `<canvas>` and overlap summary div
└── tests/
    └── integration/
        └── test_frontend.py # Potentially ignored given purely JS nature, rely on existing API Pytests
```

**Structure Decision**: A monolithic web application layout modified primarily in the `static/` asset structures, reusing the backend identically.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
